#!/usr/bin/env python3
"""Read-only Test14 structural regression checks; does not build or change firmware.

Usage: python3 audit_test14.py [applied-upstream-directory]
Checks the source overlay and, optionally, the generated upstream source.
These are static contracts, NOT hardware/timing proofs.
"""
from pathlib import Path
import re
import sys

overlay = Path(__file__).resolve().parent
upstream = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
failures = []
checks = 0

def check(condition, message):
    global checks
    checks += 1
    print(("PASS" if condition else "FAIL") + ": " + message)
    if not condition:
        failures.append(message)

def read(path):
    p = overlay / path
    if not p.is_file():
        failures.append(f"missing overlay: {path}")
        return ""
    return p.read_text()

driver = read("src/drivers/xgo/XGODriver.cpp")
header = read("headers/drivers/xgo/XGODriver.h")
apply = read("apply.py")
workflow = (overlay.parent.parent / ".github/workflows/gp2040ce-xgo-test01.yml")
# Actual repository root is two directories above integrations/gp2040ce-xgo-test01.
workflow = overlay.parents[1] / ".github/workflows/gp2040ce-xgo-test01.yml"
ci = workflow.read_text() if workflow.is_file() else ""

check("static void runResponder();" in header, "dedicated responder entrypoint exposed")
check("std::atomic<uint16_t> published_mask{0}" in driver, "single atomic 12-bit snapshot storage")
check("published_mask.store(snapshot, std::memory_order_release)" in driver, "producer release publication")
check("published_mask.load(std::memory_order_acquire)" in driver, "responder acquire snapshot")
check("void XGODriver::initialize() { /* USB PHY belongs exclusively to Core1 responder. */ }" in driver,
      "driver initialize does not reconfigure PHY on Core0")
check(re.search(r"void XGODriver::runResponder\(\)\s*\{\s*raw_init\(\);\s*while \(true\)", driver) is not None,
      "responder initializes PHY and runs continuously")
process = driver.split("bool XGODriver::process(Gamepad *gamepad)", 1)[-1]
check("emit_frame(" not in process and "raw_init(" not in process,
      "Core0 gamepad producer never performs PHY transactions")
check(all(f"1u << {i}" in driver for i in range(12)), "all 12 XGO button slots mapped")
check("save_and_disable_interrupts()" in driver and "restore_interrupts(irq_state)" in driver,
      "slot transfer has matched local interrupt masking")
check("USB_USBPHY_DIRECT_RX_DM_BITS" in driver and "USB_USBPHY_DIRECT_RX_DP_BITS" in driver,
      "XGO retains USB PHY direct clock/data acquisition")
check('if (xgoMode) gp2040Core1->setup();' in apply and
      'XGODriver::runResponder();' in apply and
      'if (xgoMode) xgo_aux_tick();' not in apply and
      'xgo_aux_tick();' in apply,
      "XGO Core0 auxiliary setup/tick and Core1 responder routing present")
check('if (DriverManager::getInstance().getInputMode() != INPUT_MODE_XGO) tud_task();' in apply and
      'if (DriverManager::getInstance().getInputMode() != INPUT_MODE_XGO) {' in apply,
      "native TinyUSB task/init gated off in XGO mode")
check('gp2040Core1->run();' in apply and 'multicore_launch_core1(core1);' in apply,
      "non-XGO Core1 scheduling retained")
check("INPUT_MODE_CONFIG" not in driver and "INPUT_MODE_XGO" in apply,
      "XGO driver does not claim Web Config USB stack")
check("audit_test14.py upstream" in ci, "CI invokes offline structural audit after overlay application")

if upstream is not None:
    def source(p):
        f = upstream / p
        if not f.is_file():
            failures.append(f"missing applied upstream: {p}")
            return ""
        return f.read_text()
    main = source("src/main.cpp")
    gp = source("src/gp2040.cpp")
    aux = source("src/gp2040aux.cpp")
    check("if (xgoMode) gp2040Core1->setup();" in main and
          "if (xgoMode) {" in main and "XGODriver::runResponder();" in main,
          "applied startup selects XGO responder after auxiliary setup")
    check("if (DriverManager::getInstance().getInputMode() == INPUT_MODE_XGO) xgo_aux_tick();" in gp,
          "applied Core0 loop ticks auxiliary add-ons only in XGO mode")
    check("void GP2040Aux::processOnce()" in aux and "processOnce();" in aux,
          "applied auxiliary cooperative tick exists")
    check("if (DriverManager::getInstance().getInputMode() != INPUT_MODE_XGO) tud_task();" in gp,
          "applied XGO mode avoids TinyUSB device task")

print(f"\nStatic audit: {checks - len(failures)}/{checks} assertions passed.")
print("NOT PROVEN: console waveform timing, flash-save safety, Web Config recovery,")
print("long-duration gameplay, input latency distribution, or non-XGO hardware regression.")
if failures:
    sys.exit(1)
