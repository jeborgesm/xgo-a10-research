#!/usr/bin/env python3
"""Build a minimally patched XGO bisrv.asd for an external-payload probe.

This tool DOES NOT touch SPI NOR and does not create Firmware.upk.
It only creates a new SD-loaded ASD file from the exact preserved XGO image.

The selected stock emulator-family call is redirected to the loader at
0x80001500. Every supported call site has an exact stock-byte signature, so a
firmware mismatch causes a hard refusal before any output is written.
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

# run_game() family dispatch sites in this exact XGO firmware revision.
# Values are (ASD file offset, expected original 4-byte little-endian JAL).
DISPATCH_SITES = {
    "gba":    (0x360CF4, bytes.fromhex("44 80 0d 0c")),  # jal 0x80360110
    "gb":     (0x360E10, bytes.fromhex("2b 81 0d 0c")),  # jal 0x803604ac
    "nes":    (0x360E20, bytes.fromhex("8f 7d 0d 0c")),  # jal 0x8035f63c
    "sega":   (0x360E30, bytes.fromhex("5d 7f 0d 0c")),  # jal 0x8035fd74
    "snes":   (0x360E40, bytes.fromhex("76 7e 0d 0c")),  # jal 0x8035f9d8
}

# Friendly aliases accepted by the command line.
FAMILY_ALIASES = {
    "gba": "gba",
    "gb": "gb",
    "gbc": "gb",
    "gb/gbc": "gb",
    "nes": "nes",
    "famicom": "nes",
    "sega": "sega",
    "md": "sega",
    "genesis": "sega",
    "sms": "sega",
    "snes": "snes",
    "sfc": "snes",
}

# jal 0x80001500, little-endian MIPS32
PROBE_LOADER_JAL = bytes.fromhex("40 05 00 0c")


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
    ap.add_argument(
        "--family",
        default="gba",
        help="stock emulator family to intercept: gba, gb/gbc, nes, sega, snes (default: gba)",
    )
    args = ap.parse_args()

    family_input = args.family.lower()
    family = FAMILY_ALIASES.get(family_input)
    if family is None:
        raise SystemExit(
            f"Unknown family {args.family!r}; choose one of: gba, gb, gbc, nes, sega, snes"
        )

    dispatch_offset, expected_stock_jal = DISPATCH_SITES[family]

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
        raise SystemExit("Refusing to patch: XGO loader window is not all zero")

    actual_jal = original[dispatch_offset:dispatch_offset + 4]
    if actual_jal != expected_stock_jal:
        raise SystemExit(
            f"Refusing to patch: {family.upper()} dispatch instruction differs from known "
            f"XGO stock bytes ({actual_jal.hex(' ')} != {expected_stock_jal.hex(' ')})"
        )

    patched = bytearray(original)
    patched[LOADER_OFFSET:LOADER_OFFSET + len(loader)] = loader
    patched[dispatch_offset:dispatch_offset + 4] = PROBE_LOADER_JAL

    payload_size = len(patched) - PAYLOAD_OFFSET
    struct.pack_into("<I", patched, LCFG_SIZE_OFFSET, payload_size)

    crc = crc32_mpeg2(bytes(patched[PAYLOAD_OFFSET:]))
    struct.pack_into("<I", patched, LCFG_CRC_OFFSET, crc)

    # Final self-audit before writing.
    if struct.unpack_from("<I", patched, LCFG_SIZE_OFFSET)[0] != payload_size:
        raise SystemExit("Internal error: LCFG payload-size write failed")
    if crc32_mpeg2(bytes(patched[PAYLOAD_OFFSET:])) != crc:
        raise SystemExit("Internal error: LCFG CRC verification failed")
    if patched[dispatch_offset:dispatch_offset + 4] != PROBE_LOADER_JAL:
        raise SystemExit("Internal error: dispatch JAL write failed")

    # Ensure no *other* native emulator call site was modified by this operation.
    for other_family, (other_offset, other_expected) in DISPATCH_SITES.items():
        if other_family == family:
            continue
        if patched[other_offset:other_offset + 4] != other_expected:
            raise SystemExit(
                f"Internal error: unrelated {other_family.upper()} dispatch site changed"
            )

    args.output_asd.write_bytes(patched)

    print(f"stock SHA-256 : {digest}")
    print(f"family        : {family}")
    print(f"dispatch off  : 0x{dispatch_offset:08x}")
    print(f"stock JAL     : {expected_stock_jal.hex(' ')}")
    print(f"patched JAL   : {PROBE_LOADER_JAL.hex(' ')}")
    print(f"loader bytes  : {len(loader)} / {LOADER_END - LOADER_OFFSET}")
    print(f"payload size  : 0x{payload_size:08x}")
    print(f"payload CRC   : 0x{crc:08x}")
    print(f"output SHA-256: {sha256(bytes(patched))}")
    print(f"wrote          {args.output_asd}")


if __name__ == "__main__":
    main()
