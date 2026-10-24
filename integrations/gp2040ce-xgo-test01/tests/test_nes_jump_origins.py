#!/usr/bin/env python3
"""XGO NES default keymap makes Contra JUMP non-unique to R/slot0.

This is SRC for the ROM-independent embedded FC fallback mapping and MODEL
for delayed DATA recovery. Do NOT present synthetic release delay as an
observed voltage, measured rise-time, or established cause of phantom jump.
"""
from pathlib import Path
import re
import unittest

PHYSICAL_ORDER=("X","Y","L","A","B","R")
WIRE_SLOT={"R":0,"Y":1,"X":2,"L":3,"A":4,"B":5}
JUMP_TARGET=8  # Libretro NES A
SHOOT_TARGET=0 # Libretro NES B
TURBO=1<<16

def embedded_nes_map():
    s=Path("findings/embedded-default-keymap-patch-points.md").read_text()
    part=s.split("### NES",1)[1]
    match=re.search(r"(?m)^((?:[0-9a-f]{8} ){5}[0-9a-f]{8})$",part)
    assert match, "Could not find full XGO embedded NES default table"
    words=[int(x,16) for x in match[1].split()]
    assert len(words)==6
    return dict(zip(PHYSICAL_ORDER,words))

def modeled_host_bits_if_load_release_is_delayed(recovery_us):
    # P0 representative captured clock structure, but host sample offsets
    # are hypothetical test conditions, NOT measured hardware sampling.
    sample_deltas={0:0.1,1:3.3,2:7.3}
    return sum((1<<slot) for slot,delta in sample_deltas.items()
               if recovery_us>delta)

class TestNesJumpOrigins(unittest.TestCase):
    def test_actual_xgo_embedded_NES_mapping(self):
        m=embedded_nes_map()
        self.assertEqual(m["R"],TURBO|JUMP_TARGET)
        self.assertEqual(m["X"],TURBO|JUMP_TARGET)
        self.assertEqual(m["A"],JUMP_TARGET)
        self.assertEqual(m["Y"],TURBO|SHOOT_TARGET)
        self.assertEqual(m["B"],SHOOT_TARGET)
        self.assertEqual(m["L"],TURBO|SHOOT_TARGET)

    def test_jump_sources_include_slot2_not_just_slot0(self):
        m=embedded_nes_map()
        slots={WIRE_SLOT[k] for k,v in m.items()
               if v&0xffff==JUMP_TARGET}
        self.assertEqual(slots,{0,2,4})
        # R, X and A can trigger NES jump in default mapping.
        self.assertTrue(2 in slots and 0 in slots)
        self.assertNotIn(5,slots)  # physical B/FIRE by itself is not jump

    def test_hypothetical_slow_data_recovery_can_contaminate_X(self):
        for delay in (0,0.35,3.5,7.5):
            raw=modeled_host_bits_if_load_release_is_delayed(delay)
            if delay<7.3:
                self.assertFalse(raw & (1<<WIRE_SLOT["X"]))
            else:
                self.assertTrue(raw & (1<<WIRE_SLOT["X"]))
        # This is a mathematical possibility, not an electrical measurement.

    def test_monotonic_release_tail_must_produce_prefix_not_isolated_x(self):
        # If the host-generated DATA LOW persists monotonically after LOAD,
        # later false slot2 necessarily implies earlier slot0 and slot1.
        # A later isolated false-X would demand a different glitch/phase
        # mechanism, not this simple one-parameter slow-rise model.
        for delay in [x / 10.0 for x in range(0, 221)]:
            raw=modeled_host_bits_if_load_release_is_delayed(delay)
            if raw & (1 << WIRE_SLOT["X"]):
                self.assertEqual(raw & 0x7, 0x7)
            if raw & (1 << WIRE_SLOT["Y"]):
                self.assertTrue(raw & (1 << WIRE_SLOT["R"]))
            self.assertIn(raw, (0, 1, 3, 7))

    def test_false_x_tail_also_activates_y_shoot_mapping(self):
        raw=modeled_host_bits_if_load_release_is_delayed(7.5)
        m=embedded_nes_map()
        self.assertEqual(raw & 0x7, 0x7)
        self.assertEqual(m["Y"] & 0xffff, SHOOT_TARGET)
        self.assertEqual(m["X"] & 0xffff, JUMP_TARGET)
        # Source/model prediction: simultaneous R+Y+X, not X alone.
        # No hardware capture establishes this in the actual XGO game.

    def test_slot0_only_inference_is_incomplete(self):
        jump_slots={WIRE_SLOT[k] for k,v in embedded_nes_map().items()
                    if v&0xffff==JUMP_TARGET}
        self.assertEqual((1<<0)|(1<<2)|(1<<4),
                         sum(1<<bit for bit in jump_slots))

if __name__=="__main__":
    unittest.main(verbosity=2)
