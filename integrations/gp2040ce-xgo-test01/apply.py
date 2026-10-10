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


for part in ["headers/drivers/xgo/XGODriver.h", "headers/drivers/xgo/XGODiagnostics.h", "src/drivers/xgo/XGODriver.cpp"]:
    dest = root / part
    dest.parent.mkdir(parents=True, exist_ok=True)
    require(not dest.exists(), f"refusing to overwrite {dest}")
    shutil.copy2(overlay / part, dest)


# XGO scheduler isolation: Core1 exclusively services the USB PHY. Core0
# continues GP2040 input processing AND runs auxiliary display/add-ons after
# publishing a coherent button mask. Non-XGO startup and Core1 remain stock.
replace_once("headers/gp2040aux.h",
             "    void run();             // loop core1",
             "    void run();             // loop core1\n    void processOnce();     // XGO: cooperative Core0 aux tick")
replace_once("src/gp2040aux.cpp",
             "void GP2040Aux::run() {\n\twhile (1) {",
             "void GP2040Aux::run() {\n\twhile (1) {\n        processOnce();\n    }\n}\n\nvoid GP2040Aux::processOnce() {\n    {")
replace_once("src/main.cpp",
             '#include "gp2040aux.h"',
             '#include "gp2040aux.h"\n#include "drivermanager.h"\n#include "drivers/xgo/XGODriver.h"')
replace_once("src/main.cpp",
             "static GP2040Aux * gp2040Core1 = nullptr;",
             "static GP2040Aux * gp2040Core1 = nullptr;\nstatic bool xgoMode = false;\nvoid xgo_aux_tick() { if (xgoMode) gp2040Core1->processOnce(); }")
replace_once("src/main.cpp",
             "\t// Create GP2040 w/ Additional Modules for Core 1\n\tgp2040Core1->setup();\n\tgp2040Core1->run();",
             "\tif (xgoMode) {\n\t\tXGODriver::runResponder();\n\t} else {\n\t\tgp2040Core1->setup();\n\t\tgp2040Core1->run();\n\t}")
replace_once("src/main.cpp",
             "\t// Create GP2040 Thread for Core1\n\tmulticore_launch_core1(core1);",
             "\t// XGO Core1 is reserved for the serial responder; move auxiliary\n\t// setup to Core0 so its OLED/add-ons never run on the responder.\n\txgoMode = DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO;\n\tif (xgoMode) gp2040Core1->setup();\n\t// Create GP2040 Thread for Core1\n\tmulticore_launch_core1(core1);")
replace_once("src/gp2040.cpp",
             "#include \"gp2040.h\"",
             "#include \"gp2040.h\"\nextern void xgo_aux_tick();")
replace_once("src/gp2040.cpp",
             "\t\taddons.PostprocessAddons(processed);",
             "\t\taddons.PostprocessAddons(processed);\n\t\tif (DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO) xgo_aux_tick();")

# Test05: capture raw state before processing, then processed state before output.
# Pack dpad in bits 16..23 and buttons in bits 0..15.
replace_once("src/gp2040.cpp", '#include "gp2040.h"\nextern void xgo_aux_tick();', '#include "gp2040.h"\nextern void xgo_aux_tick();\n#include "drivers/xgo/XGODiagnostics.h"')
replace_once("src/gp2040.cpp", '\t\tgamepad->read();', '\t\tgamepad->read();\n\t\tif (DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO)\n\t\t\txgo_diag_raw.store((uint32_t(gamepad->state.dpad) << 16) | (uint32_t(gamepad->state.buttons) & 0xffffu), std::memory_order_relaxed);')
replace_once("src/gp2040.cpp", '\t\tbool processed = inputDriver->process(gamepad);', '\t\tif (DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO)\n\t\t\txgo_diag_processed.store((uint32_t(gamepad->state.dpad) << 16) | (uint32_t(gamepad->state.buttons) & 0xffffu), std::memory_order_relaxed);\n\t\tbool processed = inputDriver->process(gamepad);')

# Test13: restore GP2040-CE's normal button layout and Input History.
# Keep diagnostics in the driver, but do not replace the user-facing OLED screen.
# XGO uses Xbox/XInput history labels (A/B/X/Y, LB/RB, LT/RT).
replace_once("headers/display/ui/screens/ButtonLayoutScreen.h",
             "            {INPUT_MODE_XINPUT, 2},",
             "            {INPUT_MODE_XINPUT, 2},\n            {INPUT_MODE_XGO, 2},")
replace_once("src/display/ui/screens/ButtonLayoutScreen.cpp",
             "            case INPUT_MODE_SINPUT: statusBar += \"SINPUT\"; break;",
             "            case INPUT_MODE_SINPUT: statusBar += \"SINPUT\"; break;\n            case INPUT_MODE_XGO: statusBar += \"XGO\"; break;")

# The Web Config frontend maintains its own mode list and translations.
# The firmware enum/driver alone cannot make XGO selectable in the browser.
replace_once("www/src/Data/InputBootModes.ts",
             "export const INPUT_MODE_OPTIONS: InputModeOptions[] = [",
             """export const INPUT_MODE_OPTIONS: InputModeOptions[] = [
    {
        labelKey: 'input-mode-options.xgo',
        value: InputMode.INPUT_MODE_XGO,
        group: 'primary',
        required: [],
        optional: [],
        authentication: [],
        deviceTypes: [],
    },""")
replace_once("www/src/Locales/en/SettingsPage.jsx",
             "\t\tps3: 'PS3',",
             "\t\tps3: 'PS3',\n\t\txgo: 'XGO (Caveman)',")

# Board-config decision: retain the stock Pico mapping, display and Web Config.
# GP2040_BOARDCONFIG=Pico is the correct first target; no stripped board overlay.
# USBHostManager uses PIO USB and is not the native TinyUSB device stack.
# Its compatibility with XGO and peripheral pin allocation remains an audit gate.

print("Overlay applied. NOT BUILT. Audit USB host, display and boot recovery before flashing.")
