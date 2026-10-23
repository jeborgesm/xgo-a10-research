#!/usr/bin/env python3
"""XGO source-guided serial boundary/fault models, not hardware proof.

Run from repository root: python3 integrations/gp2040ce-xgo-test01/tests/test_serial_boundary_faults_offline.py

Source guards pin the exact contrasting end-of-frame logic; pure Python models
explore consequences and explicitly avoid claiming measured host behavior.
"""
from dataclasses import dataclass
from pathlib import Path
import unittest

ROOT = Path('integrations/gp2040ce-xgo-test01')
NATIVE = Path('tools/rp2040-xgo-live-controller/main.c')
CONTRA = Path('tools/rp2040-xgo-native-contra/main.c')
GP = ROOT / 'candidates/test49-attack-edge-provenance/XGODriver.cpp'
GP50 = ROOT / 'candidates/test50-pause-edge-provenance/XGODriver.cpp'
TEST49 = ROOT / 'tests/test49_attack_edge_provenance.py'
CANDIDATE = ROOT / 'candidates/offline-terminal-postamble/XGODriver.cpp'
OLD_POSTAMBLE = ('if (complete && !wait_clock(true, EDGE_TIMEOUT_US)) { complete = false; '
                 'clock_high_failure = true; clock_timeout = true; failed_slot = 12; }')
NEW_POSTAMBLE = 'if (complete) (void)wait_clock(true, EDGE_TIMEOUT_US);'

RIGHT = 1 << 11
FIRE_B2 = 1 << 5    # Observed P5 rising with deliberate FIRE tapping.
JUMP_R0 = 1 << 0     # HW fixed-R/P1 Contra A=JUMP mapping, slot 0.
OTHER_B1 = 1 << 4   # B1 is an independent slot, not proven to be Contra JUMP.
START_S2 = 1 << 7
SELECT_S1 = 1 << 6
ATTACK_BITS = 0x003f


@dataclass(frozen=True)
class Postamble:
    """Model host's final clock low/high after all twelve button slots."""
    saw_terminal_clock_low: bool
    saw_terminal_clock_high_before_timeout: bool


def native_completes(p: Postamble) -> bool:
    # Native code ignores final high wait's result.
    return p.saw_terminal_clock_low


def gp49_completes(p: Postamble) -> bool:
    # GP Test49 requires final high to complete successfully.
    return p.saw_terminal_clock_low and p.saw_terminal_clock_high_before_timeout


def processed_edges(states):
    prev = 0
    counts = [0] * 8
    for state in states:
        rising = (state & 0x00ff) & ~prev
        for bit in range(8):
            if rising & (1 << bit):
                counts[bit] += 1
        prev = state & 0x00ff
    return counts


def pulse_queue_states(processed_samples, pulse_us=18000):
    """Source-shaped happy-path queue; no I/O fault injection.

    Models current Core0 edge accumulation and Core1 time-bounded attack
    window when one host poll follows every processed sample. This is not
    an independent emulator of GP2040-CE or an electrical host decoder.
    """
    previous_attacks = 0
    pending = 0
    active = 0
    started = 0
    output = []
    for now, state in processed_samples:
        attacks = state & ATTACK_BITS
        pending |= attacks & ~previous_attacks
        previous_attacks = attacks
        if active and now - started >= pulse_us:
            active = 0
        new_pending = pending
        pending = 0
        if new_pending and not active:
            active, started = new_pending, now
        elif new_pending:
            pending |= new_pending
        output.append((state & ~ATTACK_BITS) | active)
    return output


def ideal_host_slots(mask: int, shift: int = 0) -> int:
    """Demonstrate *possible* wrong-button decoding from bit-position drift.

    Positive shift means a future serial bit is sampled into an earlier host
    slot; negative shift means an older bit persists into later host slots.
    This cannot establish that either drift actually happened on XGO.
    """
    return sum(((mask >> (slot + shift)) & 1) << slot
               for slot in range(12) if 0 <= slot + shift < 12)


