#!/usr/bin/env python3
"""Test50 controlled SELECT/START processed-edge provenance checks.

This is a source-level/state-transition model, not a host serial waveform model.
"""
from pathlib import Path

root=Path("integrations/gp2040ce-xgo-test01/candidates")
old=(root/"test49-attack-edge-provenance/XGODriver.cpp").read_text()
new=(root/"test50-pause-edge-provenance/XGODriver.cpp").read_text()
ui=(root/"test50-pause-edge-provenance/ButtonLayoutScreen.cpp").read_text()
header=(root/"test50-pause-edge-provenance/XGODiagnostics.h").read_text()

def section(s, begin, end):
    return s[s.index(begin):s.index(end, s.index(begin))]

assert section(new,"bool emit_frame()","} // namespace") == section(old,"bool emit_frame()","} // namespace"), "Serial responder changed"
assert section(new,"uint16_t map_mask(","bool emit_frame()") == section(old,"uint16_t map_mask(","bool emit_frame()"), "Input mapping changed"
assert "constexpr uint32_t EDGE_TIMEOUT_US = 18;" in new
assert "constexpr uint32_t ATTACK_PULSE_US = 18000;" in new
assert "pending_press_edges.fetch_or(rising, std::memory_order_release);" in new
assert "std::atomic<uint32_t> xgo_diag_system_rising_edges[2]{};" in new
assert "extern std::atomic<uint32_t> xgo_diag_system_rising_edges[2];" in header
assert "const uint16_t system_rising = (snapshot & 0x00c0u) & ~previous_snapshot;" in new
for bit in range(2):
    assert f"xgo_diag_system_rising_edges[{bit}].fetch_add(1, std::memory_order_relaxed);" in new
    assert f"xgo_diag_system_rising_edges[{bit}].load" in ui
assert "XGO50 PAUSE TRACE" in ui

def edges(masks):
    previous=0
    counts=[0,0]
    for snapshot in masks:
        rising=(snapshot & 0x00c0) & (~previous & 0xffff)
        counts[0]+=int(bool(rising & (1 << 6)))
        counts[1]+=int(bool(rising & (1 << 7)))
        previous=snapshot
    return counts

RIGHT=1 << 11
FIRE=1 << 5
SELECT=1 << 6
START=1 << 7
no_start=[RIGHT | (FIRE if (i//5)%2 else 0) for i in range(1000)]
assert edges(no_start)==[0,0], "Right+Fire should not produce a processed system edge"
assert edges([RIGHT | START]*1000)==[0,1], "Held Start must count once"
assert edges([RIGHT,RIGHT | START,RIGHT,RIGHT | START])==[0,2], "Start must rearm on release"
assert edges([RIGHT | SELECT,RIGHT | SELECT,RIGHT])==[1,0]
assert edges(no_start+[RIGHT | START,RIGHT,RIGHT | START])==[0,2]
print("PASS: Test50 unchanged PHY/mapping and SELECT/START processed-edge accounting")
