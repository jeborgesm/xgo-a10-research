#!/usr/bin/env python3
"""Behavioral source checks for Test26 input lifecycle."""
from pathlib import Path
s=Path("integrations/gp2040ce-xgo-test01/candidates/test26-hk-sequencer-offline/XGODriver.cpp").read_text()
p=s.split("bool XGODriver::process(Gamepad *gamepad) {",1)[1]
checks=[
 "const uint16_t physical = map_mask(gamepad);",
 "const bool chord = select && start && hk;",
 "const bool abort = select && start && !hk;",
 "if (abort_edge && (armed || hk_sequence.running()))",
 "hk_sequence.reset();",
 "if (armed && !hk && !select && !start) trigger_released = true;",
 "const uint16_t synthetic = hk_sequence.update(to_ms_since_boot(get_absolute_time()), trigger);",
 "if (swallow_trigger_until_release && hk && !hk_sequence.running()) snapshot &= ~1u;",
 "if (chord || abort || swallow_chord_until_release) snapshot = 0;",
 "published_mask.store(snapshot, std::memory_order_release);",
]
for c in checks:
 assert c in p,c
print("Test26 lifecycle source assertions passed; dynamic simulation still pending")
