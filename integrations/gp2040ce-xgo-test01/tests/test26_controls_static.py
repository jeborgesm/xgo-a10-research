#!/usr/bin/env python3
"""Fail-closed source gates for Test26 Core0 hotkey integration."""
from pathlib import Path
p=Path("integrations/gp2040ce-xgo-test01/candidates/test26-hk-sequencer-offline/XGODriver.cpp")
s=p.read_text()
core0=s.split("bool XGODriver::process(Gamepad *gamepad) {",1)[1]
core1=s.split("void XGODriver::runResponder() {",1)[1].split("bool XGODriver::process",1)[0]
assert "static bool swallow_chord_until_release" in core0
assert "static bool swallow_trigger_until_release" in core0
assert "if (abort_edge && (armed || hk_sequence.running()))" in core0
assert "hk_sequence.reset();" in core0
assert "if (armed && !hk && !select && !start) trigger_released = true;" in core0
assert "hk_sequence.update(to_ms_since_boot(get_absolute_time()), trigger)" in core0
assert "snapshot &= ~1u;" in core0
assert "snapshot = physical;" in core0
assert "xgo_hk_phase_state.store" in core0
assert "xgo_hk_repeat_state.store" in core0
assert "published_mask.store(snapshot, std::memory_order_release)" in core0
assert "hk_sequence" not in core1
print("Test26 static source gates passed (not a hardware or behavioral simulation)")
