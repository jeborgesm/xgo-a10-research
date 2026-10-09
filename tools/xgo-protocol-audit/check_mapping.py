#!/usr/bin/env python3
"""Offline XGO slot mapping contract. Does not require hardware or alter firmware."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CAVEMAN = ROOT / "tools/rp2040-xgo-native-contra/main.c"
DRIVER = ROOT / "integrations/gp2040ce-xgo-test01/src/drivers/xgo/XGODriver.cpp"
SLOTS = ("R", "Y", "X", "L", "A", "B", "SELECT", "START", "UP", "DOWN", "LEFT", "RIGHT")
GP_INPUTS = ("R1", "B4", "B3", "L1", "B1", "B2", "S1", "S2", "Up", "Down", "Left", "Right")

def check():
    caveman = CAVEMAN.read_text()
    driver = DRIVER.read_text()
    for i, name in enumerate(GP_INPUTS):
        pattern = rf"pressed{name}\(\)\s*\?\s*1u\s*<<\s*{i}\s*:\s*0u"
        assert re.search(pattern, driver), f"missing/wrong GP mapping for slot {i}: {name}"
    for source, name in ((caveman, "Caveman"), (driver, "GP2040")):
        for token in ("wait_data(false,LOAD_TIMEOUT_US)", "wait_data(true,EDGE_TIMEOUT_US)"):
            compact = re.sub(r"\s+", "", source)
            assert token in compact, f"{name}: missing {token}"
        assert re.search(r"slot\s*=\s*1\s*;\s*slot\s*<\s*12", source), f"{name}: wrong slot loop"
        assert "wait_clock(false,EDGE_TIMEOUT_US)" in compact, f"{name}: missing falling edge"
        assert "wait_clock(true,EDGE_TIMEOUT_US)" in compact, f"{name}: missing rising edge"
    for i, (slot, inp) in enumerate(zip(SLOTS, GP_INPUTS)):
        print(f"{i:2} {slot:7} <- GP2040 {inp}")
    print("PASS: source-level slot map and frame skeleton; NOT a timing or hardware test.")

if __name__ == "__main__":
    check()
