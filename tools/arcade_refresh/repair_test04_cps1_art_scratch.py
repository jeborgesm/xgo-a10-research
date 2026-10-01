#!/usr/bin/env python3
"""Apply the minimal Test04 CPS1 artwork scratch-path repair.

Input must be the exact HW-observed Test04 CPS1 materializer.  This tool does
not build or package firmware and does not alter the JPEG worker or Arcade
finalizer.
"""
from __future__ import annotations
import hashlib
import pathlib
import sys

PARENT_SIZE = 0x101F08
PARENT_SHA256 = "301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28"
TAIL_SHA256 = "9ca2599d45d5c7cadb4f89064d959f5959fc1de258c4384545353bc796fec136"

PATCHES = (
    (0x1234, b"/mnt/sda1/ARCADE/CPS1/art/.xgo.jpg\0",
             b"/mnt/sda1/ARCADE/.xgo.jpg\0"),
    (0x1258, b"/mnt/sda1/ARCADE/CPS1/art/.xgo.rgb565\0",
             b"/mnt/sda1/ARCADE/.xgo.rgb565\0"),
)

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: repair_test04_cps1_art_scratch.py TEST04_REFRESH.XGC OUT.XGC")
    src = pathlib.Path(sys.argv[1]).read_bytes()
    if len(src) != PARENT_SIZE or sha256(src) != PARENT_SHA256:
        raise SystemExit("refusing non-Test04 parent")
    if sha256(src[0x100000:0x101F08]) != TAIL_SHA256:
        raise SystemExit("golden JPEG tail mismatch")

    out = bytearray(src)
    allowed = set()
    for off, old, new in PATCHES:
        if bytes(out[off:off+len(old)]) != old:
            raise SystemExit(f"expected literal missing at 0x{off:X}")
        if len(new) > len(old):
            raise SystemExit("replacement exceeds proven literal slot")
        repl = new + b"\0" * (len(old) - len(new))
        out[off:off+len(old)] = repl
        allowed.update(range(off, off+len(old)))

    changed = {i for i,(a,b) in enumerate(zip(src,out)) if a != b}
    if not changed <= allowed:
        raise SystemExit("unexpected delta outside literal slots")
    if sha256(out[0x100000:0x101F08]) != TAIL_SHA256:
        raise SystemExit("JPEG tail changed")

    pathlib.Path(sys.argv[2]).write_bytes(out)
    print("size", len(out))
    print("sha256", sha256(out))
    print("changed_bytes", len(changed))
    print("decoder_tail_sha256", sha256(out[0x100000:0x101F08]))

if __name__ == "__main__":
    main()