class TestProvenContracts(unittest.TestCase):
    def test_same_12_slot_order(self):
        s = GP.read_text()
        expressions = ['g->pressedR1()', 'g->pressedB4()',
                       'g->pressedB3()', 'g->pressedL1()',
                       'g->pressedB1()', 'g->pressedB2()',
                       'g->pressedS1()', 'g->pressedS2()',
                       'g->pressedUp()', 'g->pressedDown()',
                       'g->pressedLeft()', 'g->pressedRight()']
        positions = [s.index(e) for e in expressions]
        self.assertEqual(positions, sorted(positions))

    def test_source_contrast_terminal_clock(self):
        # This distinguishes a real source difference from an invented model.
        for path in [NATIVE, CONTRA, GP, GP50]:
            self.assertTrue(path.is_file(), str(path))
        n, c, g, g50 = (p.read_text() for p in [NATIVE, CONTRA, GP, GP50])
        self.assertIn('(void)wait_clock(true,EDGE_TIMEOUT_US);', n)
        self.assertIn('(void)wait_clock(true,EDGE_TIMEOUT_US);', c)
        gp_guard = 'if (complete && !wait_clock(true, EDGE_TIMEOUT_US)) { complete = false;'
        self.assertIn(gp_guard, g)
        self.assertIn(gp_guard, g50)
        self.assertIn(OLD_POSTAMBLE, g)
        self.assertIn('if (!complete) require_idle_high = true;', g)
        self.assertIn('if (!complete) require_idle_high = true;', g50)
        self.assertIn('const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;', g)
        self.assertIn('constexpr uint32_t EDGE_TIMEOUT_US = 18;', g)
        self.assertIn('#define EDGE_TIMEOUT_US 12u', n)

    def test_real_contra_jump_binding_is_serial_R_slot0(self):
        p = Path('experiments/rp2040-responder-p1-fixed-r.md').read_text()
        q = Path('tools/rp2040-xgo-p2-contra/README.md').read_text()
        self.assertIn('fixed serial-position-0 R responder', p)
        self.assertIn('raw R maps through the current Contra keymap to FC A/jump', q)
        self.assertEqual(JUMP_R0, 1)
        self.assertNotEqual(JUMP_R0, OTHER_B1)

    def test_postamble_candidate_is_exactly_one_line_difference(self):
        # Candidate must not touch pulses, mask, IRQ, release, pin mappings,
        # or other sections. This is a source guard, not a compiled binary.
        old = GP.read_text()
        candidate = CANDIDATE.read_text()
        self.assertEqual(old.count(OLD_POSTAMBLE), 1)
        self.assertEqual(candidate, old.replace(OLD_POSTAMBLE, NEW_POSTAMBLE))

    def test_fire_label_matches_observed_p5(self):
        self.assertIn('FIRE = 1 << 5', TEST49.read_text())
        self.assertIn('OTHER = 1 << 4', TEST49.read_text())
        self.assertIn('g->pressedB1() ? 1u << 4', GP.read_text())
        self.assertIn('g->pressedB2() ? 1u << 5', GP.read_text())
        self.assertIn('g->pressedS2() ? 1u << 7', GP.read_text())


class TestBoundaryModel(unittest.TestCase):
    def test_normal_tail_both_accept(self):
        p = Postamble(True, True)
        self.assertTrue(native_completes(p))
        self.assertTrue(gp49_completes(p))

    def test_terminal_high_timeout_only_gp_marks_failed(self):
        p = Postamble(True, False)
        self.assertTrue(native_completes(p))
        self.assertFalse(gp49_completes(p))
        # All 12 bits have already been sent in this case; no individual
        # wrong button follows *solely* from this postamble difference.

    def test_terminal_low_timeout_both_fail(self):
        p = Postamble(False, False)
        self.assertFalse(native_completes(p))
        self.assertFalse(gp49_completes(p))

    def test_recorded_test49_slot12_errors_are_substantial(self):
        # Test49 corrected run screenshots: 40 -> 126 -> 226.
        # These counts do NOT separate missing final low from final high.
        self.assertEqual(226 - 40, 186)
        self.assertEqual(320 - 59, 261)
        self.assertLess(186, 261)


class TestNoPhantomFromCleanInput(unittest.TestCase):
    def test_right_and_repeated_fire_only_never_invents_jump_or_start(self):
        samples = [(i * 1000, RIGHT | (FIRE_B2 if (i // 5) % 2 else 0))
                   for i in range(2000)]
        output = pulse_queue_states(samples)
        edges = processed_edges([s for _, s in samples])
        self.assertGreater(edges[5], 100)
        self.assertEqual(edges[0], 0)
        self.assertEqual(edges[4], 0)
        self.assertEqual(edges[7], 0)
        self.assertTrue(all(m & RIGHT for m in output))
        self.assertTrue(all(not (m & JUMP_R0) for m in output))
        self.assertTrue(all(not (m & OTHER_B1) for m in output))
        self.assertTrue(all(not (m & START_S2) for m in output))
        self.assertTrue(all(not (m & SELECT_S1) for m in output))

    def test_hold_fire_produces_single_processed_rise(self):
        states = [RIGHT | FIRE_B2] * 400
        edges = processed_edges(states)
        self.assertEqual(edges[5], 1)
        self.assertEqual(edges[4], 0)
        self.assertEqual(edges[7], 0)

    def test_ideal_host_decoding_never_invents_buttons(self):
        for state in [RIGHT, RIGHT | FIRE_B2, FIRE_B2, 0]:
            self.assertEqual(ideal_host_slots(state), state)
            self.assertFalse(ideal_host_slots(state) & (JUMP_R0 | START_S2 | OTHER_B1))

    def test_one_slot_advance_can_make_fire_look_like_unrelated_B1_not_jump(self):
        decoded = ideal_host_slots(RIGHT | FIRE_B2, shift=1)
        self.assertTrue(decoded & OTHER_B1)
        self.assertFalse(decoded & START_S2)
        self.assertFalse((RIGHT | FIRE_B2) & OTHER_B1)
        self.assertFalse(decoded & JUMP_R0)
        # Contra JUMP is hardware-confirmed on R/slot0, not B1/slot4.
        # Synthetic alignment offset only: no observed CLOCK waveform.

    def test_two_slot_delay_can_make_fire_look_like_start(self):
        decoded = ideal_host_slots(RIGHT | FIRE_B2, shift=-2)
        self.assertTrue(decoded & START_S2)
        self.assertFalse(decoded & JUMP_R0)
        self.assertFalse(decoded & OTHER_B1)
        self.assertFalse((RIGHT | FIRE_B2) & START_S2)
        # Synthetic alignment offset only: no observed CLOCK waveform.


if __name__ == '__main__':
    unittest.main(verbosity=2)
