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
  <out>/ROMS/fceumm;<rom-name>.gba   (zero-byte launch token)
  <out>/ROMS/fceumm/README-STUB.txt
  <out>/XGO-FCEUMM-MANIFEST.txt

The firmware patching itself is delegated to build_probe_asd.py so all exact
firmware fingerprint, zero-window, dispatch-JAL and GP-patch guards remain the
single source of truth.

The zero-byte launch token is intentional. Static disassembly confirms that the
XGO User Games scanner classifies entries by filename/extension without testing
file size, and run_game() dispatches GBA-family paths to the patched call site
without opening or reading the selected .gba file.
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
DEFAULT_ROM_NAME = "ScienceFrog.nes"


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


def validate_rom_name(name: str) -> str:
    if not name or name in {".", ".."}:
        raise SystemExit("Refusing to stage: ROM name must be a filename")
    if "/" in name or "\\" in name or ";" in name:
        raise SystemExit(
            "Refusing to stage: --rom-name must be one filename with no path separators or ';'"
        )
    if name.lower().endswith(".gba"):
        raise SystemExit(
            "Refusing to stage: --rom-name is the REAL NES filename; do not give it the synthetic .gba suffix"
        )
    if len(name.encode("utf-8")) > 220:
        raise SystemExit("Refusing to stage: ROM filename is too long for a conservative XGO path")
    return name


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("stock_asd", type=Path)
    ap.add_argument("loader_bin", type=Path)
    ap.add_argument("core_xgc", type=Path)
    ap.add_argument("output_dir", type=Path)
    ap.add_argument(
        "--rom-name",
        default=DEFAULT_ROM_NAME,
        help=(
            "real NES filename expected under ROMS/fceumm; a matching zero-byte "
            f"launch token is generated in ROMS (default: {DEFAULT_ROM_NAME!r})"
        ),
    )
    args = ap.parse_args()
    rom_name = validate_rom_name(args.rom_name)

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
    cores_dir = args.output_dir / "cores" / "fceumm"
    roms_root = args.output_dir / "ROMS"
    real_rom_dir = roms_root / "fceumm"
    bios_dir.mkdir(parents=True)
    cores_dir.mkdir(parents=True)
    real_rom_dir.mkdir(parents=True)

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

    core_out = cores_dir / "core.xgc"
    shutil.copyfile(args.core_xgc, core_out)

    # Browser-visible token belongs in the ROMS directory being scanned. Its
    # contents are deliberately empty; only the filename/path reaches the hook.
    token_name = f"fceumm;{rom_name}.gba"
    token_path = roms_root / token_name
    token_path.touch(exist_ok=False)

    real_rom_path = real_rom_dir / rom_name
    stub_note = real_rom_dir / "README-STUB.txt"
    stub_note.write_text(
        "XGO FCEUmm first-hardware-test launch contract\n"
        "===============================================\n\n"
        f"This staging bundle created the zero-byte browser token:\n\n"
        f"  /ROMS/{token_name}\n\n"
        f"Place ONE known-good NES ROM at exactly:\n\n"
        f"  /ROMS/fceumm/{rom_name}\n\n"
        "Do not put NES bytes into the .gba token and do not rename the real ROM\n"
        "to .gba. Static disassembly confirms that XGO's User Games scanner uses\n"
        "the token filename/extension only, and run_game() reaches the patched\n"
        "GBA dispatch call without opening or reading the token. The bridge then\n"
        "removes only the final synthetic .gba suffix and opens the real path.\n",
        encoding="utf-8",
    )

    manifest = args.output_dir / "XGO-FCEUMM-MANIFEST.txt"
    manifest.write_text(
        "XGO FCEUmm disposable-SD staging manifest\n"
        "========================================\n\n"
        f"stock bisrv SHA-256  : {stock_hash}\n"
        f"loader SHA-256       : {sha256_file(args.loader_bin)}\n"
        f"patched bisrv SHA-256: {sha256_file(patched_asd)}\n"
        f"core.xgc SHA-256     : {sha256_file(core_out)}\n"
        f"launch token         : /ROMS/{token_name}\n"
        f"launch token bytes   : {token_path.stat().st_size}\n"
        f"real ROM expected    : /ROMS/fceumm/{rom_name}\n\n"
        f"XGOC load            : 0x{xgoc['load']:08x}\n"
        f"XGOC entry           : 0x{xgoc['entry']:08x}\n"
        f"XGOC entry offset    : 0x{xgoc['entry_offset']:x}\n"
        f"XGOC payload         : {xgoc['payload_size']} bytes\n"
        f"XGOC runtime         : {xgoc['memory_size']} bytes\n"
        f"XGOC zero tail       : {xgoc['zero_tail']} bytes\n"
        f"XGOC payload CRC32   : 0x{xgoc['payload_crc']:08x}\n"
        f"XGOC header CRC32    : 0x{xgoc['header_crc']:08x}\n\n"
        "Safety model:\n"
        "- SD-loaded bisrv.asd only\n"
        "- no Firmware.upk\n"
        "- no SPI-NOR write path\n"
        "- exact stock firmware fingerprint required\n"
        "- XGOC header and payload CRCs verified before staging\n"
        "- output directory must be new/empty\n"
        "- generated .gba token is zero bytes by design\n"
        "- no game ROM copied or modified by this tool\n",
        encoding="utf-8",
    )

    print(f"staged: {args.output_dir}")
    print(f"  patched ASD: {patched_asd}")
    print(f"  core:        {core_out}")
    print(f"  token:       {token_path} (0 bytes)")
    print(f"  real ROM:    {real_rom_path} (user supplies this file)")
    print(f"  manifest:    {manifest}")


if __name__ == "__main__":
    main()
