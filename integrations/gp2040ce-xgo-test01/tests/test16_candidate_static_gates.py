#!/usr/bin/env python3
"""Static source gates for isolated Test16, not hardware proof."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]
gold=(root/"src/drivers/xgo/XGODriver.cpp").read_text()
new=(root/"candidates/test16-offline/XGODriver.cpp").read_text()
def check(condition, label):
    assert condition, label
    print("PASS:", label)
frame=new[new.index("bool emit_frame()"):new.index("} // namespace",new.index("bool emit_frame()"))]
critical=frame[frame.index("save_and_disable_interrupts()"):frame.index("restore_interrupts(irq_state)")]
check("bool emit_frame(uint16_t mask)" in gold and "bool emit_frame()" in new,"isolated candidate, original snapshot API preserved")
check("const bool complete = emit_frame();" in new and "const uint16_t snapshot = published_mask.load" not in new,"snapshot acquired inside responder transaction")
check(frame.index("wait_data(false, LOAD_TIMEOUT_US)") < frame.index("published_mask.load(std::memory_order_acquire)") < frame.index("wait_data(true, EDGE_TIMEOUT_US)"),"snapshot after LOAD low before LOAD release")
check(not re.search(r"xgo_diag_\\w+\\.(fetch_add|store|load)",critical),"no diagnostic atomics in IRQ-disabled serial train")
check("if (complete && !wait_clock(true, EDGE_TIMEOUT_US)) { complete = false; }" in critical,"final CLOCK rise failure is not success")
check("if (!complete) require_idle_high = true;" in frame,"failed frame requires DATA-high rearm")
check("if (mask & 1u) data_sink(); else data_release();" in frame and "if (mask & (1u << slot)) data_sink(); else data_release();" in frame,"all serial slots still use one snapshot")
check(new[new.index("bool XGODriver::process(Gamepad *gamepad)"):] == gold[gold.index("bool XGODriver::process(Gamepad *gamepad)"):],"producer and mapping unchanged")
check("raw_init();" in new,"PHY setup retained")
print("PASS: Test16 static gates; timing and electrical correctness remain unproven")
