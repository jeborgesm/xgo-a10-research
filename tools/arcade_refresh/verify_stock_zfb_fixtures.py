#!/usr/bin/env python3
"""Validate zfb_codec.py against the four direct stock XGO fixtures.

Usage:
  python verify_stock_zfb_fixtures.py <fixture-directory>

The fixture directory must contain the original filenames listed below.
The test parses each stock file and rebuilds it from its own 59,904-byte
preview plus the parsed driver name. Rebuild must be byte-identical.
"""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path
from zfb_codec import PREVIEW_BYTES, build_zfb, parse_zfb

FIXTURES = {
    "Cadillacs and Dinosaurs.zfb": (
        "dino.zip",
        59918,
        "906395f282ba3c048311a77f32ee929622c92b074a1ff3f46450ddf19f06a6bc",
    ),
    "Street Fighter Alpha 3.zfb": (
        "sfa3.zip",
        59918,
        "c7f9ba3d3e8bf260d2ceaf31481e6d35aa6a0a61d7e490a63a6331de6f331a56",
    ),
    "Knights of Valour.zfb": (
        "kov.zip",
        59917,
        "f102b67b5beb7e2acdc248a249a45c633bd5c1830d6d8b43ab0a136c487cf774",
    ),
    "The King of Fighters '94.zfb": (
        "kof94.zip",
        59919,
        "42fe80265245293f097ba415f070a4840bcb2dd985a5bcd1558c4b6db0c726b9",
    ),
}

def main(root: Path) -> None:
    for filename, (driver, size, sha) in FIXTURES.items():
        blob = (root / filename).read_bytes()
        assert len(blob) == size, (filename, len(blob), size)
        assert hashlib.sha256(blob).hexdigest() == sha, filename
        record = parse_zfb(blob)
        assert record.driver_zip == driver, (filename, record.driver_zip, driver)
        assert len(record.preview_rgb565le) == PREVIEW_BYTES
        rebuilt = build_zfb(record.preview_rgb565le, record.driver_zip)
        assert rebuilt == blob, filename
        print(f"PASS {filename}: {driver}, {size} bytes, byte-identical rebuild")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_stock_zfb_fixtures.py <fixture-directory>")
    main(Path(sys.argv[1]))
