#!/usr/bin/env python3
"""Build XGO gameplay-audio Test A from the protected cumulative firmware.

Input must be the exact HW-proven cumulative firmware from the current golden
Refresh baseline. The builder refuses stock or any experimental firmware.

Test A changes only the generic 22050-Hz audio path:
  0x80306E00  force selected hardware rate to requested s2 (22050 on stock FBA)
  0x802FDFC8  make the first 22050 repetition comparison miss
  0x802FE068  make the second 22050 repetition comparison miss

Then it reseals the LCFG CRC32/MPEG-2 field.

No scheduler, frontend quantum, sample_num, admission threshold, mono policy,
auto-resume, SNES, Refresh, Mapper, or Audio OSD code is changed.
"""
from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

BASE = 0x80000000
EXPECTED_INPUT_SHA256 = "ea442b74bdc07cd5e05ec2de8da5c997848a76ed3125681c1955fbcb29b66152"
EXPECTED_SIZE = 12_768_452
LCFG_HEADER = 0x200
LCFG_SIZE_OFF = 0x184
LCFG_CRC_OFF = 0x18C

PATCHES = (
    (0x80306E00, 0x3402AC44, 0x02401021, "selected hardware rate: 44100 -> requested s2"),
    (0x802FDFC8, 0x24025622, 0x24025623, "bypass first 22050 x2 repetition compare"),
    (0x802FE068, 0x24025622, 0x24025623, "bypass second 22050 x2 repetition compare"),
)

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def crc32_mpeg2(data: bytes) -> int:
    crc = 0xFFFFFFFF
    poly = 0x04C11DB7
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFFFFFFFF if crc & 0x80000000 else (crc << 1) & 0xFFFFFFFF
    return crc

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="protected cumulative bios/bisrv.asd")
    ap.add_argument("output", type=Path, help="new Test A bisrv.asd")
    args = ap.parse_args()

    original = args.input.read_bytes()
    if len(original) != EXPECTED_SIZE:
        raise SystemExit(f"REFUSE: size {len(original)} != {EXPECTED_SIZE}")
    got = sha256(original)
    if got != EXPECTED_INPUT_SHA256:
        raise SystemExit(f"REFUSE: input SHA256 {got} != protected {EXPECTED_INPUT_SHA256}")
    if original[:4] != b"LCFG":
        raise SystemExit("REFUSE: missing LCFG header")

    payload_size = struct.unpack_from("<I", original, LCFG_SIZE_OFF)[0]
    if payload_size != len(original) - LCFG_HEADER:
        raise SystemExit(f"REFUSE: LCFG payload size {payload_size:#x} inconsistent with file")

    fw = bytearray(original)
    for va, old, new, desc in PATCHES:
        off = va - BASE
        got_word = struct.unpack_from("<I", fw, off)[0]
        if got_word != old:
            raise SystemExit(f"REFUSE: {va:#010x} is {got_word:#010x}, expected {old:#010x} ({desc})")
        struct.pack_into("<I", fw, off, new)

    new_crc = crc32_mpeg2(fw[LCFG_HEADER:])
    struct.pack_into("<I", fw, LCFG_CRC_OFF, new_crc)

    # Verify semantic diff: only three 4-byte words + CRC field may differ.
    allowed = set(range(LCFG_CRC_OFF, LCFG_CRC_OFF + 4))
    for va, _, _, _ in PATCHES:
        off = va - BASE
        allowed.update(range(off, off + 4))
    changed = [i for i,(a,b) in enumerate(zip(original,fw)) if a != b]
    unexpected = [i for i in changed if i not in allowed]
    if unexpected:
        raise SystemExit(f"REFUSE: unexpected changed offsets begin {unexpected[:16]}")

    # Re-verify payload CRC after writing header CRC (header is outside payload).
    check = crc32_mpeg2(fw[LCFG_HEADER:])
    if check != new_crc:
        raise SystemExit("REFUSE: CRC self-check failed")

    args.output.write_bytes(fw)
    print(f"input_sha256={got}")
    print(f"output_sha256={sha256(fw)}")
    print(f"lcfg_crc32_mpeg2=0x{new_crc:08X}")
    print(f"changed_bytes={len(changed)}")
    for va, old, new, desc in PATCHES:
        print(f"{va:#010x}: {old:#010x} -> {new:#010x}  {desc}")

if __name__ == "__main__":
    main()
