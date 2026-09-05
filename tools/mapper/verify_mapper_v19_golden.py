#!/usr/bin/env python3
"""Verify the exact hardware-confirmed interactive mapper v19 card artifact."""

from __future__ import annotations
import argparse, hashlib, zipfile
from pathlib import Path

ZIP_SHA256 = "c45925f965cf86b4e1efc622b02aabb5545122814743aaf7723d4dbf6ba4ec81"
EXPECTED = {
    "README-MAPPER-V19.txt": (785, "79b9559e4871f637b3f5b858f4c76c4631eae7353821b04b2f808cb754cb8d16"),
    "Resources/gpapi.bvs": (614400, "759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8"),
    "bios/bisrv.asd": (12768452, "466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab"),
}

def h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("zip", type=Path)
    args=ap.parse_args()
    raw=args.zip.read_bytes()
    if h(raw) != ZIP_SHA256:
        raise SystemExit(f"wrong v19 ZIP hash: {h(raw)}")
    with zipfile.ZipFile(args.zip) as z:
        names=set(z.namelist())
        if names != set(EXPECTED):
            raise SystemExit(f"unexpected member set: {sorted(names)}")
        for name,(size,sha) in EXPECTED.items():
            data=z.read(name)
            if len(data) != size or h(data) != sha:
                raise SystemExit(f"member mismatch: {name}")
    print("interactive mapper v19 golden artifact verified")
    print(f"ZIP SHA-256: {ZIP_SHA256}")
    for name,(size,sha) in EXPECTED.items():
        print(f"{name}: {size} bytes {sha}")

if __name__ == "__main__":
    main()
