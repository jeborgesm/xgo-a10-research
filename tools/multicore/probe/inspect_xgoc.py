#!/usr/bin/env python3
"""Inspect and validate an XGOC external-core image on the host."""

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


def fail(message: str) -> None:
    raise SystemExit(f"INVALID XGOC: {message}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    args = ap.parse_args()

    data = args.image.read_bytes()
    if len(data) < HEADER_SIZE:
        fail("file is shorter than the 32-byte header")

    header = data[:HEADER_SIZE]
    payload = data[HEADER_SIZE:]
    (
        magic,
        version_header,
        load_addr,
        entry_offset,
        payload_size,
        memory_size,
        payload_crc,
        header_crc,
    ) = struct.unpack("<4s7I", header)

    version = version_header & 0xFFFF
    header_size = version_header >> 16
    calculated_header_crc = binascii.crc32(header[:28]) & 0xFFFFFFFF
    calculated_payload_crc = binascii.crc32(payload) & 0xFFFFFFFF

    if magic != MAGIC:
        fail(f"bad magic {magic!r}")
    if version != VERSION or header_size != HEADER_SIZE:
        fail(f"unsupported version/header pair {version}/{header_size}")
    if header_crc != calculated_header_crc:
        fail("header CRC mismatch")
    if load_addr != LOAD_ADDR:
        fail(f"unsupported load address 0x{load_addr:08x}")
    if payload_size != len(payload):
        fail(f"payload_size={payload_size} but file contains {len(payload)} payload bytes")
    if payload_size == 0:
        fail("empty payload")
    if memory_size < payload_size:
        fail("memory size is smaller than payload size")
    if memory_size > CORE_LIMIT - LOAD_ADDR:
        fail("runtime image exceeds the reserved XGO external-core window")
    if entry_offset >= payload_size:
        fail("entry point is outside file-backed payload")
    if payload_crc != calculated_payload_crc:
        fail("payload CRC mismatch")

    print("VALID XGOC v1")
    print(f"  file          {args.image}")
    print(f"  load          0x{load_addr:08x}")
    print(f"  entry         0x{load_addr + entry_offset:08x}")
    print(f"  payload       {payload_size} bytes")
    print(f"  runtime       {memory_size} bytes")
    print(f"  zero tail     {memory_size - payload_size} bytes")
    print(f"  payload CRC   0x{payload_crc:08x}")
    print(f"  header CRC    0x{header_crc:08x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
