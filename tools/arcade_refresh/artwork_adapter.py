#!/usr/bin/env python3
"""Composition contract between the proven JPEG worker and Arcade ZFB codec.

This host-side adapter deliberately starts *after* JPEG decoding. Runtime JPEG
work must reuse the exact Test72/Test74/Test75 0x1F08 decoder tail.
"""
from pathlib import Path
from zfb_codec import PREVIEW_BYTES, build_zfb

BLACK_PREVIEW = b"\x00" * PREVIEW_BYTES

def compose_from_rgb565(preview: bytes | None, driver_zip: str) -> bytes:
    """Build an Arcade ZFB from proven-worker output or black fallback."""
    if preview is None:
        preview = BLACK_PREVIEW
    if len(preview) != PREVIEW_BYTES:
        raise ValueError("decoder output is not exact 144x208 RGB565LE")
    return build_zfb(preview, driver_zip)

def compose_files(rgb565_path: Path | None, driver_zip: str, out: Path) -> None:
    preview = None if rgb565_path is None else rgb565_path.read_bytes()
    out.write_bytes(compose_from_rgb565(preview, driver_zip))
