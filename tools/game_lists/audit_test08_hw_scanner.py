#!/usr/bin/env python3
"""Audit the exact HW-passed Test08 scanner blob without modifying firmware.

Repository-first recovery tool. It imports the hash-pinned SCANNER_ZB64 from the
canonical Test08 reproducer, verifies length/SHA, and reports direct references
to the frontend count-cache region plus selected stock ABI/table addresses.

This exists so later selective workers are derived from the actual HW-passed
binary rather than from narrative notes.
"""
from __future__ import annotations
import ast, base64, hashlib, struct, zlib
from pathlib import Path

EXPECTED_SHA = "a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d"
EXPECTED_LEN = 3601
BASE = 0x807DAB98

def load_blob(builder: Path) -> bytes:
    tree = ast.parse(builder.read_text(encoding="utf-8"))
    vals = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in {"SCANNER_ZB64", "SCANNER_SHA", "SCANNER_LEN"}:
                vals[name] = ast.literal_eval(node.value)
    assert vals["SCANNER_SHA"] == EXPECTED_SHA
    assert vals["SCANNER_LEN"] == EXPECTED_LEN
    blob = zlib.decompress(base64.b64decode(vals["SCANNER_ZB64"]))
    assert len(blob) == EXPECTED_LEN
    assert hashlib.sha256(blob).hexdigest() == EXPECTED_SHA
    return blob

def words(blob: bytes):
    for off in range(0, len(blob) - 3, 4):
        yield off, struct.unpack_from("<I", blob, off)[0]

def main():
    here = Path(__file__).resolve().parent
    src = here / "build_test08_all_console_scanner_candidate.py"
    blob = load_blob(src)
    print(f"Test08 scanner: {len(blob)} bytes sha256={hashlib.sha256(blob).hexdigest()}")
    # MIPS absolute addresses are normally synthesized by LUI + signed ADDIU,
    # so also report literal high halves and nearby instruction words.
    targets = {
        "resource_table": 0x80A3C32C,
        "count_base": 0x80D2894C,
        "dir_open": 0x807D40C4,
        "dir_next": 0x807D4124,
        "dir_close": 0x807D41F4,
        "ext_classify": 0x80360A08,
    }
    for name, addr in targets.items():
        hi = ((addr + 0x8000) >> 16) & 0xFFFF
        lo = addr & 0xFFFF
        hits = []
        for off, w in words(blob):
            if (w & 0xFFFF) in {hi, lo}:
                hits.append((off, w))
        print(f"\n{name} {addr:#010x} hi={hi:#06x} lo={lo:#06x}")
        for off, w in hits[:32]:
            start=max(0,off-12); end=min(len(blob),off+16)
            ws=[f"{x:08x}" for _,x in words(blob[start:end])]
            print(f"  {BASE+off:#010x} off={off:#05x} word={w:08x} context={' '.join(ws)}")

    # Directly decode the common LUI rt,hi ; ADDIU rt,rt,lo construction and
    # enumerate all absolute addresses in the count-cache neighborhood.
    print("\nDecoded absolute references in 0x80D28900..0x80D289FF:")
    found=[]
    for off in range(0,len(blob)-8,4):
        w1=struct.unpack_from("<I",blob,off)[0]; w2=struct.unpack_from("<I",blob,off+4)[0]
        if (w1>>26)==15 and (w2>>26)==9:
            rt=(w1>>16)&31
            if ((w2>>21)&31)==rt and ((w2>>16)&31)==rt:
                hi=w1&0xffff; lo=w2&0xffff
                slo=lo-0x10000 if lo&0x8000 else lo
                addr=((hi<<16)+slo)&0xffffffff
                if 0x80D28900 <= addr <= 0x80D289FF:
                    found.append((BASE+off,addr,w1,w2))
    for pc,addr,w1,w2 in found:
        print(f"  pc={pc:#010x} -> {addr:#010x} ({w1:08x} {w2:08x})")
    if not found:
        print("  no direct LUI/ADDIU reference; address is computed dynamically")
if __name__ == "__main__":
    main()
