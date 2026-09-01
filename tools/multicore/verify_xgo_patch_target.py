#!/usr/bin/env python3
"""Verify that a bisrv.asd is the preserved XGO firmware expected by our
Multicore patch research.

This tool DOES NOT modify the image. It only checks the firmware fingerprint,
reserved injection windows, and original instruction bytes at candidate patch
sites. A future patcher should run equivalent checks before changing anything.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

EXPECTED_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"

EXPECTED_BYTES = {
    0x001270: bytes.fromhex("c3 80 1c 3c 74 47 9c 27"),
    0x0030D4: bytes.fromhex("ad de 1e 3c ad be de 37"),
    0x0495A0: bytes.fromhex("ff ff 00 10 00 00 00 00"),
    0x049744: bytes.fromhex("3a 41 0c 0c 00 00 00 00"),
    0x360CF4: bytes.fromhex("44 80 0d 0c 21 28 00 00"),
}

ZERO_RANGES = {
    "loader workspace": (0x1500, 0x2180),
    "debug-font workspace": (0x2260, 0x2500),
}


def verify(path: Path) -> bool:
    image = path.read_bytes()
    ok = True

    digest = hashlib.sha256(image).hexdigest()
    print(f"SHA-256: {digest}")
    if digest != EXPECTED_SHA256:
        print("FAIL: firmware SHA-256 does not match preserved XGO image")
        ok = False
    else:
        print("OK: exact preserved XGO firmware fingerprint")

    for name, (start, end) in ZERO_RANGES.items():
        chunk = image[start:end]
        if len(chunk) != end - start:
            print(f"FAIL: {name} is outside/truncated in image")
            ok = False
        elif any(chunk):
            first = next(i for i, b in enumerate(chunk) if b)
            print(f"FAIL: {name} is not empty; first non-zero at 0x{start + first:x}")
            ok = False
        else:
            print(f"OK: {name} 0x{start:x}..0x{end - 1:x} is all zero")

    for offset, expected in EXPECTED_BYTES.items():
        actual = image[offset:offset + len(expected)]
        if actual != expected:
            print(
                f"FAIL: bytes at 0x{offset:x}: expected {expected.hex(' ')}, "
                f"got {actual.hex(' ')}"
            )
            ok = False
        else:
            print(f"OK: patch-site signature at 0x{offset:x}: {actual.hex(' ')}")

    return ok


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bisrv", type=Path, help="path to XGO bios/bisrv.asd")
    args = parser.parse_args()

    if not args.bisrv.is_file():
        parser.error(f"not a file: {args.bisrv}")

    if verify(args.bisrv):
        print("\nPASS: image matches the researched XGO Multicore patch target")
        return 0

    print("\nREFUSED: image does not match the researched XGO patch target")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
