#!/usr/bin/env python3
"""Source guard for isolated SRAM hot-path experiment. No firmware validation."""
from pathlib import Path

root = Path("integrations/gp2040ce-xgo-test01/candidates")
base = (root/"test49-attack-edge-provenance/XGODriver.cpp").read_text()
trial = (root/"offline-ram-hotpath/XGODriver.cpp").read_text()
edits = (
 ('#include "pico/time.h"', '#include "pico/time.h"\n#include "pico/platform.h"'),
 ('bool wait_clock(bool level, uint32_t timeout) {',
  'bool __not_in_flash_func(wait_clock)(bool level, uint32_t timeout) {'),
 ('bool wait_data(bool level, uint32_t timeout) {',
  'bool __not_in_flash_func(wait_data)(bool level, uint32_t timeout) {'),
 ('bool emit_frame() {','bool __no_inline_not_in_flash_func(emit_frame)() {'),
)
comment = """// Offline-only time-critical placement experiment.
// Execute the serial responder and level-wait loops from SRAM so Core0
// flash activity cannot directly stall their instruction fetches.
// Does NOT solve DATA electrical threshold timing, verify slot phase,
// or guarantee external helper calls are SRAM resident.
// NO HW VALIDATION; do not replace protected Test44.
"""
expected=base
for old,new in edits:
    assert expected.count(old)==1, old
    expected=expected.replace(old,new)
expected=expected.replace(
  'bool __not_in_flash_func(wait_clock)(bool level, uint32_t timeout) {',
  comment+'bool __not_in_flash_func(wait_clock)(bool level, uint32_t timeout) {')
assert trial==expected, "RAM candidate contains functional, mapping, or timing changes"
assert "constexpr uint32_t EDGE_TIMEOUT_US = 18;" in trial
assert "constexpr uint32_t ATTACK_PULSE_US = 18000;" in trial
assert "const bool hk_slot0 = (mask & 1u) != 0;" in trial
assert "pending_press_edges.exchange(0, std::memory_order_acq_rel)" in trial
print("PASS isolated SRAM experiment is Test49 byte-for-byte except residency annotations")
