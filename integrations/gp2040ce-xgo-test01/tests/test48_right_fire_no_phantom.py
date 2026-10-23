#!/usr/bin/env python3
"""Model and source guard: right held + fire taps must never assert unrelated buttons."""
from pathlib import Path

driver = Path("integrations/gp2040ce-xgo-test01/candidates/test47-clock-edge-phase-fix/XGODriver.cpp").read_text()
assert "constexpr uint16_t ATTACK_BITS = 0x003fu;" in driver
assert "const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;" in driver
assert "const uint16_t rising = attacks & ~previous_physical_attacks;" in driver
assert "pending_press_edges.fetch_or(rising" in driver

RIGHT = 1 << 11
FIRE = 1 << 4   # representative action bit, not a claimed Contra binding
JUMP = 1 << 5   # independent representative action bit
ATTACK_BITS = 0x003f
pending = 0
active = 0
started = 0
prev = 0
for t in range(0, 150000, 1000):
    tapped = (t // 7000) % 2 == 0
    physical = RIGHT | (FIRE if tapped else 0)
    attacks = physical & ATTACK_BITS
    pending |= attacks & ~prev
    prev = attacks
    if active and t-started >= 18000:
        active = 0
    if pending and not active:
        active = pending
        pending = 0
        started = t
    output = (physical & ~ATTACK_BITS) | active
    assert output & RIGHT
    assert not output & JUMP, f"unexpected unrelated bit at {t} us"
print("PASS: right + repeated fire taps cannot create another button bit in the pulse model")
