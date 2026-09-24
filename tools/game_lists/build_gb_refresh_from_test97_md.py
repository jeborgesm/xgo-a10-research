#!/usr/bin/env python3
"""Derive the GB enrichment materializer from the exact HW-proven Test97 MD helper.

This intentionally does NOT redesign the parser. GB .gb has the same two-letter
source-extension geometry as MD .md, so preserve Test97's HW-proven short-extension
control flow, including the NOP at helper offset 0x027C.

Input is proprietary and is not stored in this repository.
"""

from __future__ import annotations
import argparse, hashlib
from pathlib import Path

SIZE = 1_056_520
TEST97_MD_SHA256 = "c0af2dea8291f86b411e819356e7b6b877ca69e39a444f0780348906f610e087"

# Exact Test97 MD -> GB substitutions.  All replacements are length-preserving.
PATCHES = {
    # generated wrapper constant: little-endian bytes for ".zmd" -> ".zgb"
    0x0114: (bytes.fromhex("6d64"), bytes.fromhex("6762")),
    # source extension checks: .md -> .gb.  The Test97 NOP at 0x027C is preserved.
    0x02A8: (b"m", b"g"),
    0x02D4: (b"d", b"b"),
    # same-length filesystem contract: MD -> GB
    0x0FF2: (b"MD", b"GB"),
    0x100D: (b"MD", b"GB"),
    0x101B: (b"MD", b"GB"),
    0x1036: (b"MD", b"GB"),
    0x1054: (b"MD", b"GB"),
    0x1071: (b"MD", b"GB"),
    0x108A: (b"MD", b"GB"),
}

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="exact Test97 MD/refresh.xgc")
    ap.add_argument("output", type=Path)
    a=ap.parse_args()
    src=a.input.read_bytes()
    assert len(src)==SIZE, (len(src), SIZE)
    assert sha(src)==TEST97_MD_SHA256, sha(src)

    out=bytearray(src)
    for off,(old,new) in PATCHES.items():
        assert len(old)==len(new)
        got=bytes(out[off:off+len(old)])
        assert got==old, (hex(off), got.hex(), old.hex())
        out[off:off+len(old)]=new

    # Critical inherited Test97 short-extension fix: second dot gate remains NOP.
    assert bytes(out[0x027C:0x0280]) == b"\x00\x00\x00\x00"

    # No accidental mutation outside the enumerated substitutions.
    changed={i for i,(x,y) in enumerate(zip(src,out)) if x!=y}
    expected=set()
    for off,(old,new) in PATCHES.items():
        expected.update(off+i for i,(x,y) in enumerate(zip(old,new)) if x!=y)
    assert changed==expected, (sorted(changed), sorted(expected))

    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(out)
    print(f"input  sha256 {sha(src)}")
    print(f"output sha256 {sha(out)}")
    print(f"changed bytes {len(changed)}")
    print("changed offsets", " ".join(hex(x) for x in sorted(changed)))

if __name__=="__main__":
    main()
