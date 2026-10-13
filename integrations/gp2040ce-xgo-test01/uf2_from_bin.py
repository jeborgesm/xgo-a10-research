#!/usr/bin/env python3
"""Convert a linked RP2040 flash .bin to UF2 without picotool post-link conversion.

Input must be a raw flash image beginning at 0x10000000, including boot2.
The 256-byte UF2 payloads use RP2040 family ID 0xE48BFF56.
"""
import argparse
import pathlib
import struct

MAGIC_START0 = 0x0A324655
MAGIC_START1 = 0x9E5D5157
MAGIC_END = 0x0AB16F30
RP2040_FAMILY = 0xE48BFF56
FLASH_BASE = 0x10000000
PAYLOAD_SIZE = 256
BLOCK_SIZE = 512
FLAG_FAMILY_ID = 0x00002000

def convert(raw: bytes) -> bytes:
    if not raw or len(raw) % 4:
        raise ValueError("input must be nonempty and word-aligned")
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError("image exceeds standard 2 MiB RP2040 flash")
    count = (len(raw) + PAYLOAD_SIZE - 1) // PAYLOAD_SIZE
    out = bytearray()
    for index in range(count):
        payload = raw[index * PAYLOAD_SIZE:(index + 1) * PAYLOAD_SIZE]
        header = struct.pack("<8I", MAGIC_START0, MAGIC_START1, FLAG_FAMILY_ID,
                             FLASH_BASE + index * PAYLOAD_SIZE, PAYLOAD_SIZE,
                             index, count, RP2040_FAMILY)
        block = header + payload.ljust(PAYLOAD_SIZE, bytes([0]))
        out.extend(block.ljust(BLOCK_SIZE - 4, bytes([0])) + struct.pack("<I", MAGIC_END))
    return bytes(out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=pathlib.Path)
    ap.add_argument("output", type=pathlib.Path)
    args = ap.parse_args()
    data = args.input.read_bytes()
    result = convert(data)
    args.output.write_bytes(result)
    print(f"RP2040 UF2: {len(data)} image bytes, {len(result)//BLOCK_SIZE} blocks, {args.output}")
