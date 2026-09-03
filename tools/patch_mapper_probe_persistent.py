#!/usr/bin/env python3
"""Build the persistent XGO hidden-page mapper probe.

This extends the hardware-proven A->B mapper probe with one additional stock
firmware fix: make the keymap writer use the same full ROM-filename buffer as
the loader. Without this fix stock writes e.g. "Game.kmp" while the loader
looks for "Game.zsf.kmp".

Edits, all against the exact preserved stock bisrv.asd:
1. writer name source: 0x8109fc20 -> 0x8109fce8,
2. expose hidden pause-menu page 4 (gpapi.bvs),
3. redirect only page-4 confirm to the stock keymap writer/resume path,
4. in the taken branch-likely delay slot set P1 physical A -> logical B.

Expected hardware result: page-4 confirm changes A->B immediately, writes a
48-byte per-ROM file whose name includes the ROM extension, and the stock
loader restores that mapping on the next launch without manual renaming.
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
EXPECTED_OUTPUT_CRC = 0x3F08B86E
EXPECTED_OUTPUT_SHA256 = "834be40b32027bc6cf2426d9f030c51d1a9a8a0b85ce1b06293564bfa42dee25"

PATCHES = {
    # Writer: addiu a3,a3,-992 (0x8109fc20 display name)
    #      -> addiu a3,a3,-792 (0x8109fce8 full ROM filename)
    0x00354054: (0x24E7FC20, 0x24E7FCE8),

    # slti s0,v1,3 -> slti s0,v1,4: expose hidden page 4.
    0x00354EC0: (0x28700003, 0x28700004),

    # bne v1,t7,0x80354df4 -> bnel v1,t7,0x80355808.
    # State 3 falls through with the delay slot annulled; state 4 takes it.
    0x0035519C: (0x146FFF15, 0x546F019A),

    # Taken-only delay slot: active P1 physical-A record -> logical B (zero).
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

    output_sha = hashlib.sha256(patched).hexdigest()
    if new_crc != EXPECTED_OUTPUT_CRC:
        raise SystemExit(
            f"unexpected generated CRC: 0x{new_crc:08x}, "
            f"expected 0x{EXPECTED_OUTPUT_CRC:08x}"
        )
    if output_sha != EXPECTED_OUTPUT_SHA256:
        raise SystemExit(
            f"unexpected generated SHA-256: {output_sha}, "
            f"expected {EXPECTED_OUTPUT_SHA256}"
        )

    args.output.write_bytes(patched)
    print(f"input SHA-256 : {sha}")
    for off, (old, new) in PATCHES.items():
        print(f"0x{off:08x}: 0x{old:08x} -> 0x{new:08x}")
    print(f"payload CRC   : 0x{STOCK_PAYLOAD_CRC:08x} -> 0x{new_crc:08x}")
    print(f"output SHA-256: {output_sha}")
    print(f"wrote          : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
