#!/usr/bin/env python3
"""Stage the first native-SNES Snes9x2005 hardware-test overlay for XGO.

The selected .sfc/.smc file is still discovered, opened and preloaded by stock
run_game(); only the subsequent stock run_snes() call is redirected.

This tool is SD-only. It never writes a mounted card directly, never creates
Firmware.upk and never touches SPI NOR.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import struct
import subprocess
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASD_BUILDER = HERE / "build_native_snes_asd.py"

STOCK_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
CANONICAL_LOADER_SHA256 = "35b05a11d00565493210698d245c1c54d965c08ec3cfb461c00b07e0781cade4"
CANONICAL_CORE_SHA256 = "ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf"
CANONICAL_PATCHED_ASD_SHA256 = "d26951d932dc4788b5a5e95ed162c9d89d73dfe5e0b9cb757192aff755e1654f"

XGOC_MAGIC = b"XGOC"
XGOC_VERSION = 1
XGOC_HEADER_SIZE = 32
XGOC_LOAD_ADDR = 0x87000000
XGOC_MAX_END = 0x87CDAE00


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def ensure_new_output(path: Path) -> None:
    if path.exists():
        if not path.is_dir() or any(path.iterdir()):
            raise SystemExit(f"Refusing to stage into non-empty path: {path}")
    else:
        path.mkdir(parents=True)


def parse_xgoc(path: Path) -> dict[str, int]:
    raw = path.read_bytes()
    if len(raw) < XGOC_HEADER_SIZE:
        raise SystemExit("Refusing to stage: XGOC shorter than 32-byte header")

    magic, vh, load, entry_off, payload_size, memory_size, payload_crc, header_crc =         struct.unpack_from("<4s7I", raw, 0)
    version = vh & 0xFFFF
    header_size = vh >> 16

    checks = [
        (magic == XGOC_MAGIC, f"bad XGOC magic {magic!r}"),
        (version == XGOC_VERSION, f"XGOC version {version} != {XGOC_VERSION}"),
        (header_size == XGOC_HEADER_SIZE, f"XGOC header size {header_size} != 32"),
        (load == XGOC_LOAD_ADDR, f"XGOC load 0x{load:08x} != 0x{XGOC_LOAD_ADDR:08x}"),
        (payload_size > 0, "empty XGOC payload"),
        (memory_size >= payload_size, "XGOC runtime smaller than payload"),
        (entry_off < payload_size, "XGOC entry outside file-backed payload"),
        (load + memory_size <= XGOC_MAX_END, "XGOC runtime exceeds reserved core window"),
        (len(raw) == header_size + payload_size, "XGOC file length mismatch"),
        ((zlib.crc32(raw[:28]) & 0xFFFFFFFF) == header_crc, "XGOC header CRC mismatch"),
        ((zlib.crc32(raw[header_size:]) & 0xFFFFFFFF) == payload_crc, "XGOC payload CRC mismatch"),
    ]
    for ok, message in checks:
        if not ok:
            raise SystemExit(f"Refusing to stage: {message}")

    return {
        "load": load,
        "entry": load + entry_off,
        "entry_offset": entry_off,
        "payload_size": payload_size,
        "memory_size": memory_size,
        "zero_tail": memory_size - payload_size,
        "payload_crc": payload_crc,
        "header_crc": header_crc,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stock_asd", type=Path)
    ap.add_argument("loader_bin", type=Path)
    ap.add_argument("core_xgc", type=Path)
    ap.add_argument("output_dir", type=Path)
    args = ap.parse_args()

    for p, label in (
        (args.stock_asd, "stock ASD"),
        (args.loader_bin, "native SNES loader"),
        (args.core_xgc, "Snes9x2005 XGOC"),
        (ASD_BUILDER, "native SNES ASD builder"),
    ):
        if not p.is_file():
            raise SystemExit(f"Missing {label}: {p}")

    stock_hash = sha256_file(args.stock_asd)
    loader_hash = sha256_file(args.loader_bin)
    core_hash = sha256_file(args.core_xgc)

    if stock_hash != STOCK_SHA256:
        raise SystemExit(f"Refusing stock ASD SHA-256 {stock_hash}")
    if loader_hash != CANONICAL_LOADER_SHA256:
        raise SystemExit(f"Refusing non-canonical SNES loader SHA-256 {loader_hash}")
    if core_hash != CANONICAL_CORE_SHA256:
        raise SystemExit(f"Refusing non-canonical SNES XGOC SHA-256 {core_hash}")

    loader_size = args.loader_bin.stat().st_size
    if loader_size != 1359:
        raise SystemExit(f"Refusing loader size {loader_size}; expected 1359")

    xgoc = parse_xgoc(args.core_xgc)
    ensure_new_output(args.output_dir)

    bios_dir = args.output_dir / "bios"
    core_dir = args.output_dir / "cores" / "snes9x2005"
    bios_dir.mkdir(parents=True)
    core_dir.mkdir(parents=True)

    patched_asd = bios_dir / "bisrv.asd"
    subprocess.run(
        [sys.executable, str(ASD_BUILDER), str(args.stock_asd),
         str(args.loader_bin), str(patched_asd)],
        check=True,
    )

    patched_hash = sha256_file(patched_asd)
    if patched_hash != CANONICAL_PATCHED_ASD_SHA256:
        raise SystemExit(
            f"Generated ASD SHA-256 {patched_hash} != canonical "
            f"{CANONICAL_PATCHED_ASD_SHA256}"
        )

    core_out = core_dir / "core.xgc"
    shutil.copyfile(args.core_xgc, core_out)

    manifest = args.output_dir / "XGO-NATIVE-SNES-MANIFEST.txt"
    manifest.write_text(
        "XGO native SNES / Snes9x2005 Core #2 hardware-test overlay\n"
        "=========================================================\n\n"
        f"stock bisrv.asd SHA-256   : {stock_hash}\n"
        f"patched bisrv.asd SHA-256 : {patched_hash}\n"
        f"native loader SHA-256      : {loader_hash}\n"
        f"native loader bytes         : {loader_size}\n"
        f"core.xgc SHA-256            : {core_hash}\n"
        f"load                         : 0x{xgoc['load']:08x}\n"
        f"entry                        : 0x{xgoc['entry']:08x}\n"
        f"payload bytes                : {xgoc['payload_size']}\n"
        f"runtime bytes                : {xgoc['memory_size']}\n"
        f"zero-filled tail             : {xgoc['zero_tail']}\n"
        f"payload CRC-32               : 0x{xgoc['payload_crc']:08x}\n"
        f"header CRC-32                : 0x{xgoc['header_crc']:08x}\n\n"
        "firmware patch site         : 0x80360e40 / ASD 0x00360e40\n"
        "stock target                : run_snes @ 0x8035f9d8\n"
        "injected loader             : 0x80001500\n"
        "core path                   : /mnt/sda1/cores/snes9x2005/core.xgc\n"
        "XGO family profile          : 0x08 / native SNES / 11025 Hz\n"
    )

    readme = args.output_dir / "README-HARDWARE-TEST.txt"
    readme.write_text(
        "XGO native SNES / Snes9x2005 Core #2 hardware test\n"
        "===================================================\n\n"
        "1. Use only a disposable clone of the exact known-good XGO SD card.\n"
        "2. Keep an untouched bootable card available.\n"
        "3. Copy this overlay onto the disposable card, preserving paths.\n"
        "4. Do not create or install Firmware.upk; this experiment is SD-only.\n"
        "5. Launch a normal known-good .sfc/.smc ROM from the stock SNES browser.\n\n"
        "Stock run_game() still preloads the selected ROM. At the normal run_snes\n"
        "call the patched JAL enters the guarded loader, which validates the XGOC,\n"
        "reserves upper RAM, zeros BSS, repairs IRQ $gp, flushes caches and enters\n"
        "external Snes9x2005. Pre-entry failures fall back to untouched run_snes.\n"
    )

    print(f"staged native SNES overlay: {args.output_dir}")
    print(f"patched ASD SHA-256        : {patched_hash}")
    print(f"core XGOC SHA-256          : {core_hash}")
    print(f"core payload/runtime       : {xgoc['payload_size']} / {xgoc['memory_size']} bytes")


if __name__ == "__main__":
    main()
