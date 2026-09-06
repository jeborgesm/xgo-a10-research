#!/usr/bin/env python3
"""Patch the exact protected XGO scheduler baseline with transient volume OSD v1."""

from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

BASE_SHA256 = "9136479687e921fc478ad89ccce3af94296366768a83600312b3bed5ee294607"
OUTPUT_SHA256 = "1fc85114909d6107ff80be6e199d54dd1d9b918454ceede61d5108246d6f50c1"
HEADER_SIZE = 0x200
CRC_OFFSET = 0x18C
POLY = 0x04C11DB7

CAVE_OFFSET = 0x2780
CAVE_END = 0x3000
HOOK_OFFSET = 0x35C458
HOOK_OLD = 0x080D70C7      # j 0x8035c31c
HOOK_NEW = 0x080009E0      # j 0x80002780

CODE_HEX = (
"0080083c8029098dc3800a3c543a4b8dff006b31060020150000000001000924"
"802909ad84290bad5b0a00080000000084290c8d04006c110000000084290bad"
"78000d2488290dad88290d8d6700a011000000004800ae2c6400c01500000000"
"1000ce2c6100c015000000005f00801000000000ffffad2588290dad0a006011"
"0000000022006f2d0a00e0150000000043006f2d0a00e0150000000040000e24"
"080000100000000025700000050000100000000015000e240200001000000000"
"2a000e24e0ffbd271c00bfaf1000a4af1400a5af1800a6af0c00a7af0800aeaf"
"f0ffd92419002703127800000800ef2540780f0021788f000080183c8c291827"
"08001924000002240000e395000003a70800ae8f2b184e001100601000000000"
"ffff03240000e3a50200ef2502001827010042244000432cf3ff601400000000"
"4018070080ff63242178e301ffff3927ecff2017000000000400001000000000"
"00000324efff001000000000c7700d0c000000001000a48f0c00a78f1800a68f"
"f0ffd92419002703127800000800ef2540780f0021788f000080183c8c291827"
"0800192440000224000003970000e3a50200ef2502001827ffff4224faff4014"
"000000004018070080ff63242178e301ffff3927f3ff2017000000001c00bf8f"
"2000bd270800e00300000000c7700d0800000000"
)

BLOB_SIZE = 1548
BLOB_SHA256 = "2556cad397c66f5ac98a4f772b05d67eb86eb946bc785c781f1e426ec8954227"


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
    ap.add_argument("protected_bisrv", type=Path)
    ap.add_argument("output_bisrv", type=Path)
    args = ap.parse_args()

    original = args.protected_bisrv.read_bytes()
    if sha256(original) != BASE_SHA256:
        raise SystemExit(f"refusing non-protected baseline: {sha256(original)}")
    if original[:4] != b"LCFG":
        raise SystemExit("refusing image without LCFG magic")
    if any(original[CAVE_OFFSET:CAVE_END]):
        raise SystemExit("refusing: OSD cave 0x2780..0x2fff is not all zero")
    if struct.unpack_from("<I", original, HOOK_OFFSET)[0] != HOOK_OLD:
        raise SystemExit("refusing: run_screen_write tail hook is not exact expected instruction")

    code = bytes.fromhex(CODE_HEX)
    blob = code + bytes(BLOB_SIZE - len(code))
    if sha256(blob) != BLOB_SHA256:
        raise SystemExit("internal error: embedded OSD blob hash mismatch")
    if len(blob) > CAVE_END - CAVE_OFFSET:
        raise SystemExit("internal error: OSD blob exceeds verified cave")

    patched = bytearray(original)
    patched[CAVE_OFFSET:CAVE_OFFSET + len(blob)] = blob
    struct.pack_into("<I", patched, HOOK_OFFSET, HOOK_NEW)

    crc = crc32_mpeg2(bytes(patched[HEADER_SIZE:]))
    struct.pack_into("<I", patched, CRC_OFFSET, crc)

    allowed = set(range(CRC_OFFSET, CRC_OFFSET + 4))
    allowed.update(range(HOOK_OFFSET, HOOK_OFFSET + 4))
    allowed.update(range(CAVE_OFFSET, CAVE_OFFSET + len(blob)))
    changed = {i for i, (a, b) in enumerate(zip(original, patched)) if a != b}
    unexpected = changed - allowed
    if unexpected:
        raise SystemExit(f"internal error: unexpected changed byte 0x{min(unexpected):x}")

    out = bytes(patched)
    if sha256(out) != OUTPUT_SHA256:
        raise SystemExit(f"internal error: output SHA mismatch {sha256(out)}")

    args.output_bisrv.write_bytes(out)
    print(f"baseline SHA-256 : {BASE_SHA256}")
    print(f"OSD blob          : {len(blob)} bytes @ 0x{CAVE_OFFSET:08x}")
    print(f"cave headroom     : {(CAVE_END-CAVE_OFFSET)-len(blob)} bytes")
    print(f"hook              : 0x{HOOK_OFFSET:08x} -> 0x80002780")
    print(f"changed bytes     : {len(changed)}")
    print(f"payload CRC       : 0x{crc:08x}")
    print(f"output SHA-256    : {sha256(out)}")


if __name__ == "__main__":
    main()
