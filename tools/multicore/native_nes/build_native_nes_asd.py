#!/usr/bin/env python3
"""Build a guarded XGO ASD that redirects only the native NES runner call.

This tool never touches SPI NOR and never creates Firmware.upk. It accepts only
the exact preserved XGO firmware revision, injects a loader into the verified
zero-filled firmware cave, redirects the NES dispatch JAL, and reseals LCFG.
"""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path

STOCK_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"

PAYLOAD_OFFSET = 0x200
LCFG_SIZE_OFFSET = 0x184
LCFG_CRC_OFFSET = 0x18C

LOADER_OFFSET = 0x1500
LOADER_END = 0x2180
NES_JAL_OFFSET = 0x360E20

# XGO stock at 0x80360e20: jal 0x8035f63c (run_nes)
EXPECTED_STOCK_NES_JAL = bytes.fromhex("8f 7d 0d 0c")

# jal 0x80001500, little-endian MIPS32
LOADER_JAL = bytes.fromhex("40 05 00 0c")


def crc32_mpeg2(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ 0x04C11DB7) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
    return crc


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stock_asd", type=Path)
    ap.add_argument("loader_bin", type=Path)
    ap.add_argument("output_asd", type=Path)
    args = ap.parse_args()

    original = args.stock_asd.read_bytes()
    loader = args.loader_bin.read_bytes()

    digest = sha256(original)
    if digest != STOCK_SHA256:
        raise SystemExit(
            f"Refusing to patch: stock SHA-256 is {digest}, expected {STOCK_SHA256}"
        )

    if len(loader) > LOADER_END - LOADER_OFFSET:
        raise SystemExit(
            f"Refusing to patch: loader is {len(loader)} bytes; "
            f"capacity is {LOADER_END - LOADER_OFFSET}"
        )

    if any(original[LOADER_OFFSET:LOADER_END]):
        raise SystemExit("Refusing to patch: XGO loader cave is not all zero")

    actual_jal = original[NES_JAL_OFFSET:NES_JAL_OFFSET + 4]
    if actual_jal != EXPECTED_STOCK_NES_JAL:
        raise SystemExit(
            "Refusing to patch: native NES dispatch differs from known XGO stock bytes "
            f"({actual_jal.hex(' ')})"
        )

    patched = bytearray(original)
    patched[LOADER_OFFSET:LOADER_OFFSET + len(loader)] = loader
    patched[NES_JAL_OFFSET:NES_JAL_OFFSET + 4] = LOADER_JAL

    payload_size = len(patched) - PAYLOAD_OFFSET
    struct.pack_into("<I", patched, LCFG_SIZE_OFFSET, payload_size)

    crc = crc32_mpeg2(bytes(patched[PAYLOAD_OFFSET:]))
    struct.pack_into("<I", patched, LCFG_CRC_OFFSET, crc)

    if struct.unpack_from("<I", patched, LCFG_SIZE_OFFSET)[0] != payload_size:
        raise SystemExit("Internal error: LCFG payload-size write failed")
    if crc32_mpeg2(bytes(patched[PAYLOAD_OFFSET:])) != crc:
        raise SystemExit("Internal error: LCFG CRC verification failed")
    if patched[NES_JAL_OFFSET:NES_JAL_OFFSET + 4] != LOADER_JAL:
        raise SystemExit("Internal error: native NES JAL patch failed")

    args.output_asd.write_bytes(patched)

    print(f"stock SHA-256 : {digest}")
    print(f"loader bytes  : {len(loader)} / {LOADER_END - LOADER_OFFSET}")
    print(f"NES patch     : 0x{NES_JAL_OFFSET:08x} -> jal 0x80001500")
    print(f"payload size  : 0x{payload_size:08x}")
    print(f"payload CRC   : 0x{crc:08x}")
    print(f"output SHA-256: {sha256(bytes(patched))}")
    print(f"wrote          {args.output_asd}")


if __name__ == "__main__":
    main()
