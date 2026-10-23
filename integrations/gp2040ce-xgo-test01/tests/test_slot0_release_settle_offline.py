#!/usr/bin/env python3
"""Source/HW-grounded but SYNTHETIC XGO slot-0 DATA release timing model.

P0 captured 6.8-7.5 us host DATA/LOAD low, followed 0.9-1.3 us later
by the first CLOCK low. XGO's stock scanner samples slot0 immediately
after DATA release. Actual DATA rising edge threshold at the host sample
has *not* been measured in the live GP2040-CE/Frankie setup.

This test demonstrates whether a delay to valid logic HIGH *could* yield
an unsolicited R/Contra JUMP with no processed R press. It does not prove
that threshold delay happened during the user's Test49 run.
"""
from pathlib import Path
import unittest

RELEASE_TO_FIRST_CLK_US = (0.9, 1.3)  # P0 measured range, HW
LOAD_LOW_US = (6.8, 7.5)              # P0 measured range, HW
CONTRA_JUMP_SLOT = 0
FIRE_SLOT = 5
START_SLOT = 7
RIGHT_SLOT = 11


def host_samples_slot0_low(settle_to_high_us, sample_after_release_us):
    """A deliberately simplified active-low threshold model.

    Host drove DATA LOW to load then changed DATA to an input. If the
    shared wire hasn't crossed its receiver's valid-high threshold when
    XGO samples serial position 0, the host sees R pressed.
    """
    assert settle_to_high_us >= 0 and sample_after_release_us >= 0
    return settle_to_high_us > sample_after_release_us


class TestSlot0Release(unittest.TestCase):
    def test_proven_jump_identity_and_p0_timing(self):
        p = Path("experiments/rp2040-responder-p1-fixed-r.md").read_text()
        q = Path("tools/rp2040-xgo-p2-contra/README.md").read_text()
        driver = Path(
            "integrations/gp2040ce-xgo-test01/candidates/"
            "test49-attack-edge-provenance/XGODriver.cpp"
        ).read_text()
        self.assertIn("fixed serial-position-0 R responder", p)
        self.assertIn("0.9-1.3 us", p)
        self.assertIn("6.8-7.5 us", p)
        self.assertIn("raw R maps through the current Contra keymap to FC A/jump", q)
        self.assertIn("g->pressedR1() ? 1u << 0", driver)
        self.assertIn("g->pressedB2() ? 1u << 5", driver)
        self.assertIn("data_release();\n // Test12 recovery:", driver)
        self.assertEqual(CONTRA_JUMP_SLOT, 0)
        self.assertNotEqual(CONTRA_JUMP_SLOT, FIRE_SLOT)
        self.assertNotEqual(CONTRA_JUMP_SLOT, START_SLOT)

    def test_clean_rise_does_not_cause_false_R(self):
        # Synthetic: line crosses HIGH threshold before host slot0 sample.
        self.assertFalse(host_samples_slot0_low(0.05, 0.20))

    def test_delayed_rise_can_cause_false_R_without_pressed_R(self):
        # Synthetic: no controller R event exists, but the host samples LOW.
        processed_mask = (1 << RIGHT_SLOT) | (1 << FIRE_SLOT)
        assert not processed_mask & (1 << CONTRA_JUMP_SLOT)
        sampled_r = host_samples_slot0_low(0.45, 0.15)
        decoded = processed_mask | ((1 << CONTRA_JUMP_SLOT) if sampled_r else 0)
        self.assertTrue(decoded & 1)           # Contra jump
        self.assertTrue(decoded & (1 << FIRE_SLOT))
        self.assertFalse(processed_mask & 1)    # No processed R press
        self.assertEqual(decoded & (1 << START_SLOT), 0)

    def test_jump_only_fault_can_end_before_first_CLOCK(self):
        # The host's immediate slot0 sample can be LOW while the first
        # CLOCK arrives after the line has recovered to HIGH. This is
        # consistent with P0's observation of DATA high through CLOCKs.
        sample_after_release_us = 0.10
        settles_high_at_us = 0.40
        first_clock_after_release_us = 1.10
        self.assertTrue(host_samples_slot0_low(settles_high_at_us,
                                               sample_after_release_us))
        self.assertLess(settles_high_at_us, first_clock_after_release_us)
        self.assertTrue(RELEASE_TO_FIRST_CLK_US[0] <=
                        first_clock_after_release_us <=
                        RELEASE_TO_FIRST_CLK_US[1])

    def test_pause_is_not_explained_by_first_slot_only(self):
        decoded = 1 << CONTRA_JUMP_SLOT
        self.assertFalse(decoded & (1 << START_SLOT))
        # Spontaneous START/PAUSE still needs independent evidence.

    def test_no_unjustified_rise_time_claim(self):
        self.assertLess(LOAD_LOW_US[0], LOAD_LOW_US[1])
        self.assertLess(RELEASE_TO_FIRST_CLK_US[0],
                        RELEASE_TO_FIRST_CLK_US[1])
        # 0.45us above is a synthetic counterexample, NOT a measured
        # electrical rise-time value from the user's controller.


if __name__ == "__main__":
    unittest.main(verbosity=2)
