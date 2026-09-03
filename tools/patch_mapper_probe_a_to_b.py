#!/usr/bin/env python3
"""Build the first functional XGO on-device mapper probe.

The probe makes three strict instruction edits to the exact preserved stock
XGO bisrv.asd:

1. expose hidden pause-menu page 4 (gpapi.bvs),
2. turn the state-3/state-4 split into a branch-likely that redirects only
   state 4 to the existing keymap writer,
3. use that taken branch's delay slot to set the active Player-1 physical A
   record to logical B (0x00000000).

Because the existing writer mirrors P1 to the corresponding P2 record,
recompiles the map with set_keymap(), and writes the per-ROM .kmp only when it
sees a P1/P2 mismatch, the single P1 write deliberately triggers the complete
stock persistence chain.

Expected hardware behavior:
- Select+Start -> hidden fifth mapper screen is reachable.
- Confirm on page 4 -> physical A becomes logical B, mapping is persisted,
  and the normal resume path is used.
- Stock page-3 behavior is preserved because MIPS branch-likely nullifies the
  patched delay slot when the branch is not taken.

This is intentionally NOT a full mapper UI. It is an end-to-end hook proof.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

STOCK_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
HEADER_SIZE = 0x200
CRC_OFFSET = 0x18C
STOCK_PAYLOAD_CRC = 0x5EE51F11
POLY = 0x04C11DB7

PATCHES = {
    # slti s0,v1,3 -> slti s0,v1,4
    0x00354EC0: (0x28700003, 0x28700004),

    # bne v1,t7,0x80354df4
    # -> bnel v1,t7,0x80355808
    # State 3 falls through with its delay slot annulled; state 4 branches to
    # the existing state-0 writer/resume path.
    0x0035519C: (0x146FFF15, 0x546F019A),

    # Old branch delay slot: lhu a0,-30364(gp)
    # New taken-only delay slot: sw zero,0x1908(s2)
    # s2 == 0x8109f65c in this pause function;
    # 0x8109f65c + 0x1908 == 0x810a0f64
    # 0x810a0f64 == active map base 0x810a0f58 + record 3*4
    # record 3 is ordinary-system physical A; zero encodes logical B.
    0x003551A0: (0x97848964, 0xAE401908),
}


def crc32_mpeg2(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ POLY) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
    return crc


def u32(buf: bytes | bytearray, off: int) -> int:
    return struct.unpack_from("<I", buf, off)[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()

    if args.input.resolve() == args.output.resolve():
        ap.error("refusing to modify input in place")

    original = args.input.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    if sha != STOCK_SHA256:
        raise SystemExit(f"refusing unknown firmware: SHA-256 {sha}")
    if original[:4] != b"LCFG":
        raise SystemExit("refusing image without LCFG magic")
    if u32(original, CRC_OFFSET) != STOCK_PAYLOAD_CRC:
        raise SystemExit("unexpected stock LCFG CRC field")
    if crc32_mpeg2(original[HEADER_SIZE:]) != STOCK_PAYLOAD_CRC:
        raise SystemExit("stock payload CRC does not validate")

    patched = bytearray(original)
    for off, (old, new) in PATCHES.items():
        got = u32(original, off)
        if got != old:
            raise SystemExit(
                f"unexpected instruction at 0x{off:08x}: "
                f"0x{got:08x}, expected 0x{old:08x}"
            )
        struct.pack_into("<I", patched, off, new)

    new_crc = crc32_mpeg2(patched[HEADER_SIZE:])
    struct.pack_into("<I", patched, CRC_OFFSET, new_crc)

    allowed = set(range(CRC_OFFSET, CRC_OFFSET + 4))
    for off in PATCHES:
        allowed.update(range(off, off + 4))
    changed = {i for i, (a, b) in enumerate(zip(original, patched)) if a != b}
    if not changed.issubset(allowed):
        raise SystemExit("internal error: unexpected bytes changed")

    args.output.write_bytes(patched)
    print(f"input SHA-256 : {sha}")
    for off, (old, new) in PATCHES.items():
        print(f"0x{off:08x}: 0x{old:08x} -> 0x{new:08x}")
    print(f"payload CRC   : 0x{STOCK_PAYLOAD_CRC:08x} -> 0x{new_crc:08x}")
    print(f"output SHA-256: {hashlib.sha256(patched).hexdigest()}")
    print(f"wrote          : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
