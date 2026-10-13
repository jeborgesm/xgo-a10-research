#!/usr/bin/env python3
"""Explicit Test17-only build overlay selector; does not modify source repo or golden files.
Usage: python3 build_test17_overlay.py /path/to/clean/pinned/gp2040-ce
Requires same upstream pin and preflight gates as apply.py.
"""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import hashlib

here = Path(__file__).resolve().parent
candidate = here / "candidates/test17-direct-gpio-offline/XGODriver.cpp"
original = here / "src/drivers/xgo/XGODriver.cpp"
target_rel = Path("src/drivers/xgo/XGODriver.cpp")
if len(sys.argv) != 2:
    raise SystemExit("Usage: build_test17_overlay.py /path/to/clean/pinned/gp2040-ce")
root = Path(sys.argv[1]).resolve()
if not candidate.is_file() or not original.is_file():
    raise SystemExit("STOP: missing candidate or original")
src = candidate.read_text()
assert "read_xgo_direct_mask()" in src and "const uint16_t mask = read_xgo_direct_mask();" in src
assert "published_mask.load" not in src
# Explicit staging of the whole overlay avoids modifying apply.py, the original
# driver, or any protected baseline. apply.py validates the upstream checkout.
with tempfile.TemporaryDirectory(prefix="xgo-test17-overlay-") as temp:
    stage = Path(temp) / "overlay"
    shutil.copytree(here, stage, ignore=shutil.ignore_patterns("*.uf2", "*.elf", "*.bin", "__pycache__"))
    shutil.copy2(candidate, stage / target_rel)
    if (stage / target_rel).read_bytes() != candidate.read_bytes():
        raise SystemExit("STOP: staged driver mismatch")
    print("TEST17 SOURCE SHA256", hashlib.sha256(candidate.read_bytes()).hexdigest(), flush=True)
    subprocess.run([sys.executable, str(stage / "apply.py"), str(root)], check=True)
    installed = root / target_rel
    if installed.read_bytes() != candidate.read_bytes():
        raise SystemExit("STOP: installed driver mismatch")
    print("TEST17 overlay applied; not built or validated. NEVER flash without further gates.")
