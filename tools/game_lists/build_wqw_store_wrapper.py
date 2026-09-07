#!/usr/bin/env python3
"""
Build an XGO/SF2000-family Zxx wrapper from:
  - raw RGB565 thumbnail bytes
  - one ROM payload

The wrapper layout proven on XGO is:
  thumbnail prefix
  WQW-obfuscated ZIP archive

This implementation deliberately uses ZIP method 0 (STORE) for the first
hardware proof so the device only has to parse WQW container metadata; no
host-side compressor compatibility is involved.
"""

from __future__ import annotations
import argparse
import binascii
import struct
from pathlib import Path

WQW_LOCAL   = 0x03575157
WQW_CENTRAL = 0x02575157
WQW_END     = 0x01575157
XOR_KEY = 0xE5

def xor_name(name: bytes) -> bytes:
    return bytes(b ^ XOR_KEY for b in name)

def build_wqw_store(payload: bytes, inner_name: str) -> bytes:
    name = inner_name.encode("utf-8")
    enc_name = xor_name(name)
    crc = binascii.crc32(payload) & 0xFFFFFFFF
    size = len(payload)

    # Deterministic DOS timestamp/date = 0 for archaeology reproducibility.
    local = struct.pack(
        "<IHHHHHIIIHH",
        WQW_LOCAL, 20, 0, 0, 0, 0,
        crc, size, size, len(enc_name), 0,
    ) + enc_name + payload

    central_offset = len(local)
    central = struct.pack(
        "<IHHHHHHIIIHHHHHII",
        WQW_CENTRAL,
        20, 20, 0, 0, 0, 0,
        crc, size, size,
        len(enc_name), 0, 0, 0, 0,
        0, 0,
    ) + enc_name

    end = struct.pack(
        "<IHHHHIIH",
        WQW_END,
        0, 0, 1, 1,
        len(central), central_offset, 0,
    )
    return local + central + end

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--thumbnail-rgb565", required=True, type=Path)
    ap.add_argument("--rom", required=True, type=Path)
    ap.add_argument("--inner-name", required=True)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--width", type=int, default=144)
    ap.add_argument("--height", type=int, default=208)
    args = ap.parse_args()

    thumb = args.thumbnail_rgb565.read_bytes()
    expected = args.width * args.height * 2
    if len(thumb) != expected:
        raise SystemExit(
            f"thumbnail size {len(thumb)} != {args.width}x{args.height}x2 = {expected}"
        )

    rom = args.rom.read_bytes()
    wqw = build_wqw_store(rom, args.inner_name)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(thumb + wqw)
    print(f"wrote {args.output}")
    print(f"thumbnail bytes: {len(thumb)}")
    print(f"payload bytes:   {len(rom)}")
    print(f"wrapper bytes:   {len(thumb) + len(wqw)}")

if __name__ == "__main__":
    main()
