#!/usr/bin/env python3
"""Model equivalence of legacy pending bits and SPSC per-bit event generations.

No hardware timing proof. Source guards ensure candidate changes only queue
plumbing and time-critical placement; tests compare *observable output pulses*
under frame schedules, fast taps, and concurrent event arrival boundaries.
"""
from pathlib import Path
import random
import unittest

ROOT = Path("integrations/gp2040ce-xgo-test01/candidates")
BASE = (ROOT / "offline-ram-hotpath/XGODriver.cpp").read_text()
NEW = (ROOT / "offline-spsc-ram-hotpath/XGODriver.cpp").read_text()

class BaseQueue:
    def __init__(self):
        self.pressed = 0
        self.pending = 0
        self.pulse = 0
        self.start = 0

    def core0_sample(self, attacks):
        rising = attacks & ~self.pressed & 0x3f
        self.pressed = attacks
        self.pending |= rising

    def host_scan(self, now, after_sample=None):
        if self.pulse and now - self.start >= 18000:
            self.pulse = 0
        pending = self.pending
        self.pending = 0
        if after_sample:
            after_sample()  # New Core0 edge after atomic exchange.
        if pending and not self.pulse:
            self.pulse = pending
            self.start = now
        elif pending:
            self.pending |= pending
        return self.pulse


class GenerationQueue:
    def __init__(self):
        self.pressed = 0
        self.generation = [0] * 6
        self.consumed = [0] * 6
        self.pulse = 0
        self.start = 0

    def core0_sample(self, attacks):
        rising = attacks & ~self.pressed & 0x3f
        self.pressed = attacks
        for bit in range(6):
            if rising & (1 << bit):
                self.generation[bit] = (self.generation[bit] + 1) & 0xffffffff

    def host_scan(self, now, after_sample=None):
        if self.pulse and now - self.start >= 18000:
            self.pulse = 0
        observed = self.generation.copy()  # Six atomic loads (not a coherent transaction).
        pending = sum((1 << bit) for bit in range(6)
                      if observed[bit] != self.consumed[bit])
        if after_sample:
            after_sample()  # New Core0 event after observation is not acknowledged.
        if pending and not self.pulse:
            self.pulse = pending
            self.start = now
            for bit in range(6):
                if pending & (1 << bit):
                    self.consumed[bit] = observed[bit]
        return self.pulse


