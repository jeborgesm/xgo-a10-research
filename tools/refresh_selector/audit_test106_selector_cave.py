#!/usr/bin/env python3
"""Audit the reserved Refresh Games selector cave against an XGO bisrv.asd."""
from pathlib import Path
import hashlib, sys

BASE=0x80000000
EXPECTED_SHA="b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e"
START=0x80A389B8
END=0x80A391F8
EXPECTED_REGION_SHA="80b67b115f8e28f3b67fddcd4cd1daac24a054603d1dd0cb13793a299a5dadfc"

def main(path):
    data=Path(path).read_bytes()
    sha=hashlib.sha256(data).hexdigest()
    if sha != EXPECTED_SHA:
        raise SystemExit(f"FAIL baseline SHA: {sha}")
    region=data[START-BASE:END-BASE]
    rsha=hashlib.sha256(region).hexdigest()
    if len(region)!=(END-START):
        raise SystemExit("FAIL truncated cave")
    if any(region):
        raise SystemExit("FAIL cave is not all zero")
    if rsha != EXPECTED_REGION_SHA:
        raise SystemExit(f"FAIL cave SHA: {rsha}")
    print(f"PASS baseline {sha}")
    print(f"PASS cave {START:#010x}..{END:#010x} ({len(region)} bytes)")
    print(f"PASS cave sha256 {rsha}")

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: audit_test106_selector_cave.py bisrv.asd")
    main(sys.argv[1])
