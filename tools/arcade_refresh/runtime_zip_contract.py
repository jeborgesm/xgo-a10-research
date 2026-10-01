#!/usr/bin/env python3
"""Reference model for Arcade runtime-ZIP placement and verification.

The runtime implementation should mirror this contract with bounded buffers:
never overwrite /ARCADE/bin/<driver>.zip when a same-name file differs.
"""
from __future__ import annotations
from enum import Enum, auto
from pathlib import Path
import shutil

CHUNK = 0x2000

class ZipResult(Enum):
    CREATED = auto()
    REUSED = auto()
    COLLISION = auto()
    FAILED = auto()

def files_identical(a: Path, b: Path) -> bool:
    try:
        if a.stat().st_size != b.stat().st_size:
            return False
        with a.open("rb") as fa, b.open("rb") as fb:
            while True:
                ba = fa.read(CHUNK)
                bb = fb.read(CHUNK)
                if ba != bb:
                    return False
                if not ba:
                    return True
    except OSError:
        return False

def ensure_runtime_zip(source: Path, destination: Path) -> ZipResult:
    if destination.exists():
        return ZipResult.REUSED if files_identical(source, destination) else ZipResult.COLLISION

    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Host reference only. Device worker must use stock file I/O wrappers
        # and exact-count checked 0x2000-byte transfers.
        with source.open("rb") as src, destination.open("xb") as dst:
            while True:
                block = src.read(CHUNK)
                if not block:
                    break
                if dst.write(block) != len(block):
                    return ZipResult.FAILED
        if not files_identical(source, destination):
            return ZipResult.FAILED
        return ZipResult.CREATED
    except FileExistsError:
        return ZipResult.REUSED if files_identical(source, destination) else ZipResult.COLLISION
    except OSError:
        return ZipResult.FAILED
