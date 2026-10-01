#!/usr/bin/env python3
"""Build mechanically-specialized Arcade catalog Stage2 engines from Test106.

Input must be the exact HW-proven Test106 MD/catalog-safe.xgc:
SHA-256 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

This builder deliberately patches only fields enumerated in PATCH_SPECS.
It refuses a source whose hash/size or expected source bytes differ.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct

SOURCE_SHA = "45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c"
SOURCE_SIZE = 7000

@dataclass(frozen=True)
class Family:
    name: str
    scan_root: str
    live: tuple[str, str, str]
    backup: tuple[str, str, str]

FAMILIES = (
    Family("cps1", "/mnt/sda1/ARCADE/CPS1/.catalog",
           ("/mnt/sda1/Resources/mswb7.tax","/mnt/sda1/Resources/msdtc.nec","/mnt/sda1/Resources/mfpmp.bvs"),
           ("/mnt/sda1/ARCADE/CPS1/.tax.bak","/mnt/sda1/ARCADE/CPS1/.nec.bak","/mnt/sda1/ARCADE/CPS1/.bvs.bak")),
    Family("cps2", "/mnt/sda1/ARCADE/CPS2/.catalog",
           ("/mnt/sda1/Resources/kjbyr.tax","/mnt/sda1/Resources/djoin.nec","/mnt/sda1/Resources/ke89a.bvs"),
           ("/mnt/sda1/ARCADE/CPS2/.tax.bak","/mnt/sda1/ARCADE/CPS2/.nec.bak","/mnt/sda1/ARCADE/CPS2/.bvs.bak")),
    Family("igs", "/mnt/sda1/ARCADE/IGS/.catalog",
           ("/mnt/sda1/Resources/subst.tax","/mnt/sda1/Resources/aepic.nec","/mnt/sda1/Resources/sensc.bvs"),
           ("/mnt/sda1/ARCADE/IGS/.tax.bak","/mnt/sda1/ARCADE/IGS/.nec.bak","/mnt/sda1/ARCADE/IGS/.bvs.bak")),
    Family("neogeo", "/mnt/sda1/ARCADE/NEOGEO/.catalog",
           ("/mnt/sda1/Resources/rmapi.tax","/mnt/sda1/Resources/pcadm.nec","/mnt/sda1/Resources/ntdll.bvs"),
           ("/mnt/sda1/ARCADE/NEOGEO/.tax.bak","/mnt/sda1/ARCADE/NEOGEO/.nec.bak","/mnt/sda1/ARCADE/NEOGEO/.bvs.bak")),
)

# Exact offsets are populated only after direct binary literal audit.
# Keeping them explicit prevents accidental global string replacement.
PATCH_SPECS: dict[str, tuple[int, bytes]] = {
    "suffix_m": (0x0444, b"\x6d"),
    "suffix_d": (0x0470, b"\x64"),
}

CACHE_WRITE_OFF = 0x1A44
CACHE_WRITE_EXPECTED = bytes.fromhex("d280013c5c892134000020ac")
NOP3 = b"\x00" * 12

def digest(b: bytes) -> str:
    return sha256(b).hexdigest()

def patch_expected(buf: bytearray, off: int, expected: bytes, replacement: bytes) -> None:
    actual = bytes(buf[off:off+len(expected)])
    if actual != expected:
        raise ValueError(f"source mismatch at 0x{off:X}: {actual.hex()} != {expected.hex()}")
    if len(replacement) != len(expected):
        raise ValueError("replacement must preserve binary geometry")
    buf[off:off+len(expected)] = replacement

def load_source(path: Path) -> bytes:
    b = path.read_bytes()
    if len(b) != SOURCE_SIZE or digest(b) != SOURCE_SHA:
        raise ValueError("not the exact HW-proven Test106 Stage2")
    return b

def specialize_suffix_and_cache(source: bytes) -> bytearray:
    out = bytearray(source)
    # MIPS immediates are 32-bit instructions; the character byte is the low
    # immediate byte at these audited locations.
    patch_expected(out, 0x0444, b"\x6d", b"\x66")  # m -> f
    patch_expected(out, 0x0470, b"\x64", b"\x62")  # d -> b
    patch_expected(out, CACHE_WRITE_OFF, CACHE_WRITE_EXPECTED, NOP3)
    return out

def main() -> None:
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("test106_stage2", type=Path)
    ap.add_argument("out_dir", type=Path)
    a=ap.parse_args()
    src=load_source(a.test106_stage2)
    a.out_dir.mkdir(parents=True, exist_ok=True)
    for fam in FAMILIES:
        # Literal-slot patching is intentionally gated until exact source
        # offsets/capacities are mechanically audited from the binary.
        out=specialize_suffix_and_cache(src)
        p=a.out_dir/f"catalog-{fam.name}.xgc.partial"
        p.write_bytes(out)
        print(f"{fam.name}: PARTIAL {len(out)} {digest(out)}")
    print("PARTIAL only: family path literals are not yet patched.")

if __name__ == "__main__":
    main()
