#!/usr/bin/env python3
"""Create the minimal XGO hidden mapping-screen visual probe.

This tool patches exactly one instruction in a known-stock XGO bisrv.asd:

    ASD 0x00354ec0 / runtime 0x80354ec0
    slti s0,v1,3  ->  slti s0,v1,4

That expands the stock in-game menu navigation range from indices 0..3 to
0..4. The stock five-entry background table already maps index 4 to
Resources/gpapi.bvs.

The tool is intentionally strict:
- requires the exact preserved stock firmware SHA-256;
- verifies the original instruction word;
- verifies the stock LCFG payload-size and CRC fields;
- never edits the input in place;
- recalculates CRC-32/MPEG-2 after patching;
- verifies that only the instruction and CRC field changed.

This is a VISUAL PROBE only. Static analysis shows that index 4 has no stock
action-dispatch body, so this patch is expected only to expose the dormant
mapping background, not to provide an interactive editor.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

STOCK_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
HEADER_SIZE = 0x200
SIZE_OFFSET = 0x184
CRC_OFFSET = 0x18C
PATCH_OFFSET = 0x00354EC0
STOCK_INSN = 0x28700003
PATCHED_INSN = 0x28700004
STOCK_PAYLOAD_SIZE = 0x00C2D2C4
STOCK_PAYLOAD_CRC = 0x5EE51F11
POLY = 0x04C11DB7


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
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    args = p.parse_args()

    if args.input.resolve() == args.output.resolve():
        p.error("refusing to modify the input in place")

    original = args.input.read_bytes()
    sha = hashlib.sha256(original).hexdigest()
    if sha != STOCK_SHA256:
        raise SystemExit(f"refusing unknown firmware: SHA-256 {sha}")

    if original[:4] != b"LCFG":
        raise SystemExit("refusing image without LCFG magic")
    if u32(original, SIZE_OFFSET) != STOCK_PAYLOAD_SIZE:
        raise SystemExit("unexpected stock LCFG payload-size field")
    if len(original) - HEADER_SIZE != STOCK_PAYLOAD_SIZE:
        raise SystemExit("file length does not match stock LCFG payload size")
    if u32(original, CRC_OFFSET) != STOCK_PAYLOAD_CRC:
        raise SystemExit("unexpected stock LCFG CRC field")
    if crc32_mpeg2(original[HEADER_SIZE:]) != STOCK_PAYLOAD_CRC:
        raise SystemExit("stock LCFG payload CRC does not validate")
    if u32(original, PATCH_OFFSET) != STOCK_INSN:
        raise SystemExit(
            f"unexpected instruction at 0x{PATCH_OFFSET:08x}: "
            f"0x{u32(original, PATCH_OFFSET):08x}"
        )

    patched = bytearray(original)
    struct.pack_into("<I", patched, PATCH_OFFSET, PATCHED_INSN)
    new_crc = crc32_mpeg2(patched[HEADER_SIZE:])
    struct.pack_into("<I", patched, CRC_OFFSET, new_crc)

    changed = [i for i, (a, b) in enumerate(zip(original, patched)) if a != b]
    allowed = set(range(PATCH_OFFSET, PATCH_OFFSET + 4)) | set(range(CRC_OFFSET, CRC_OFFSET + 4))
    if not set(changed).issubset(allowed):
        raise SystemExit("internal error: bytes outside patch/CRC fields changed")

    args.output.write_bytes(patched)

    print(f"input SHA-256 : {sha}")
    print(f"patch offset  : 0x{PATCH_OFFSET:08x}")
    print(f"instruction   : 0x{STOCK_INSN:08x} -> 0x{PATCHED_INSN:08x}")
    print(f"payload CRC   : 0x{STOCK_PAYLOAD_CRC:08x} -> 0x{new_crc:08x}")
    print(f"output SHA-256: {hashlib.sha256(patched).hexdigest()}")
    print(f"wrote          : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
