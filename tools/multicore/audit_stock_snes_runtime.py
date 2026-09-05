#!/usr/bin/env python3
"""Verify the exact stock XGO SNES special-case in run_emulator().

The script intentionally requires the preserved stock firmware fingerprint and
checks the small instruction sequence that distinguishes SNES family 0x08 from
the ordinary libretro AV/audio path. It does not modify the firmware.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

STOCK_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"

# ASD offset == runtime - 0x80000000 for this preserved image.
WORDS = {
    0x0035EE00: 0x9788F35C,  # lhu t0,-0xca4(gp) : active family selector
    0x0035EE04: 0x24060008,  # li a2,8
    0x0035EE08: 0x110600FB,  # beq t0,a2,0x8035f1f8
    0x0035F1F8: 0x241F0050,  # li ra,80
    0x0035F1FC: 0x24192B11,  # li t9,11025
    0x0035F200: 0x00002021,  # move a0,zero
    0x0035F204: 0x24052B11,  # li a1,11025
    0x0035F208: 0x24060002,  # li a2,2
    0x0035F20C: 0xAF9F8C9C,  # sw ra,-29540(gp)
    0x0035F210: 0x1000FF10,  # b 0x8035ee54
    0x0035F214: 0xAF998C94,  # sw t9,-29548(gp) (delay slot)
    0x0035EE54: 0x0C0D7266,  # jal 0x8035c998 (stock sound init)
    0x0035EE5C: 0x8F90F328,  # generic region callback resumes here
}

def word(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("firmware", type=Path)
    args = ap.parse_args()

    data = args.firmware.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != STOCK_SHA256:
        raise SystemExit(f"refusing unknown firmware: SHA-256 {sha}")

    for off, expected in WORDS.items():
        got = word(data, off)
        if got != expected:
            raise SystemExit(
                f"mismatch at ASD 0x{off:08x} / runtime 0x{0x80000000+off:08x}: "
                f"got 0x{got:08x}, expected 0x{expected:08x}"
            )

    print("stock XGO SNES run_emulator special-case verified")
    print("family selector  : 0x08")
    print("branch           : 0x8035ee08 -> 0x8035f1f8")
    print("sound init args  : a0=0, a1=11025 Hz, a2=2 channels")
    print("fixed globals    : 0x80c2d410=80, 0x80c2d408=11025")
    print("resume path      : 0x8035ee54 sound init -> 0x8035ee5c region")
    print("AV-info callback : skipped for family 0x08")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
