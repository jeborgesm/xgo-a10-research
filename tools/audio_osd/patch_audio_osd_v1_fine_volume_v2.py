#!/usr/bin/env python3
"""Patch the exact Audio OSD v1 golden baseline with fine-grained volume v2."""

from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

BASE_SHA256 = "1fc85114909d6107ff80be6e199d54dd1d9b918454ceede61d5108246d6f50c1"
OUT_SHA256 = "6b3261a9871c2b5678428ae1985176718c140178564ea924241bf6889ec714ac"
HEADER_SIZE = 0x200
CRC_OFFSET = 0x18C
POLY = 0x04C11DB7

VOL_INC_OFFSET = 0x35D67C
VOL_INC_OLD = 0x25AC0021
VOL_INC_NEW = 0x25AC0009

OSD_MAP_OFFSET = 0x27FC
OSD_MAP_END = 0x2844
OSD_MAP_WORDS = [
    0x240F0015,  # addiu t7,zero,21
    0x016F0019,  # multu t3,t7
    0x00007012,  # mflo t6
    0x000E7142,  # srl t6,t6,5
    0x1000000D,  # b 0x80002844
    0x00000000,
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def crc32_mpeg2(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = (((crc << 1) ^ POLY) if crc & 0x80000000 else (crc << 1)) & 0xFFFFFFFF
    return crc


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("audio_osd_v1_bisrv", type=Path)
    ap.add_argument("output_bisrv", type=Path)
    args = ap.parse_args()

    original = args.audio_osd_v1_bisrv.read_bytes()
    if sha256(original) != BASE_SHA256:
        raise SystemExit(f"refusing non-golden OSD v1 baseline: {sha256(original)}")

    if struct.unpack_from("<I", original, VOL_INC_OFFSET)[0] != VOL_INC_OLD:
        raise SystemExit("unexpected volume increment instruction")

    patched = bytearray(original)
    struct.pack_into("<I", patched, VOL_INC_OFFSET, VOL_INC_NEW)

    for i, word in enumerate(OSD_MAP_WORDS):
        struct.pack_into("<I", patched, OSD_MAP_OFFSET + 4*i, word)
    for off in range(OSD_MAP_OFFSET + 4*len(OSD_MAP_WORDS), OSD_MAP_END, 4):
        struct.pack_into("<I", patched, off, 0)

    crc = crc32_mpeg2(bytes(patched[HEADER_SIZE:]))
    struct.pack_into("<I", patched, CRC_OFFSET, crc)

    out = bytes(patched)
    if sha256(out) != OUT_SHA256:
        raise SystemExit(f"unexpected output SHA-256: {sha256(out)}")

    args.output_bisrv.write_bytes(out)
    print(f"input  SHA-256: {BASE_SHA256}")
    print(f"output SHA-256: {OUT_SHA256}")
    print(f"CRC-32/MPEG-2 : 0x{crc:08x}")
    print("volume cycle   : 0,9,18,27,36,45,54,63,72,81,90,99,0")


if __name__ == "__main__":
    main()
