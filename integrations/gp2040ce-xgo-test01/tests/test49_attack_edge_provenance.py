#!/usr/bin/env python3
"""Test49: processed-input edge provenance, not a host-electrical simulator."""
from pathlib import Path

root = Path("integrations/gp2040ce-xgo-test01")
prior = (root / "candidates/test48-right-fire-phantom-diag/XGODriver.cpp").read_text()
current = (root / "candidates/test49-attack-edge-provenance/XGODriver.cpp").read_text()
display = (root / "candidates/test49-attack-edge-provenance/ButtonLayoutScreen.cpp").read_text()
header = (root / "candidates/test49-attack-edge-provenance/XGODiagnostics.h").read_text()

def responder(source):
    start = source.index("bool emit_frame()")
    end = source.index("} // namespace", start)
    return source[start:end]

assert responder(current) == responder(prior), "Serial responder or timing was modified"
assert "constexpr uint32_t EDGE_TIMEOUT_US = 18;" in current
assert "constexpr uint32_t ATTACK_PULSE_US = 18000;" in current
assert "pending_press_edges.fetch_or(rising, std::memory_order_release);" in current
assert "xgo_diag_attack_rising_edges[bit].fetch_add(1, std::memory_order_relaxed);" in current
assert "extern std::atomic<uint32_t> xgo_diag_attack_rising_edges[6];" in header
for bit in range(6):
    assert f"xgo_diag_attack_rising_edges[{bit}].load" in display
assert 'XGO49 EDGE TRACE' in display

ATTACK_BITS = 0x003f
RIGHT = 1 << 11
FIRE = 1 << 5
OTHER = 1 << 4

def simulate(inputs):
    prev = 0
    pending = 0
    active = 0
    started = 0
    counts = [0] * 6
    for time, mask in inputs:
        attacks = mask & ATTACK_BITS
        rising = attacks & ~prev
        prev = attacks
        for bit in range(6):
            if rising & (1 << bit):
                counts[bit] += 1
        pending |= rising
        if active and time-started >= 18000:
            active = 0
        if pending and not active:
            active, pending, started = pending, 0, time
        output = (mask & ~ATTACK_BITS) | active
        assert output & RIGHT
        if counts[4] == 0:
            assert not output & OTHER, "Pulse queue synthesized an unrelated button"
    return counts

# Stress repeated taps and a long hold without JUMP.
sequence = [(t, RIGHT | (FIRE if (t // 6000) % 2 else 0))
            for t in range(0, 240000, 1000)]
counts = simulate(sequence)
assert counts[5] > 10 and all(v == 0 for i, v in enumerate(counts) if i != 5)
# Holding FIRE produces one physical rising edge, not repeated edges.
counts = simulate([(t, RIGHT | FIRE) for t in range(0, 240000, 1000)])
assert counts[5] == 1 and sum(counts) == 1
# If a processed JUMP does appear, it must appear in its own edge counter.
counts = simulate([(0, RIGHT | FIRE), (1000, RIGHT), (2000, RIGHT | OTHER)])
assert counts[4] == 1 and counts[5] == 1
print("PASS: Test49 edge provenance source guard and repeated-tap models")