class TestSPSC(unittest.TestCase):
    def check_pair(self, actions):
        a, b = BaseQueue(), GenerationQueue()
        outputs = []
        for kind, value in actions:
            if kind == "sample":
                a.core0_sample(value)
                b.core0_sample(value)
            elif kind == "scan":
                before = (a.host_scan(value), b.host_scan(value))
                self.assertEqual(before[0], before[1], ("pulse mismatch", value))
                outputs.append((value, before[0]))
            else:
                raise AssertionError(kind)
        return outputs

    def test_source_diff_only_event_transport(self):
        replacements = [
            ("""// Core0 observes physical transitions; Core1 acknowledges consumption once per host scan.
namespace { std::atomic<uint16_t> pending_press_edges{0}; }""",
             """// SPSC event generations: Core0 increments, Core1 observes. Per-button
// counters avoid a read-modify-write / hardware spinlock on Core1 after LOAD.
namespace { std::atomic<uint32_t> attack_edge_generation[6]{}; }
namespace { uint32_t consumed_attack_edge_generation[6]{}; }"""),
            (""" const uint16_t pending = pending_press_edges.exchange(0, std::memory_order_acq_rel);
 // Queue any new edge after the current window; do not erase other edges.
 // Physical release is tracked on Core0, not inferred from the output pulse.
 if (pending && !attack_pulse_mask) {
  attack_pulse_mask = pending;
  attack_pulse_start_us = now;
 } else if (pending) {
  pending_press_edges.fetch_or(pending, std::memory_order_release);
 }""",
             """ // Snapshot Core0 event generations without a lock-taking atomic RMW.
 // Each load is 32-bit/aligned on ARMv6-M; verify the linked ELF before use.
 // Observed generations are only acknowledged when their pulse starts:
 // an edge arriving during this scan stays pending until a future scan.
 uint16_t pending = 0;
 uint32_t observed_edge_generation[6];
 for (unsigned bit = 0; bit < 6; ++bit) {
  observed_edge_generation[bit] = attack_edge_generation[bit].load(std::memory_order_acquire);
  if (observed_edge_generation[bit] != consumed_attack_edge_generation[bit])
   pending |= uint16_t(1u << bit);
 }
 // A second press during the current pulse remains pending, not discarded.
 if (pending && !attack_pulse_mask) {
  attack_pulse_mask = pending;
  attack_pulse_start_us = now;
  for (unsigned bit = 0; bit < 6; ++bit)
   if (pending & (1u << bit))
    consumed_attack_edge_generation[bit] = observed_edge_generation[bit];
 }"""),
            ("""  for (unsigned bit = 0; bit < 6; ++bit)
   if (rising & (1u << bit))
    xgo_diag_attack_rising_edges[bit].fetch_add(1, std::memory_order_relaxed);
  pending_press_edges.fetch_or(rising, std::memory_order_release);""",
             """  for (unsigned bit = 0; bit < 6; ++bit) {
   if (rising & (1u << bit)) {
    xgo_diag_attack_rising_edges[bit].fetch_add(1, std::memory_order_relaxed);
    attack_edge_generation[bit].fetch_add(1, std::memory_order_release);
   }
  }""")
        ]
        expected = BASE
        for old, new in replacements:
            self.assertEqual(expected.count(old), 1, old)
            expected = expected.replace(old, new)
        self.assertEqual(NEW, expected)
        # GPIO timings, priority, serial bit layout, diagnostic policy remain.
        for must in (
            "constexpr uint32_t EDGE_TIMEOUT_US = 18;",
            "constexpr uint32_t ATTACK_PULSE_US = 18000;",
            "const bool hk_slot0 = (mask & 1u) != 0;",
            "const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;",
            "if (!complete) require_idle_high = true;",
            "bool __no_inline_not_in_flash_func(emit_frame)() {"
        ):
            self.assertIn(must, NEW)
        critical = NEW[NEW.index("bool __no_inline_not_in_flash_func(emit_frame)() {"):
                       NEW.index("} // namespace", NEW.index("bool __no_inline_not_in_flash_func(emit_frame)() {"))]
        self.assertNotIn("pending_press_edges", critical)
        self.assertNotIn(".exchange(", critical)
        self.assertNotIn(".fetch_or(", critical)

    def test_rapid_tapping_same_button_pulse_equivalence(self):
        actions = []
        state = 0
        for ms in range(0, 500, 2):
            state = 0x20 if (ms // 4) % 2 else 0
            actions.append(("sample", state))
            if ms % 16 == 0:
                actions.append(("scan", ms * 1000))
        out = self.check_pair(actions)
        self.assertTrue(any(mask & 0x20 for _, mask in out))

    def test_holding_does_not_repeat_and_repress_during_pulse_waits(self):
        seq = [
            ("sample", 0x20), ("scan", 0),
            ("scan", 16000), ("scan", 32000),  # First pulse expires
            ("sample", 0), ("sample", 0x20),
            ("scan", 48000), ("scan", 64000), ("scan", 80000)
        ]
        out = self.check_pair(seq)
        self.assertEqual([v for _, v in out], [0x20, 0x20, 0, 0x20, 0x20, 0])

    def test_simultaneous_and_deferred_distinct_attack(self):
        self.check_pair([
            ("sample", 0x03), ("scan", 0),
            ("sample", 0), ("sample", 0x24),
            ("scan", 16000), ("scan", 32000), ("scan", 48000),
            ("sample", 0), ("sample", 0x20), ("scan", 64000),
            ("scan", 80000), ("scan", 96000)
        ])

    def test_edge_arriving_after_scan_snapshot_not_acknowledged(self):
        a,b = BaseQueue(),GenerationQueue()
        a.core0_sample(0x20); b.core0_sample(0x20)
        def rising(consumer):
            consumer.core0_sample(0)
            consumer.core0_sample(0x10)
        self.assertEqual(a.host_scan(0,lambda: rising(a)),
                         b.host_scan(0,lambda: rising(b)))
        self.assertEqual(a.host_scan(16000),b.host_scan(16000))
        self.assertEqual(a.host_scan(32000),b.host_scan(32000))
        self.assertEqual(a.pulse,b.pulse)
        self.assertTrue(a.pulse & 0x10)

    def test_deterministic_stress_25k_events(self):
        rng=random.Random(0xA10)
        a,b=BaseQueue(),GenerationQueue()
        mask=0
        for event in range(25000):
            if rng.random() < .71:
                mask ^= (1 << rng.randrange(6))
                a.core0_sample(mask); b.core0_sample(mask)
            if rng.random() < .43:
                now=event*720
                self.assertEqual(a.host_scan(now),b.host_scan(now),
                                 f"frame mismatch at event={event}")
        self.assertEqual(a.pulse,b.pulse)

    def test_wraparound_counter_does_not_require_reset(self):
        g=GenerationQueue()
        g.consumed[5]=0xffffffff
        g.generation[5]=0xffffffff
        g.core0_sample(0x20)  # 0xffffffff -> 0, still different from consumed
        self.assertEqual(g.generation[5],0)
        self.assertEqual(g.host_scan(0),0x20)
        self.assertEqual(g.consumed[5],0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
