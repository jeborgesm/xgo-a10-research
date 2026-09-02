#!/usr/bin/env python3
"""Pack a raw MIPS payload into the minimal XGO external-core container."""

from __future__ import annotations

import argparse
import binascii
import struct
from pathlib import Path

MAGIC = b"XGOC"
VERSION = 1
HEADER_SIZE = 32
LOAD_ADDR = 0x87000000
CORE_LIMIT = 0x87CDAE00


def parse_int(value: str) -> int:
    return int(value, 0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("payload", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--load-address", type=parse_int, default=LOAD_ADDR)
    ap.add_argument("--entry-offset", type=parse_int, required=True)
    ap.add_argument("--memory-size", type=parse_int, required=True)
    args = ap.parse_args()

    payload = args.payload.read_bytes()
    payload_size = len(payload)

    if args.load_address != LOAD_ADDR:
        raise SystemExit(f"unsupported load address 0x{args.load_address:08x}")
    if payload_size == 0:
        raise SystemExit("payload is empty")
    if args.entry_offset < 0 or args.entry_offset >= payload_size:
        raise SystemExit("entry offset must point inside the file-backed payload")
    if args.memory_size < payload_size:
        raise SystemExit("memory size is smaller than payload size")
    if args.memory_size > CORE_LIMIT - LOAD_ADDR:
        raise SystemExit("memory image exceeds reserved XGO external-core window")

    crc = binascii.crc32(payload) & 0xFFFFFFFF
    version_header = VERSION | (HEADER_SIZE << 16)

    header = struct.pack(
        "<4s7I",
        MAGIC,
        version_header,
        args.load_address,
        args.entry_offset,
        payload_size,
        args.memory_size,
        crc,
        0,  # flags; version 1 defines no flags
    )
    assert len(header) == HEADER_SIZE

    args.output.write_bytes(header + payload)
    print(f"XGOC: {args.output}")
    print(f"  payload      {payload_size} bytes")
    print(f"  memory       {args.memory_size} bytes")
    print(f"  BSS/runtime  {args.memory_size - payload_size} bytes")
    print(f"  entry        0x{args.load_address + args.entry_offset:08x}")
    print(f"  CRC32        0x{crc:08x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
