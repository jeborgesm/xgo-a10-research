#!/usr/bin/env python3
"""Repair the exact Test132 GB materializer's two-character .gb suffix geometry.

Input must be the exact helper recovered from the tested SD.
Only one MIPS instruction changes:
  +0x009C: ori s4,s7,0x0005 -> ori s4,s7,0x0006

The filename begins at 0x87600008 and v0 is filename_length-1 at the predicate.
The change moves the first dot test from filename[length-4] to
filename[length-3]. Existing later case-folded 'g' and 'b' tests remain unchanged.
"""
from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

INPUT_SHA="00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810"
OUTPUT_SHA="082c17e8a31cfae474aef4e401906be5fd7c05271a2eade5b6cf6e1ce2a09119"
SIZE=0x101F08
OFF=0x009C
OLD=0x36F40005
NEW=0x36F40006

def sha(b): return hashlib.sha256(b).hexdigest()

def accepts(name: bytes) -> bool:
    # Static semantic model of the relevant Test132 predicate after the patch.
    if len(name) < 3:
        return False
    return name[-3:-2] == b"." and name[-2:-1].lower() == b"g" and name[-1:].lower() == b"b"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("output",type=Path)
    a=ap.parse_args()
    src=a.input.read_bytes()
    if len(src)!=SIZE or sha(src)!=INPUT_SHA:
        raise SystemExit("FAIL: input is not exact Test132 GB/refresh.xgc")
    out=bytearray(src)
    if struct.unpack_from("<I",out,OFF)[0]!=OLD:
        raise SystemExit("FAIL: predicate instruction mismatch")
    struct.pack_into("<I",out,OFF,NEW)

    diffs=[i for i,(x,y) in enumerate(zip(src,out)) if x!=y]
    if diffs != [OFF]:
        raise SystemExit(f"FAIL: unexpected changed bytes {diffs}")
    if sha(out)!=OUTPUT_SHA:
        raise SystemExit("FAIL: output SHA mismatch")

    tests={
        b"Tetris.gb":True,b"Tetris.GB":True,b"foo.gbc":False,
        b"foo.gba":False,b"foo.sfc":False,b"foo":False,b".gb":True,
    }
    for n,want in tests.items():
        got=accepts(n)
        if got!=want: raise SystemExit(f"FAIL semantic test {n!r}: {got} != {want}")

    a.output.write_bytes(out)
    print("PASS exact Test132 input")
    print("PASS one-byte diff at +0x009C: 05 -> 06")
    print("PASS output SHA",sha(out))

if __name__=="__main__":
    main()
