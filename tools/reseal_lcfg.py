#!/usr/bin/env python3
"""Validate and reseal an XGO/SF2000-family LCFG bisrv.asd image.

This tool does not flash hardware. It only updates the two confirmed LCFG
integrity fields in an output copy:

  0x184  uint32 little-endian payload size (file size - 0x200)
  0x18c  uint32 little-endian CRC-32/MPEG-2 of bytes 0x200..EOF

Usage:
    python reseal_lcfg.py input.asd output.asd

The input is never modified in place.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

HEADER_SIZE = 0x200
SIZE_OFFSET = 0x184
CRC_OFFSET = 0x18C
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


def read_u32_le(buf: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", buf, offset)[0]


def reseal(data: bytes) -> tuple[bytes, dict[str, int | bool]]:
    if len(data) < HEADER_SIZE:
        raise ValueError("image is smaller than the 0x200-byte LCFG header")
    if data[:4] != b"LCFG":
        raise ValueError("input does not begin with LCFG magic")

    output = bytearray(data)
    payload = data[HEADER_SIZE:]
    payload_size = len(payload)
    payload_crc = crc32_mpeg2(payload)

    old_size = read_u32_le(data, SIZE_OFFSET)
    old_crc = read_u32_le(data, CRC_OFFSET)

    struct.pack_into("<I", output, SIZE_OFFSET, payload_size)
    struct.pack_into("<I", output, CRC_OFFSET, payload_crc)

    return bytes(output), {
        "old_size": old_size,
        "new_size": payload_size,
        "old_crc": old_crc,
        "new_crc": payload_crc,
        "size_already_valid": old_size == payload_size,
        "crc_already_valid": old_crc == payload_crc,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    if args.input.resolve() == args.output.resolve():
        parser.error("refusing to modify the input in place")

    original = args.input.read_bytes()
    sealed, info = reseal(original)
    args.output.write_bytes(sealed)

    print(f"payload size: 0x{info['new_size']:08x} ({info['new_size']} bytes)")
    print(f"payload CRC : 0x{info['new_crc']:08x} (CRC-32/MPEG-2)")
    print(f"input size field valid: {info['size_already_valid']}")
    print(f"input CRC field valid : {info['crc_already_valid']}")
    print(f"wrote: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
