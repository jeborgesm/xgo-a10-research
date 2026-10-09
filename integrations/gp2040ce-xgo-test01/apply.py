#!/usr/bin/env python3
"""Apply XGO Test01 overlay to exact pinned GP2040-CE checkout.
Fail closed if expected upstream anchors change.
"""
from pathlib import Path
import shutil
import subprocess
import sys

PIN = "3d1f32f7d02d418826b725b60208278d3be878c3"
root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
overlay = Path(__file__).resolve().parent

def require(cond, msg):
    if not cond: raise SystemExit("STOP: " + msg)

require((root / "src/gp2040.cpp").exists(), "not a GP2040-CE checkout")
sha = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
require(sha == PIN, f"upstream revision mismatch: {sha}")
require(not subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"], text=True).strip(), "checkout is dirty")

# Validate all known upstream contracts BEFORE writing any file.
subprocess.run([sys.executable, str(overlay / "preflight.py"), str(root)], check=True)

def replace_once(path, old, new):
    p = root / path
    s = p.read_text()
    require(s.count(old) == 1, f"expected exactly one anchor in {path}: {old!r}")
    p.write_text(s.replace(old, new, 1))

# Retain stock Pico display, I2C and all arcade GPIO assignments.
# New installations default to XGO; existing saved inputMode settings may override it.
# Web Config recovery/entry still requires a separate validation gate.
replace_once("configs/Pico/BoardConfig.h",
             '#define BOARD_CONFIG_LABEL "Pico"',
             '#define BOARD_CONFIG_LABEL "Pico"\n#define DEFAULT_INPUT_MODE INPUT_MODE_XGO')

# Backup display layout (0.7.12): left 0 = STICK, right 14 = FIGHTBOARD.
# Both enum names and numeric values match the pinned upstream proto/enums.proto.
# Override only default macros, never stored settings or the stock Pico GPIO map.
replace_once("configs/Pico/BoardConfig.h",
             "#define BUTTON_LAYOUT BUTTON_LAYOUT_STICKLESS",
             "#define BUTTON_LAYOUT BUTTON_LAYOUT_STICK")
replace_once("configs/Pico/BoardConfig.h",
             "#define BUTTON_LAYOUT_RIGHT BUTTON_LAYOUT_STICKLESSB",
             "#define BUTTON_LAYOUT_RIGHT BUTTON_LAYOUT_FIGHTBOARD")

# The OLED mini-menu references INPUT_MODE_<enum>_NAME macros for every mode.
# Without a matching XGO label, protobuf compilation succeeds but gp2040aux.cpp fails.
replace_once("headers/display/ui/screens/MainMenuScreen.h",
             '#define INPUT_MODE_SINPUT_NAME "SInput"',
             '#define INPUT_MODE_SINPUT_NAME "SInput"\n#define INPUT_MODE_XGO_NAME "XGO"')

# Protobuf: keep CONFIG=255 unchanged.
replace_once("proto/enums.proto", "    INPUT_MODE_SINPUT = 17;", "    INPUT_MODE_SINPUT = 17;\n    INPUT_MODE_XGO = 18;")
replace_once("src/drivermanager.cpp", '#include "drivers/sinput/SInputDriver.h"', '#include "drivers/sinput/SInputDriver.h"\n#include "drivers/xgo/XGODriver.h"')
replace_once("src/drivermanager.cpp", "        case INPUT_MODE_SINPUT:\n            driver = new SInputDriver();\n            break;", "        case INPUT_MODE_SINPUT:\n            driver = new SInputDriver();\n            break;\n        case INPUT_MODE_XGO:\n            driver = new XGODriver();\n            break;")
replace_once("CMakeLists.txt", "src/drivers/sinput/SInputDriver.cpp", "src/drivers/sinput/SInputDriver.cpp\nsrc/drivers/xgo/XGODriver.cpp")

# The XGO driver initializes its PHY during GP2040::setup().
# In GP2040::run(), do not initialize the native USB device or call tud_task in XGO mode.
replace_once("src/gp2040.cpp", "const tusb_rhport_init_t dev_init = { .role = TUSB_ROLE_DEVICE, .speed = TUSB_SPEED_AUTO };\n\ttusb_init(TUD_OPT_RHPORT, &dev_init);",
"""if (DriverManager::getInstance().getInputMode() != INPUT_MODE_XGO) {
\t\tconst tusb_rhport_init_t dev_init = { .role = TUSB_ROLE_DEVICE, .speed = TUSB_SPEED_AUTO };
\t\ttusb_init(TUD_OPT_RHPORT, &dev_init);
\t}""")
replace_once("src/gp2040.cpp", "\t\ttud_task();", "\t\tif (DriverManager::getInstance().getInputMode() != INPUT_MODE_XGO) tud_task();")

for part in ["headers/drivers/xgo/XGODriver.h", "src/drivers/xgo/XGODriver.cpp"]:
    dest = root / part
    dest.parent.mkdir(parents=True, exist_ok=True)
    require(not dest.exists(), f"refusing to overwrite {dest}")
    shutil.copy2(overlay / part, dest)


# Board-config decision: retain the stock Pico mapping, display and Web Config.
# GP2040_BOARDCONFIG=Pico is the correct first target; no stripped board overlay.
# USBHostManager uses PIO USB and is not the native TinyUSB device stack.
# Its compatibility with XGO and peripheral pin allocation remains an audit gate.

print("Overlay applied. NOT BUILT. Audit USB host, display and boot recovery before flashing.")
