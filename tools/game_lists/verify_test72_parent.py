#!/usr/bin/env python3
"""Verify the exact cumulative Test72 parent before stock-catalog enrichment.

This tool deliberately does not patch anything.  It accepts only the documented
hardware-proven Test72 artifact, verifies the protected core, extracts the
package, and prints hashes for the mutable/runtime components that the next
builder must pin explicitly.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import zipfile
from pathlib import Path

TEST72_ZIP_SHA256 = "af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16"
PROTECTED_CORE_SHA256 = "60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e"

REQUIRED = (
    "bios/bisrv.asd",
    "CLASSIC/refresh.xgc",
    "cores/classic-mame2000/core.xgc",
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("zip", type=Path, help="xgo-classic-test72-one-shot-batch-import.zip")
    ap.add_argument("--extract", type=Path, help="optional clean extraction directory")
    args = ap.parse_args()

    if not args.zip.is_file():
        print(f"ERROR: not a file: {args.zip}", file=sys.stderr)
        return 2

    zhash = sha256_file(args.zip)
    print(f"zip_sha256={zhash}")
    if zhash != TEST72_ZIP_SHA256:
        print("ERROR: artifact is not the documented hardware-proven Test72 ZIP", file=sys.stderr)
        print(f"expected={TEST72_ZIP_SHA256}", file=sys.stderr)
        return 3

    with zipfile.ZipFile(args.zip, "r") as zf:
        names = set(zf.namelist())
        missing = [name for name in REQUIRED if name not in names]
        if missing:
            print("ERROR: Test72 package is missing required runtime files:", file=sys.stderr)
            for name in missing:
                print(f"  {name}", file=sys.stderr)
            return 4

        blobs = {name: zf.read(name) for name in REQUIRED}

        core_hash = sha256_bytes(blobs["cores/classic-mame2000/core.xgc"])
        if core_hash != PROTECTED_CORE_SHA256:
            print("ERROR: protected classic-mame2000 core hash mismatch", file=sys.stderr)
            print(f"expected={PROTECTED_CORE_SHA256}", file=sys.stderr)
            print(f"actual={core_hash}", file=sys.stderr)
            return 5

        print(f"firmware_sha256={sha256_bytes(blobs['bios/bisrv.asd'])}")
        print(f"classic_refresh_sha256={sha256_bytes(blobs['CLASSIC/refresh.xgc'])}")
        print(f"classic_core_sha256={core_hash}")
        print(f"entries={len(zf.infolist())}")

        if args.extract:
            out = args.extract
            if out.exists() and any(out.iterdir()):
                print(f"ERROR: extraction directory is not empty: {out}", file=sys.stderr)
                return 6
            out.mkdir(parents=True, exist_ok=True)
            zf.extractall(out)
            print(f"extracted={out}")

    print("PASS: exact Test72 parent verified; safe to begin additive stock-SFC build work")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
