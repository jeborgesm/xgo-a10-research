#!/usr/bin/env python3
"""Verify an exact golden XGO artifact ZIP against the public manifest."""

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", type=Path)
    ap.add_argument("artifact_id")
    ap.add_argument("zipfile", type=Path)
    args = ap.parse_args()

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    matches = [a for a in data["artifacts"] if a["id"] == args.artifact_id]
    if not matches:
        print(f"ERROR: artifact id not found: {args.artifact_id}", file=sys.stderr)
        return 2

    art = matches[0]
    actual_zip_sha = sha256_file(args.zipfile)
    expected_zip_sha = art["zip_sha256"]
    print(f"ZIP SHA-256: {actual_zip_sha}")
    if actual_zip_sha != expected_zip_sha:
        print(f"ERROR: expected {expected_zip_sha}", file=sys.stderr)
        return 1

    expected_members = {m["path"]: m for m in art.get("members", [])}
    if not expected_members:
        print("ZIP identity matches. No member manifest recorded for this artifact.")
        return 0

    with zipfile.ZipFile(args.zipfile, "r") as zf:
        actual_names = set(zf.namelist())
        expected_names = set(expected_members)

        if actual_names != expected_names:
            print("ERROR: ZIP member set differs", file=sys.stderr)
            print(" missing:", sorted(expected_names - actual_names), file=sys.stderr)
            print(" extra:", sorted(actual_names - expected_names), file=sys.stderr)
            return 1

        for name in sorted(expected_names):
            payload = zf.read(name)
            exp = expected_members[name]
            actual_size = len(payload)
            actual_sha = sha256_bytes(payload)
            ok = actual_size == exp["size"] and actual_sha == exp["sha256"]
            print(f"{name}: size={actual_size} sha256={actual_sha} {'OK' if ok else 'FAIL'}")
            if not ok:
                return 1

    print("PASS: exact golden artifact verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
