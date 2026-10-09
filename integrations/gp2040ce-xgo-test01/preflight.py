#!/usr/bin/env python3
"""Read-only preflight for the pinned GP2040-CE XGO overlay.
Usage: python preflight.py /path/to/GP2040-CE
Does not modify checkout or produce firmware.
"""
from pathlib import Path
import subprocess
import sys

PIN = "3d1f32f7d02d418826b725b60208278d3be878c3"
root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
checks = {
    "proto/enums.proto": [
        "    INPUT_MODE_SINPUT = 17;",
        "    BUTTON_LAYOUT_STICK = 0;",
        "    BUTTON_LAYOUT_FIGHTBOARD = 14;",
    ],
    "src/drivermanager.cpp": [
        '#include "drivers/sinput/SInputDriver.h"',
        "        case INPUT_MODE_SINPUT:\n            driver = new SInputDriver();\n            break;",
    ],
    "CMakeLists.txt": ["src/drivers/sinput/SInputDriver.cpp"],
    "src/gp2040.cpp": [
        "const tusb_rhport_init_t dev_init = { .role = TUSB_ROLE_DEVICE, .speed = TUSB_SPEED_AUTO };\n\ttusb_init(TUD_OPT_RHPORT, &dev_init);",
        "\t\ttud_task();",
    ],
    "configs/Pico/BoardConfig.h": [
        '#define BOARD_CONFIG_LABEL "Pico"',
        "#define BUTTON_LAYOUT BUTTON_LAYOUT_STICKLESS",
        "#define BUTTON_LAYOUT_RIGHT BUTTON_LAYOUT_STICKLESSB",
        "#define HAS_I2C_DISPLAY 1",
        "#define I2C0_PIN_SDA 0",
        "#define I2C0_PIN_SCL 1",
    ],
    "headers/display/ui/screens/MainMenuScreen.h": [
        '#define INPUT_MODE_SINPUT_NAME "SInput"',
    ],
    "headers/gpdriver.h": [
        "virtual void initialize() = 0;",
        "virtual bool process(Gamepad * gamepad) = 0;",
        "virtual USBListener * get_usb_auth_listener() = 0;",
    ],
}
errors = []
if not (root / ".git").exists():
    errors.append("missing upstream .git checkout")
else:
    sha = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True)
    if sha.returncode or sha.stdout.strip() != PIN:
        errors.append(f"revision mismatch: {sha.stdout.strip()}")
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True)
    if status.returncode or status.stdout.strip():
        errors.append("upstream checkout is dirty")
for path, anchors in checks.items():
    file = root / path
    if not file.is_file():
        errors.append(f"missing: {path}")
        continue
    source = file.read_text()
    for anchor in anchors:
        count = source.count(anchor)
        if count != 1:
            errors.append(f"{path}: expected exactly one occurrence, got {count}: {anchor[:70]!r}")
if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)
print("PASS: pinned revision, clean checkout, driver interface, display wiring and overlay anchors")
print("NOT BUILT: run apply.py and compile before any hardware flash")
