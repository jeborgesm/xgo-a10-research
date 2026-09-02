#!/usr/bin/env python3
"""Stage a guarded XGO FCEUmm disposable-SD experiment.

This tool does not touch a mounted SD card directly, does not create
Firmware.upk, and does not copy any game ROM. It builds a staging DIRECTORY
that can be inspected before anything is placed on physical media.

Inputs:
  - exact stock XGO bisrv.asd
  - already-built injected loader binary
  - validated XGOC FCEUmm core image

Outputs:
  <out>/bios/bisrv.asd
  <out>/cores/fceumm/core.xgc
  <out>/ROMS/fceumm/README-STUB.txt
  <out>/XGO-FCEUMM-MANIFEST.txt

The firmware patching itself is delegated to build_probe_asd.py so all exact
firmware fingerprint, zero-window, dispatch-JAL and GP-patch guards remain the
single source of truth.
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
PROBE_DIR = HERE / "probe"
ASD_BUILDER = PROBE_DIR / "build_probe_asd.py"

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


def parse_xgoc(path: Path) -> dict[str, int]:
    raw = path.read_bytes()
    if len(raw) < XGOC_HEADER_SIZE:
        raise SystemExit("Refusing to stage: XGOC file is shorter than 32-byte header")

    magic, vh, load, entry_off, payload_size, memory_size, payload_crc, header_crc = \
        struct.unpack_from("<4s7I", raw, 0)
    version = vh & 0xFFFF
    header_size = vh >> 16

    if magic != XGOC_MAGIC:
        raise SystemExit(f"Refusing to stage: bad XGOC magic {magic!r}")
    if version != XGOC_VERSION or header_size != XGOC_HEADER_SIZE:
        raise SystemExit(
            f"Refusing to stage: XGOC version/header is {version}/{header_size}, "
            f"expected {XGOC_VERSION}/{XGOC_HEADER_SIZE}"
        )
    if load != XGOC_LOAD_ADDR:
        raise SystemExit(f"Refusing to stage: XGOC load address is 0x{load:08x}")
    if payload_size == 0 or memory_size < payload_size:
        raise SystemExit("Refusing to stage: invalid XGOC payload/runtime sizes")
    if load + memory_size > XGOC_MAX_END:
        raise SystemExit("Refusing to stage: XGOC runtime exceeds reserved core window")
    if entry_off >= payload_size:
        raise SystemExit("Refusing to stage: XGOC entry is outside file-backed payload")
    if len(raw) != header_size + payload_size:
        raise SystemExit(
            f"Refusing to stage: XGOC file length {len(raw)} does not equal "
            f"header+payload {header_size + payload_size}"
        )

    calc_header_crc = zlib.crc32(raw[:28]) & 0xFFFFFFFF
    calc_payload_crc = zlib.crc32(raw[header_size:]) & 0xFFFFFFFF
    if calc_header_crc != header_crc:
        raise SystemExit(
            f"Refusing to stage: XGOC header CRC mismatch "
            f"0x{calc_header_crc:08x} != 0x{header_crc:08x}"
        )
    if calc_payload_crc != payload_crc:
        raise SystemExit(
            f"Refusing to stage: XGOC payload CRC mismatch "
            f"0x{calc_payload_crc:08x} != 0x{payload_crc:08x}"
        )

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


def ensure_empty_output(path: Path) -> None:
    if path.exists():
        if any(path.iterdir()) if path.is_dir() else True:
            raise SystemExit(
                f"Refusing to stage into non-empty/existing path: {path}\n"
                "Use a new disposable staging directory."
            )
    else:
        path.mkdir(parents=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stock_asd", type=Path)
    ap.add_argument("loader_bin", type=Path)
    ap.add_argument("core_xgc", type=Path)
    ap.add_argument("output_dir", type=Path)
    args = ap.parse_args()

    for p, label in (
        (args.stock_asd, "stock ASD"),
        (args.loader_bin, "loader binary"),
        (args.core_xgc, "XGOC core"),
        (ASD_BUILDER, "ASD builder"),
    ):
        if not p.is_file():
            raise SystemExit(f"Missing {label}: {p}")

    stock_hash = sha256_file(args.stock_asd)
    if stock_hash != STOCK_SHA256:
        raise SystemExit(
            f"Refusing to stage: stock ASD SHA-256 {stock_hash} != {STOCK_SHA256}"
        )

    xgoc = parse_xgoc(args.core_xgc)
    ensure_empty_output(args.output_dir)

    bios_dir = args.output_dir / "bios"
    core_dir = args.output_dir / "cores" / "fceumm"
    rom_dir = args.output_dir / "ROMS" / "fceumm"
    bios_dir.mkdir(parents=True)
    core_dir.mkdir(parents=True)
    rom_dir.mkdir(parents=True)

    patched_asd = bios_dir / "bisrv.asd"
    subprocess.run(
        [
            sys.executable,
            str(ASD_BUILDER),
            str(args.stock_asd),
            str(args.loader_bin),
            str(patched_asd),
            "--family",
            "gba",
        ],
        check=True,
    )

    shutil.copyfile(args.core_xgc, core_dir / "core.xgc")

    stub_note = rom_dir / "README-STUB.txt"
    stub_note.write_text(
        "XGO FCEUmm first-hardware-test launch contract\n"
        "===============================================\n\n"
        "Place ONE known-good NES ROM in this directory. Example:\n\n"
        "  /ROMS/fceumm/ScienceFrog.nes\n\n"
        "The stock GBA dispatch token must have the basename:\n\n"
        "  fceumm;ScienceFrog.nes.gba\n\n"
        "The final .gba suffix is synthetic and is removed by the external-core\n"
        "bridge. Do not rename the real NES ROM to .gba. This staging tool does\n"
        "not fabricate the stub file yet because stock-browser handling of an\n"
        "empty/minimal GBA file is still being validated separately.\n",
        encoding="utf-8",
    )

    manifest = args.output_dir / "XGO-FCEUMM-MANIFEST.txt"
    manifest.write_text(
        "XGO FCEUmm disposable-SD staging manifest\n"
        "========================================\n\n"
        f"stock bisrv SHA-256 : {stock_hash}\n"
        f"loader SHA-256      : {sha256_file(args.loader_bin)}\n"
        f"patched bisrv SHA-256: {sha256_file(patched_asd)}\n"
        f"core.xgc SHA-256    : {sha256_file(core_dir / 'core.xgc')}\n\n"
        f"XGOC load           : 0x{xgoc['load']:08x}\n"
        f"XGOC entry          : 0x{xgoc['entry']:08x}\n"
        f"XGOC entry offset   : 0x{xgoc['entry_offset']:x}\n"
        f"XGOC payload        : {xgoc['payload_size']} bytes\n"
        f"XGOC runtime        : {xgoc['memory_size']} bytes\n"
        f"XGOC zero tail      : {xgoc['zero_tail']} bytes\n"
        f"XGOC payload CRC32  : 0x{xgoc['payload_crc']:08x}\n"
        f"XGOC header CRC32   : 0x{xgoc['header_crc']:08x}\n\n"
        "Safety model:\n"
        "- SD-loaded bisrv.asd only\n"
        "- no Firmware.upk\n"
        "- no SPI-NOR write path\n"
        "- exact stock firmware fingerprint required\n"
        "- XGOC header and payload CRCs verified before staging\n"
        "- output directory must be new/empty\n"
        "- no game ROM copied or modified by this tool\n",
        encoding="utf-8",
    )

    print(f"staged: {args.output_dir}")
    print(f"  patched ASD: {patched_asd}")
    print(f"  core:        {core_dir / 'core.xgc'}")
    print(f"  manifest:    {manifest}")
    print("  ROM/stub:    see ROMS/fceumm/README-STUB.txt")


if __name__ == "__main__":
    main()
