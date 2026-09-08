#!/usr/bin/env python3
"""Offline reference implementation for XGO built-in game-list stable merge.

This is the byte-exact algorithm the on-device Refresh scanner must reproduce:
- preserve every existing catalog index and string byte;
- discover physical ROM filenames;
- append only names missing from slot 0;
- append basename fallbacks to slots 1 and 2;
- never reorder or delete.

The tool intentionally does not patch firmware.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

DEFAULT_EXTS = {
    "BKP","ZIP","ZFC","ZSF","ZMD","ZGB","ZFB",
    "SMC","FIG","SFC","GD3","GD7","DX2","BSX","SWC",
    "NES","NFC","FDS","UNF","GBA","AGB","GBZ","GBC","GB","SGB",
    "BIN","MD","SMD","GEN","SMS",
}


def parse_catalog(data: bytes) -> tuple[list[int], bytes, list[bytes]]:
    if len(data) < 4:
        raise ValueError("catalog too short")
    count = struct.unpack_from("<I", data, 0)[0]
    table_end = 4 + count * 4
    if table_end > len(data):
        raise ValueError("offset table outside file")
    offsets = list(struct.unpack_from(f"<{count}I", data, 4)) if count else []
    blob = data[table_end:]
    strings: list[bytes] = []
    for i, off in enumerate(offsets):
        if off >= len(blob):
            raise ValueError(f"offset {i} outside blob")
        end = blob.find(b"\0", off)
        if end < 0:
            raise ValueError(f"string {i} is not NUL terminated")
        strings.append(blob[off:end])
    if offsets:
        final_end = offsets[-1] + len(strings[-1]) + 1
        if final_end != len(blob):
            raise ValueError("catalog has trailing bytes/footer; stable append assumption invalid")
    elif blob:
        raise ValueError("zero-count catalog has unexpected payload")
    return offsets, blob, strings


def append_exact(data: bytes, value: bytes) -> bytes:
    offsets, blob, _ = parse_catalog(data)
    count = len(offsets)
    return (
        struct.pack("<I", count + 1)
        + (struct.pack(f"<{count}I", *offsets) if offsets else b"")
        + struct.pack("<I", len(blob))
        + blob
        + value
        + b"\0"
    )


def basename_bytes(filename: bytes) -> bytes:
    dot = filename.rfind(b".")
    return filename[:dot] if dot > 0 else filename


def valid_rom_name(name: str, exts: set[str]) -> bool:
    if not name or name in {".", ".."}:
        return False
    suffix = Path(name).suffix
    return bool(suffix) and suffix[1:].upper() in exts


def stable_merge(slot0: bytes, slot1: bytes, slot2: bytes, filenames: list[str]) -> tuple[bytes, bytes, bytes, list[str]]:
    _, _, s0 = parse_catalog(slot0)
    _, _, s1 = parse_catalog(slot1)
    _, _, s2 = parse_catalog(slot2)
    if not (len(s0) == len(s1) == len(s2)):
        raise ValueError("triplet counts are not aligned")

    existing = {s.decode("utf-8", "surrogateescape") for s in s0}
    additions = sorted({n for n in filenames if n not in existing}, key=lambda x: x.casefold())

    out0, out1, out2 = slot0, slot1, slot2
    for name in additions:
        raw = name.encode("utf-8", "surrogateescape")
        base = basename_bytes(raw)
        out0 = append_exact(out0, raw)
        out1 = append_exact(out1, base)
        out2 = append_exact(out2, base)

    c0 = struct.unpack_from("<I", out0, 0)[0]
    c1 = struct.unpack_from("<I", out1, 0)[0]
    c2 = struct.unpack_from("<I", out2, 0)[0]
    if not (c0 == c1 == c2):
        raise AssertionError("output triplet counts diverged")
    return out0, out1, out2, additions


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom-dir", type=Path, required=True)
    ap.add_argument("--slot0", type=Path, required=True)
    ap.add_argument("--slot1", type=Path, required=True)
    ap.add_argument("--slot2", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--extensions", default=",".join(sorted(DEFAULT_EXTS)))
    args = ap.parse_args()

    exts = {x.strip().upper() for x in args.extensions.split(",") if x.strip()}
    physical = sorted(
        p.name for p in args.rom_dir.iterdir()
        if p.is_file() and valid_rom_name(p.name, exts)
    )

    original = [args.slot0.read_bytes(), args.slot1.read_bytes(), args.slot2.read_bytes()]
    merged0, merged1, merged2, additions = stable_merge(*original, physical)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs = [merged0, merged1, merged2]
    inputs = [args.slot0, args.slot1, args.slot2]
    for src, data in zip(inputs, outputs):
        (args.out_dir / src.name).write_bytes(data)

    before = struct.unpack_from("<I", original[0], 0)[0]
    after = struct.unpack_from("<I", merged0, 0)[0]
    print(f"count {before} -> {after}")
    for name in additions:
        print(f"+ {name}")


if __name__ == "__main__":
    main()
