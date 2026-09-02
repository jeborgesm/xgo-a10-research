#!/usr/bin/env python3
"""Stage the native-NES FCEUmm hardware-test overlay for a disposable XGO SD.

Unlike the older semicolon/GBA external-core experiment, this path patches the
real NES dispatch inside run_game(). The selected .nes file is therefore
scanned, opened and preloaded by stock firmware exactly as before; only the
subsequent call to stock run_nes() is redirected to the native XGOC loader.

This tool does NOT copy a ROM, touch a mounted SD card directly, create a
Firmware.upk, or write SPI NOR. It creates an inspectable overlay directory:

  <out>/bios/bisrv.asd
  <out>/cores/fceumm/core.xgc
  <out>/XGO-NATIVE-NES-MANIFEST.txt
  <out>/README-HARDWARE-TEST.txt

Copy that overlay onto a disposable clone of the exact known XGO SD image, then
launch an ordinary known-good NES ROM from the normal NES browser. If loader or
core validation fails before external execution, the loader restores RAMSIZE
and calls the untouched stock run_nes() implementation.
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
ASD_BUILDER = HERE / "build_native_nes_asd.py"

STOCK_SHA256 = "869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf"
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

    magic, vh, load, entry_off, payload_size, memory_size, payload_crc, header_crc = \
        struct.unpack_from("<4s7I", raw, 0)
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
        (args.loader_bin, "native NES loader"),
        (args.core_xgc, "native FCEUmm XGOC"),
        (ASD_BUILDER, "native NES ASD builder"),
    ):
        if not p.is_file():
            raise SystemExit(f"Missing {label}: {p}")

    stock_hash = sha256_file(args.stock_asd)
    if stock_hash != STOCK_SHA256:
        raise SystemExit(
            f"Refusing to stage: stock ASD SHA-256 {stock_hash} != {STOCK_SHA256}"
        )

    loader_size = args.loader_bin.stat().st_size
    loader_capacity = 0x2180 - 0x1500
    if loader_size <= 0 or loader_size > loader_capacity:
        raise SystemExit(
            f"Refusing to stage: loader size {loader_size} exceeds {loader_capacity}-byte cave"
        )

    xgoc = parse_xgoc(args.core_xgc)
    ensure_new_output(args.output_dir)

    bios_dir = args.output_dir / "bios"
    core_dir = args.output_dir / "cores" / "fceumm"
    bios_dir.mkdir(parents=True)
    core_dir.mkdir(parents=True)

    patched_asd = bios_dir / "bisrv.asd"
    subprocess.run(
        [
            sys.executable,
            str(ASD_BUILDER),
            str(args.stock_asd),
            str(args.loader_bin),
            str(patched_asd),
        ],
        check=True,
    )

    core_out = core_dir / "core.xgc"
    shutil.copyfile(args.core_xgc, core_out)

    patched_hash = sha256_file(patched_asd)
    loader_hash = sha256_file(args.loader_bin)
    core_hash = sha256_file(core_out)

    manifest = args.output_dir / "XGO-NATIVE-NES-MANIFEST.txt"
    manifest.write_text(
        "XGO native NES / FCEUmm hardware-test overlay\n"
        "==============================================\n\n"
        "Patch generation\n"
        "----------------\n"
        f"stock bisrv.asd SHA-256 : {stock_hash}\n"
        f"patched bisrv.asd SHA-256: {patched_hash}\n"
        f"native loader SHA-256    : {loader_hash}\n"
        f"native loader bytes       : {loader_size}\n\n"
        "Core container\n"
        "--------------\n"
        f"core.xgc SHA-256          : {core_hash}\n"
        f"load                       : 0x{xgoc['load']:08x}\n"
        f"entry                      : 0x{xgoc['entry']:08x}\n"
        f"entry offset               : 0x{xgoc['entry_offset']:x}\n"
        f"payload bytes              : {xgoc['payload_size']}\n"
        f"runtime bytes              : {xgoc['memory_size']}\n"
        f"zero-filled tail           : {xgoc['zero_tail']}\n"
        f"payload CRC-32             : 0x{xgoc['payload_crc']:08x}\n"
        f"header CRC-32              : 0x{xgoc['header_crc']:08x}\n\n"
        "Native interception contract\n"
        "----------------------------\n"
        "firmware patch site          : 0x80360e20 / ASD 0x00360e20\n"
        "stock target                 : run_nes @ 0x8035f63c\n"
        "injected loader              : 0x80001500\n"
        "core path                    : /mnt/sda1/cores/fceumm/core.xgc\n"
    )

    readme = args.output_dir / "README-HARDWARE-TEST.txt"
    readme.write_text(
        "XGO native NES / FCEUmm first hardware test\n"
        "===========================================\n\n"
        "THIS IS THE NATIVE NES PATH. Do not use the older semicolon/GBA token\n"
        "procedure with this core.\n\n"
        "1. Use a disposable clone of the exact known-good XGO SD card.\n"
        "2. Preserve a second untouched bootable card for immediate recovery.\n"
        "3. Copy this overlay onto the disposable card, preserving paths.\n"
        "4. Do not create or install Firmware.upk; this experiment is SD-only.\n"
        "5. Boot normally and launch one small, known-good .nes ROM from the\n"
        "   console's ordinary NES browser. No renamed .gba token is needed.\n\n"
        "Expected control flow\n"
        "---------------------\n"
        "Stock run_game() still opens and preloads the selected NES ROM into the\n"
        "64 MiB gp_buf_64m arena. At the stock call to run_nes(), the patched JAL\n"
        "enters the injected loader. The loader validates /cores/fceumm/core.xgc,\n"
        "reserves upper RAM, reconstructs BSS, repairs the IRQ $gp path, flushes\n"
        "cache state, and calls the external core at 0x87000000. FCEUmm consumes\n"
        "the ROM that stock firmware already loaded.\n\n"
        "Guarded fallback\n"
        "----------------\n"
        "Before external execution, heap collision, missing/invalid core, short\n"
        "read, bad CRC, or invalid geometry restores RAMSIZE and calls untouched\n"
        "stock run_nes(). A crash after successful transfer is outside that\n"
        "fallback boundary and is exactly what this first device test is meant\n"
        "to characterize.\n"
    )

    print(f"staged native NES overlay: {args.output_dir}")
    print(f"patched ASD SHA-256       : {patched_hash}")
    print(f"core XGOC SHA-256         : {core_hash}")
    print(f"core payload/runtime      : {xgoc['payload_size']} / {xgoc['memory_size']} bytes")


if __name__ == "__main__":
    main()
