#!/usr/bin/env python3
"""Compose native Snes9x2005 interception onto exact mapper-v19 firmware."""

from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

MAPPER_V19_SHA256 = "466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab"
PAYLOAD_OFFSET = 0x200
LCFG_SIZE_OFFSET = 0x184
LCFG_CRC_OFFSET = 0x18C

LOADER_OFFSET = 0x2230
LOADER_END = 0x3000
SNES_JAL_OFFSET = 0x360E40

EXPECTED_STOCK_SNES_JAL = bytes.fromhex("76 7e 0d 0c")
# jal 0x80002230
LOADER_JAL = bytes.fromhex("8c 08 00 0c")

def crc32_mpeg2(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = (((crc << 1) ^ 0x04C11DB7) if (crc & 0x80000000) else (crc << 1)) & 0xFFFFFFFF
    return crc

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("mapper_v19_asd", type=Path)
    ap.add_argument("loader_bin", type=Path)
    ap.add_argument("output_asd", type=Path)
    args=ap.parse_args()

    original=args.mapper_v19_asd.read_bytes()
    loader=args.loader_bin.read_bytes()

    digest=sha256(original)
    if digest != MAPPER_V19_SHA256:
        raise SystemExit(f"Refusing non-v19 firmware: {digest}")

    if len(loader) <= 0 or len(loader) > LOADER_END-LOADER_OFFSET:
        raise SystemExit(f"Refusing loader size {len(loader)}")

    if any(original[LOADER_OFFSET:LOADER_END]):
        raise SystemExit("Refusing patch: v19 relocation cave is not all zero")

    if original[SNES_JAL_OFFSET:SNES_JAL_OFFSET+4] != EXPECTED_STOCK_SNES_JAL:
        raise SystemExit("Refusing patch: SNES dispatch no longer matches expected v19 bytes")

    patched=bytearray(original)
    patched[LOADER_OFFSET:LOADER_OFFSET+len(loader)] = loader
    patched[SNES_JAL_OFFSET:SNES_JAL_OFFSET+4] = LOADER_JAL

    payload_size=len(patched)-PAYLOAD_OFFSET
    struct.pack_into("<I", patched, LCFG_SIZE_OFFSET, payload_size)
    crc=crc32_mpeg2(bytes(patched[PAYLOAD_OFFSET:]))
    struct.pack_into("<I", patched, LCFG_CRC_OFFSET, crc)

    if crc32_mpeg2(bytes(patched[PAYLOAD_OFFSET:])) != crc:
        raise SystemExit("LCFG CRC self-check failed")

    args.output_asd.write_bytes(patched)
    print(f"mapper-v19 input : {digest}")
    print(f"loader bytes     : {len(loader)}")
    print(f"SNES patch       : 0x{SNES_JAL_OFFSET:08x} -> jal 0x80002230")
    print(f"payload CRC      : 0x{crc:08x}")
    print(f"output SHA-256   : {sha256(bytes(patched))}")

if __name__ == "__main__":
    main()
