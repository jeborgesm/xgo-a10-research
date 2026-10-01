#!/usr/bin/env python3
"""Stock XGO Arcade ZFB reference-wrapper codec.

Evidence: four stock XGO samples spanning CPS1/CPS2/IGS/NeoGeo.
This module deliberately does not classify Arcade family; family identity
belongs to the selected catalog/list descriptor, not to ZFB bytes.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PREVIEW_WIDTH = 144
PREVIEW_HEIGHT = 208
PREVIEW_BYTES = PREVIEW_WIDTH * PREVIEW_HEIGHT * 2  # 0xEA00
SEPARATOR = b"\x00" * 4
TRAILER = b"\x00" * 2


@dataclass(frozen=True)
class ZfbRecord:
    preview_rgb565le: bytes
    driver_zip: str


def validate_driver_zip(name: str) -> bytes:
    if not name or "/" in name or "\\" in name:
        raise ValueError("driver ZIP must be a basename")
    if not name.lower().endswith(".zip"):
        raise ValueError("driver ZIP must end in .zip")
    try:
        raw = name.encode("ascii")
    except UnicodeEncodeError as exc:
        raise ValueError("driver ZIP basename must be ASCII") from exc
    if b"\x00" in raw:
        raise ValueError("driver ZIP basename contains NUL")
    return raw


def build_zfb(preview_rgb565le: bytes, driver_zip: str) -> bytes:
    if len(preview_rgb565le) != PREVIEW_BYTES:
        raise ValueError(
            f"preview must be exactly {PREVIEW_BYTES} bytes "
            f"({PREVIEW_WIDTH}x{PREVIEW_HEIGHT} RGB565LE)"
        )
    driver = validate_driver_zip(driver_zip)
    return preview_rgb565le + SEPARATOR + driver + TRAILER


def parse_zfb(blob: bytes) -> ZfbRecord:
    if len(blob) < PREVIEW_BYTES + len(SEPARATOR) + len(".zip") + len(TRAILER):
        raise ValueError("ZFB is too short")
    if blob[PREVIEW_BYTES:PREVIEW_BYTES + 4] != SEPARATOR:
        raise ValueError("missing four-byte ZFB separator")
    tail = blob[PREVIEW_BYTES + 4:]
    if not tail.endswith(TRAILER):
        raise ValueError("missing two-byte ZFB trailer")
    driver_raw = tail[:-2]
    if not driver_raw or b"\x00" in driver_raw:
        raise ValueError("invalid driver field")
    try:
        driver = driver_raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("driver field is not ASCII") from exc
    validate_driver_zip(driver)
    expected = PREVIEW_BYTES + 4 + len(driver_raw) + 2
    if len(blob) != expected:
        raise ValueError("unexpected bytes in ZFB record")
    return ZfbRecord(blob[:PREVIEW_BYTES], driver)


def build_from_preview_file(preview_path: Path, driver_zip: str, out_path: Path) -> None:
    out_path.write_bytes(build_zfb(preview_path.read_bytes(), driver_zip))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("preview_rgb565")
    ap.add_argument("driver_zip")
    ap.add_argument("output_zfb")
    a = ap.parse_args()
    build_from_preview_file(Path(a.preview_rgb565), a.driver_zip, Path(a.output_zfb))
