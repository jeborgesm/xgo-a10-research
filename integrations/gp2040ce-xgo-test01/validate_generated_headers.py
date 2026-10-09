#!/usr/bin/env python3
"""Fail fast if XGO overlay emits malformed Pico / OLED preprocessor lines."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else None
if root is None:
    raise SystemExit("usage: validate_generated_headers.py GP2040_CE_ROOT")

checks = {
    "configs/Pico/BoardConfig.h": {
        "BOARD_CONFIG_LABEL": '"Pico"',
        "DEFAULT_INPUT_MODE": "INPUT_MODE_XGO",
        "BUTTON_LAYOUT": "BUTTON_LAYOUT_STICK",
        "BUTTON_LAYOUT_RIGHT": "BUTTON_LAYOUT_FIGHTBOARD",
    },
    "headers/display/ui/screens/MainMenuScreen.h": {
        "INPUT_MODE_SINPUT_NAME": '"SInput"',
        "INPUT_MODE_XGO_NAME": '"XGO"',
    },
}
problems = []
for rel, expected in checks.items():
    path = root / rel
    if not path.is_file():
        problems.append(f"{rel}: missing file")
        continue
    source = path.read_text()
    for number, line in enumerate(source.splitlines(), 1):
        if re.search(r"\[nr](?=\s*#)", line):
            problems.append(f"{rel}:{number}: literal escaped newline before directive")
        if re.search(r"#define\s+\w+.*#define", line):
            problems.append(f"{rel}:{number}: multiple defines on one line")
    for macro, value in expected.items():
        pattern = rf"^\s*#define\s+{re.escape(macro)}\s+{re.escape(value)}\s*$"
        if len(re.findall(pattern, source, flags=re.MULTILINE)) != 1:
            problems.append(f"{rel}: expected exactly one standalone #define {macro} {value}")

if problems:
    raise SystemExit("XGO generated-header validation FAILED:\n" + "\n".join(problems))
print("XGO generated-header validation passed.")
