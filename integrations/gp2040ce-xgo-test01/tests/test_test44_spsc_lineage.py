#!/usr/bin/env python3
"""Guard playable SPSC source against the exact HW-proven Test44 baseline.

The isolated candidate is the already ELF-proven SPSC+RAM source with only
Test49-added diagnostic provenance stripped. No GPIO/serial timing/pulse
reconfiguration is permitted. The pinned Test44 and original SPSC blobs
are verified by exact Git blob hash, so these assertions have provenance.
"""
from pathlib import Path
import hashlib
import unittest

ROOT=Path("integrations/gp2040ce-xgo-test01/candidates")
GOLDEN=ROOT/"test44-clock-timeout-18us/XGODriver.cpp"
PROVEN=ROOT/"offline-spsc-ram-hotpath/XGODriver.cpp"
NEW=ROOT/"offline-test44-spsc-ram-playable/XGODriver.cpp"

def git_blob_sha(p):
    data=p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def strip_test49_diagnostics(proven):
    pairs=[
      ("""std::atomic<uint32_t> xgo_diag_clock_low_failures{0};
std::atomic<uint32_t> xgo_diag_clock_high_failures{0};
std::atomic<uint32_t> xgo_diag_right_attack_attempts{0};
std::atomic<uint32_t> xgo_diag_right_attack_failures{0};
// Processed Gamepad rising edges per attack bit (not raw GPIO).
std::atomic<uint32_t> xgo_diag_attack_rising_edges[6]{};
""",""),
      (" bool clock_low_failure = false;\n bool clock_high_failure = false;\n",""),
      ("if (!wait_clock(false, EDGE_TIMEOUT_US)) { clock_timeout = true; clock_low_failure = true; failed_slot = slot; complete = false; break; }",
       "if (!wait_clock(false, EDGE_TIMEOUT_US)) { clock_timeout = true; failed_slot = slot; complete = false; break; }"),
      ("if (!wait_clock(true, EDGE_TIMEOUT_US)) { clock_timeout = true; clock_high_failure = true; failed_slot = slot; complete = false; break; }",
       "if (!wait_clock(true, EDGE_TIMEOUT_US)) { clock_timeout = true; failed_slot = slot; complete = false; break; }"),
      ("if (!wait_clock(false, EDGE_TIMEOUT_US)) { clock_timeout = true; clock_low_failure = true; failed_slot = 12; complete = false; }",
       "if (!wait_clock(false, EDGE_TIMEOUT_US)) { clock_timeout = true; failed_slot = 12; complete = false; }"),
      ("if (complete && !wait_clock(true, EDGE_TIMEOUT_US)) { complete = false; clock_high_failure = true; clock_timeout = true; failed_slot = 12; }",
       "if (complete && !wait_clock(true, EDGE_TIMEOUT_US)) { complete = false; }"),
      (""" const bool right_and_attack = (mask & (1u << 11)) && (mask & ATTACK_BITS);
 if (right_and_attack) {
  xgo_diag_right_attack_attempts.fetch_add(1, std::memory_order_relaxed);
  if (!complete) xgo_diag_right_attack_failures.fetch_add(1, std::memory_order_relaxed);
 }
""",""),
      (" if (clock_low_failure) xgo_diag_clock_low_failures.fetch_add(1, std::memory_order_relaxed);\n if (clock_high_failure) xgo_diag_clock_high_failures.fetch_add(1, std::memory_order_relaxed);\n",""),
      ("""  for (unsigned bit = 0; bit < 6; ++bit) {
   if (rising & (1u << bit)) {
    xgo_diag_attack_rising_edges[bit].fetch_add(1, std::memory_order_relaxed);
    attack_edge_generation[bit].fetch_add(1, std::memory_order_release);
   }
  }""",
       """  for (unsigned bit = 0; bit < 6; ++bit)
   if (rising & (1u << bit))
    attack_edge_generation[bit].fetch_add(1, std::memory_order_release);""")
    ]
    for old,new in pairs:
        assert proven.count(old)==1, f"Unrecognized upstream SPSC layout: {old[:70]}"
        proven=proven.replace(old,new)
    return proven

class TestGoldenPlayCandidate(unittest.TestCase):
    def test_protected_golden_source_hash(self):
        self.assertEqual(git_blob_sha(GOLDEN),"f445a1a6d8f9c871a80532e25cc5b1a3ac3b32a0")

    def test_proven_spsc_source_hash(self):
        self.assertEqual(git_blob_sha(PROVEN),"68301b47e4b815cff4cfd5b24bf760d875875492")

    def test_exact_spsc_minus_test49_diagnostics(self):
        self.assertEqual(NEW.read_text(),strip_test49_diagnostics(PROVEN.read_text()))

    def test_protected_mapping_timing_queue_and_no_extra_counters(self):
        golden=GOLDEN.read_text()
        cand=NEW.read_text()
        maskstart="uint16_t map_mask(Gamepad *g) {"
        end="\n}\n"
        self.assertEqual(golden[golden.index(maskstart):golden.index(end,golden.index(maskstart))+len(end)],
                         cand[cand.index(maskstart):cand.index(end,cand.index(maskstart))+len(end)])
        for invariant in (
            "constexpr uint32_t EDGE_TIMEOUT_US = 18;",
            "constexpr uint32_t ATTACK_PULSE_US = 18000;",
            "constexpr uint16_t ATTACK_BITS = 0x003fu;",
            "const bool hk_slot0 = (mask & 1u) != 0;",
            "while ((uint32_t)(time_us_32() - low_start) < 3u) {}",
            "const uint16_t mask = (physical & ~ATTACK_BITS) | attack_pulse_mask;",
            "if (!complete) require_idle_high = true;",
            "const uint16_t rising = attacks & ~previous_physical_attacks;",
        ):
            self.assertIn(invariant,golden)
            self.assertIn(invariant,cand)
        for forbid in (
            "xgo_diag_right_attack_attempts",
            "xgo_diag_attack_rising_edges",
            "xgo_diag_clock_low_failures",
            "xgo_diag_clock_high_failures",
            "pending_press_edges",
            ".exchange(",
        ):
            self.assertNotIn(forbid,cand)
        self.assertIn("bool __no_inline_not_in_flash_func(emit_frame)() {",cand)
        self.assertIn("attack_edge_generation[bit].load(std::memory_order_acquire)",cand)
        self.assertIn("attack_edge_generation[bit].fetch_add(1, std::memory_order_release)",cand)

if __name__=="__main__":
    unittest.main(verbosity=2)
