#!/usr/bin/env python3
"""Strict codec and stable-append planner for XGO synchronized catalog triplets.

The append transform preserves every original offset and string byte.
No sorting, deletion, normalization, or reserialization of existing entries.
"""
from __future__ import annotations
from dataclasses import dataclass
import struct

@dataclass(frozen=True)
class Catalog:
    raw: bytes
    count: int
    offsets: tuple[int, ...]
    blob: bytes
    strings: tuple[bytes, ...]


def parse_catalog(data: bytes) -> Catalog:
    if len(data) < 4:
        raise ValueError("catalog too short")
    count = struct.unpack_from("<I", data, 0)[0]
    table_end = 4 + count * 4
    if table_end > len(data):
        raise ValueError("offset table outside file")
    offsets = struct.unpack_from(f"<{count}I", data, 4) if count else ()
    blob = data[table_end:]
    strings = []
    previous = -1
    for i, off in enumerate(offsets):
        if off >= len(blob):
            raise ValueError(f"offset {i} outside blob")
        if off <= previous:
            raise ValueError(f"offset {i} is not strictly increasing")
        end = blob.find(b"\0", off)
        if end < 0:
            raise ValueError(f"string {i} not NUL terminated")
        if i + 1 < count and end + 1 != offsets[i + 1]:
            raise ValueError(f"catalog has gap/overlap after string {i}")
        strings.append(blob[off:end])
        previous = off
    if offsets:
        if offsets[0] != 0:
            raise ValueError("first offset is not zero")
        if offsets[-1] + len(strings[-1]) + 1 != len(blob):
            raise ValueError("trailing bytes/footer detected")
    elif blob:
        raise ValueError("zero-count catalog has payload")
    return Catalog(data, count, tuple(offsets), blob, tuple(strings))


def append_exact(data: bytes, value: bytes) -> bytes:
    if not value or b"\0" in value:
        raise ValueError("catalog value must be nonempty and NUL-free")
    c = parse_catalog(data)
    return (
        struct.pack("<I", c.count + 1)
        + (struct.pack(f"<{c.count}I", *c.offsets) if c.count else b"")
        + struct.pack("<I", len(c.blob))
        + c.blob + value + b"\0"
    )


def validate_triplet(slot0: bytes, slot1: bytes, slot2: bytes) -> tuple[Catalog, Catalog, Catalog]:
    cs = tuple(parse_catalog(x) for x in (slot0, slot1, slot2))
    if not (cs[0].count == cs[1].count == cs[2].count):
        raise ValueError("triplet counts diverge")
    return cs


def append_record(slot0: bytes, slot1: bytes, slot2: bytes,
                  zfb_name: str, title: str) -> tuple[bytes, bytes, bytes, bool]:
    cs = validate_triplet(slot0, slot1, slot2)
    z = zfb_name.encode("utf-8")
    t = title.encode("utf-8")
    if not z.lower().endswith(b".zfb"):
        raise ValueError("slot0 identity must end in .zfb")
    if not t or b"\0" in t or b"\0" in z:
        raise ValueError("invalid catalog text")

    # Exact slot0 identity is the idempotence key. Do not case-fold OEM names.
    if z in cs[0].strings:
        return slot0, slot1, slot2, False

    out = (append_exact(slot0, z), append_exact(slot1, t), append_exact(slot2, t))
    validate_triplet(*out)
    return (*out, True)


def assert_stable_prefix(before: bytes, after: bytes) -> None:
    a = parse_catalog(before)
    b = parse_catalog(after)
    if b.count != a.count + 1:
        raise AssertionError("not a single append")
    if b.offsets[:a.count] != a.offsets:
        raise AssertionError("old offsets changed")
    if not b.blob.startswith(a.blob):
        raise AssertionError("old string blob changed")
    if b.strings[:a.count] != a.strings:
        raise AssertionError("old strings changed")
