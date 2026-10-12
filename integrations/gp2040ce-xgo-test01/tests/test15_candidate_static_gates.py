#!/usr/bin/env python3
"""Static and model gates for isolated Test15 candidate; not hardware validation."""
from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
gold=(root/"src/drivers/xgo/XGODriver.cpp").read_text()
candidate=(root/"candidates/test15-offline/XGODriver.cpp").read_text()

def require(ok, why):
    assert ok, why
    print("PASS:",why)

def frame(s, signature):
    return s[s.index(signature):s.index("} // namespace",s.index(signature))]

old=frame(gold,"bool emit_frame(uint16_t mask)")
new=frame(candidate,"bool emit_frame()")
require("published_mask.load(std::memory_order_acquire)" in candidate,
        "acquire load retained")
require("published_mask.store(snapshot, std::memory_order_release)" in candidate,
        "release publication retained")
require("const bool complete = emit_frame();" in candidate,
        "responder no longer takes pre-LOAD snapshot")
require("const uint16_t snapshot = published_mask.load" not in candidate,
        "no stale snapshot in runResponder")
load=new.index("wait_data(false, LOAD_TIMEOUT_US)")
irq=new.index("save_and_disable_interrupts()")
snapshot=new.index("published_mask.load(std::memory_order_acquire)")
release=new.index("wait_data(true, EDGE_TIMEOUT_US)")
restore=new.index("restore_interrupts(irq_state)")
require(load < irq < snapshot < release < restore,
        "fresh snapshot taken under IRQ mask after LOAD low")
require(new.count("save_and_disable_interrupts()")==1 and
        new.count("restore_interrupts(irq_state)")==1,
        "single balanced interrupt-mask region")
irq_block=new[irq:restore]
require(not re.search(r"xgo_diag_\w+\.(fetch_add|store|load)",irq_block),
        "atomic diagnostic work removed from timing-critical region")
require(new.count("wait_clock(false, EDGE_TIMEOUT_US)")==2 and
        new.count("wait_clock(true, EDGE_TIMEOUT_US)")==2,
        "slot and trailing CLOCK waits retained")
require("(void)wait_clock(true, EDGE_TIMEOUT_US)" in new and
        "(void)wait_clock(true, EDGE_TIMEOUT_US)" in old,
        "reference-compatible final CLOCK rise semantics retained")
require("if (!complete) require_idle_high = true;" in new,
        "failure-only DATA-high rearm preserved")
require("if (mask & (1u << slot)) data_sink(); else data_release();" in new,
        "clocked slot mapping retained")
require("if (mask & 1u) data_sink(); else data_release();" in new,
        "slot zero mapping retained")
require("raw_init();" in candidate and
        "void XGODriver::initialize()" in candidate,
        "PHY ownership and initialization preserved")
require("xgo_diag_clock_failure_slots[failure_slot]" in candidate,
        "failure-slot diagnostic preserved")
require("xgo_diag_clock_failure_slots[slot]" in gold,
        "comparison against golden failure-slot accounting")
require(candidate.count("bool XGODriver::process(Gamepad *gamepad)") == 1,
        "Core0 mapping entrypoint preserved")
require(candidate[candidate.index("bool XGODriver::process(Gamepad *gamepad)"):] ==
        gold[gold.index("bool XGODriver::process(Gamepad *gamepad)"):],
        "Core0 producer byte-for-byte identical to golden")
print("PASS: Test15 candidate source gates")
