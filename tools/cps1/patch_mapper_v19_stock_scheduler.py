#!/usr/bin/env python3
"""Build XGO mapper-v19 + sibling-style stock scheduler candidate.

This patcher deliberately requires the exact hardware-confirmed mapper-v19
firmware and writes a new file. It does not modify the input in place.
"""

from __future__ import annotations
import argparse, hashlib, struct
from pathlib import Path

V19_SHA256 = "466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab"
HEADER_SIZE = 0x200
CRC_OFFSET = 0x18C
POLY = 0x04C11DB7

# Main wall-time / bounded-catchup helper, linked at 0x8035eee8.
MAIN_OFFSET = 0x0035EEE8
MAIN_WORDS = [
    0x0c0c3fb2, 0x00000000, 0x8f89f300, 0x00495023,
    0x8f8b89b4, 0x014b0019, 0x00006012, 0x240d03e8,
    0x018d001b, 0x00007012, 0x8f8f89b8, 0x25f80001,
    0x01d8c82b, 0x17200054, 0x00000000, 0xaf9889b8,
    0x8f8889a0, 0x030e482b, 0x2d0a0003, 0x012a4824,
    0x15200006, 0x25080001, 0xaf8089a0, 0xaf8e89b8,
    0xaf80f31c, 0x080d7bdc, 0x00000000, 0xaf8889a0,
    0x24090001, 0xaf89f31c, 0x080d7bdc, 0x00000000,
]

# Early path at 0x8035f070: sleep 1 ms, then recompute against absolute wall time.
EARLY_OFFSET = 0x0035F070
EARLY_WORDS = [0x0c0c3d20, 0x24040001, 0x080d7bba, 0x00000000]

# Exact original XGO words required at all small edit sites.
WORD_PATCHES = {
    # Ordinary scheduler initialization.
    0x0035EE94: (0xaf8689b8, 0xaf8089b8),  # completed = 0
    0x0035EE9C: (0xaf8789a0, 0xaf8089a0),  # catchup = 0
    0x0035EEB4: (0xaf80f300, 0xaf82f300),  # start_tick = setup tick

    # Pause/audio re-entry: establish a fresh wall-time anchor and reset state.
    0x0035F050: (0xaf80f300, 0xaf8089a0),  # catchup = 0 during wait
    0x0035F05C: (0x8f83f300, 0xaf82f300),  # start_tick = fresh post-wait tick
    0x0035F060: (0x8f84a0fc, 0xaf8089b8),  # completed = 0
    0x0035F064: (0x8f8589a4, 0x080d7bba),  # jump main scheduler
    0x0035F068: (0x00403021, 0xaf8089a0),  # delay slot: catchup = 0
    0x0035F06C: (0x00431021, 0x00000000),  # clear obsolete debt-loop op
}

# The main and early blocks must still contain exact known XGO stock/v19 bytes.
# Hashes are over the original bytes, not the patched bytes. They make the
# patch refuse a v19 derivative whose scheduler code has already changed.
EXPECTED_MAIN_SHA256 = "d67c117fa1e6721da5f616de16014751e3ac3c297a5fa889246d8a66dfd02b09"
EXPECTED_EARLY_SHA256 = "b28cce0792c966fc666c0a7e59b9506056d6dbe016356ac42c73daead28d1157"

def crc32_mpeg2(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = (((crc << 1) ^ POLY) if crc & 0x80000000 else (crc << 1)) & 0xFFFFFFFF
    return crc

def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def u32(data: bytes | bytearray, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]

def words_bytes(words: list[int]) -> bytes:
    return b"".join(struct.pack("<I", w) for w in words)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mapper_v19_asd", type=Path)
    ap.add_argument("output_asd", type=Path)
    args = ap.parse_args()

    if args.mapper_v19_asd.resolve() == args.output_asd.resolve():
        raise SystemExit("refusing to modify mapper-v19 input in place")

    original = args.mapper_v19_asd.read_bytes()
    digest = h(original)
    if digest != V19_SHA256:
        raise SystemExit(f"refusing non-v19 firmware: SHA-256 {digest}")
    if original[:4] != b"LCFG":
        raise SystemExit("refusing image without LCFG magic")

    for off, (expected, _new) in WORD_PATCHES.items():
        got = u32(original, off)
        if got != expected:
            raise SystemExit(
                f"unexpected original word at 0x{off:08x}: "
                f"0x{got:08x} != 0x{expected:08x}"
            )

    original_main = original[MAIN_OFFSET:MAIN_OFFSET + len(MAIN_WORDS) * 4]
    original_early = original[EARLY_OFFSET:EARLY_OFFSET + len(EARLY_WORDS) * 4]
    if h(original_main) != EXPECTED_MAIN_SHA256:
        raise SystemExit("main scheduler block is not the expected v19/XGO block")
    if h(original_early) != EXPECTED_EARLY_SHA256:
        raise SystemExit("early scheduler island is not the expected v19/XGO block")

    patched = bytearray(original)
    for off, (_expected, new) in WORD_PATCHES.items():
        struct.pack_into("<I", patched, off, new)
    patched[MAIN_OFFSET:MAIN_OFFSET + len(MAIN_WORDS) * 4] = words_bytes(MAIN_WORDS)
    patched[EARLY_OFFSET:EARLY_OFFSET + len(EARLY_WORDS) * 4] = words_bytes(EARLY_WORDS)

    crc = crc32_mpeg2(bytes(patched[HEADER_SIZE:]))
    struct.pack_into("<I", patched, CRC_OFFSET, crc)

    allowed = set(range(CRC_OFFSET, CRC_OFFSET + 4))
    for off in WORD_PATCHES:
        allowed.update(range(off, off + 4))
    allowed.update(range(MAIN_OFFSET, MAIN_OFFSET + len(MAIN_WORDS) * 4))
    allowed.update(range(EARLY_OFFSET, EARLY_OFFSET + len(EARLY_WORDS) * 4))
    changed = {i for i,(a,b) in enumerate(zip(original, patched)) if a != b}
    unexpected = changed - allowed
    if unexpected:
        raise SystemExit(f"internal error: unexpected changed byte at 0x{min(unexpected):x}")

    args.output_asd.write_bytes(patched)
    print(f"mapper-v19 input : {digest}")
    print(f"main helper       : 0x{MAIN_OFFSET:08x}, {len(MAIN_WORDS)*4} bytes")
    print(f"early helper      : 0x{EARLY_OFFSET:08x}, {len(EARLY_WORDS)*4} bytes")
    print(f"changed bytes     : {len(changed)}")
    print(f"payload CRC       : 0x{crc:08x}")
    print(f"output SHA-256    : {h(bytes(patched))}")
    print(f"wrote             : {args.output_asd}")

if __name__ == "__main__":
    main()
