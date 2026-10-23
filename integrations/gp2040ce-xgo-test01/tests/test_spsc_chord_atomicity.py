#!/usr/bin/env python3
"""Validate coherent single-batch publication of attack edges without Core1 RMW.

Enumerate all legal SC interleavings of a Core0 multi-button rising-edge
publication and a Core1 six-counter snapshot. Core1 may defer an entire batch,
but may never admit only part of a simultaneous button chord. The original
per-bit snapshot has a counterexample, which this test preserves as evidence.

No ARM timing/physical guarantees: the linked-ELF audit is a separate gate.
"""
from pathlib import Path
from itertools import combinations
from math import comb
import hashlib
import unittest

ROOT=Path("integrations/gp2040ce-xgo-test01/candidates")
BASE=ROOT/"offline-test44-spsc-ram-playable/XGODriver.cpp"
NEW=ROOT/"offline-test44-spsc-coherent-ram/XGODriver.cpp"

def blobsha(path):
    d=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(d)).encode()+b"\0"+d).hexdigest()

def replay_source_diff(s):
    fixes=[
      ("""namespace { std::atomic<uint32_t> attack_edge_generation[6]{}; }
namespace { uint32_t consumed_attack_edge_generation[6]{}; }""",
       """namespace { std::atomic<uint32_t> attack_edge_generation[6]{}; }
namespace { uint32_t consumed_attack_edge_generation[6]{}; }
// A Core0-owned commit marker makes all edges from one processed Gamepad
// sample visible as a single batch. Odd = writer publishing, even = stable.
// Core1 never spins on this marker; an in-progress batch is deferred.
namespace { std::atomic<uint32_t> attack_edge_commit_seq{0}; }
namespace { uint32_t core0_attack_commit_counter = 0; }"""),
      (""" uint16_t pending = 0;
 uint32_t observed_edge_generation[6];
 for (unsigned bit = 0; bit < 6; ++bit) {
  observed_edge_generation[bit] = attack_edge_generation[bit].load(std::memory_order_acquire);
  if (observed_edge_generation[bit] != consumed_attack_edge_generation[bit])
   pending |= uint16_t(1u << bit);
 }
 // A second press during the current pulse remains pending, not discarded.""",
       """ uint16_t pending = 0;
 // All commit/counter operations are seq_cst atomics. In the single global
 // order, a complete batch either precedes both reads or follows them;
 // observing an odd/changing marker never accepts a partial button chord.
 const uint32_t commit_before = attack_edge_commit_seq.load(std::memory_order_seq_cst);
 uint32_t observed_edge_generation[6];
 for (unsigned bit = 0; bit < 6; ++bit) {
  observed_edge_generation[bit] = attack_edge_generation[bit].load(std::memory_order_seq_cst);
  if (observed_edge_generation[bit] != consumed_attack_edge_generation[bit])
   pending |= uint16_t(1u << bit);
 }
 const uint32_t commit_after = attack_edge_commit_seq.load(std::memory_order_seq_cst);
 if (commit_before != commit_after || (commit_after & 1u))
  pending = 0; // Defer all events to the next scan; NEVER send half a chord.
 // A second press during the current pulse remains pending, not discarded."""),
      (""" if (rising) {
  for (unsigned bit = 0; bit < 6; ++bit)
   if (rising & (1u << bit))
    attack_edge_generation[bit].fetch_add(1, std::memory_order_release);
 }""",
       """ if (rising) {
  // Publisher-only commit: two atomic stores, no Core1 shared RMW or lock.
  // The odd/even marker brackets *all* rising bits from this one sample.
  attack_edge_commit_seq.store(++core0_attack_commit_counter, std::memory_order_seq_cst);
  for (unsigned bit = 0; bit < 6; ++bit)
   if (rising & (1u << bit))
    attack_edge_generation[bit].fetch_add(1, std::memory_order_seq_cst);
  attack_edge_commit_seq.store(++core0_attack_commit_counter, std::memory_order_seq_cst);
 }""")
    ]
    for old,new in fixes:
        assert s.count(old)==1, f"Missing unique protected source: {old[:50]}"
        s=s.replace(old,new)
    return s

def schedule_results(mask):
    active=[i for i in range(6) if mask&(1<<i)]
    producer=[("odd",None)]+[("inc",i) for i in active]+[("even",None)]
    consumer=[("seq_start",None)]+[("read",i) for i in range(6)]+[("seq_end",None)]
    n=len(producer)+len(consumer)
    splits=0
    total=0
    for producer_slots in combinations(range(n),len(producer)):
        positions=set(producer_slots)
        ip=ic=0
        seq=0
        generation=[0]*6
        observed=[0]*6
        seq_start=seq_end=None
        for step in range(n):
            if step in positions:
                action,value=producer[ip]
                ip+=1
                if action=="odd": seq=1
                elif action=="inc": generation[value]+=1
                else: seq=2
            else:
                action,value=consumer[ic]
                ic+=1
                if action=="seq_start":seq_start=seq
                elif action=="read": observed[value]=generation[value]
                else:seq_end=seq
        raw=sum((1<<i) for i,v in enumerate(observed) if v)
        if raw not in (0,mask):
            splits+=1
        accepted = raw if (seq_start==seq_end and not(seq_end&1)) else 0
        assert accepted in (0,mask), (hex(mask),hex(accepted),seq_start,seq_end)
        # A deferred batch must still appear intact at next stable scan.
        consumed=[observed[i] if accepted&(1<<i) else 0 for i in range(6)]
        next_pending=sum((1<<i) for i in range(6)
                         if generation[i]!=consumed[i])
        assert (accepted | next_pending) == mask
        assert not (accepted & next_pending)
        total+=1
    return splits,total

class TestCoherentPublication(unittest.TestCase):
    def test_proven_ancestor_and_limited_patch(self):
        self.assertEqual(blobsha(BASE),"f38b7a6bd08a48f46f4c9cbd15018d67d7370563")
        self.assertEqual(NEW.read_text(),replay_source_diff(BASE.read_text()))
        s=NEW.read_text()
        self.assertIn("const bool hk_slot0 = (mask & 1u) != 0;",s)
        self.assertIn("constexpr uint32_t ATTACK_PULSE_US = 18000;",s)
        self.assertIn("constexpr uint32_t EDGE_TIMEOUT_US = 18;",s)
        # The diagnostics after IRQ restoration still legitimately use
        # atomic fetch_add. Guard only the true IRQ-masked critical window.
        frame=s[s.index("const uint32_t irq_state = save_and_disable_interrupts();"):
                s.index("restore_interrupts(irq_state);",
                        s.index("const uint32_t irq_state = save_and_disable_interrupts();"))]
        self.assertNotIn(".fetch_add(",frame)
        self.assertNotIn(".exchange(",frame)
        self.assertNotIn(".fetch_or(",frame)
        self.assertIn("commit_before != commit_after",frame)

    def test_all_simultaneous_button_subsets_all_sc_interleavings(self):
        total=0
        split_witnesses=0
        for mask in range(1,64):
            splits, schedules=schedule_results(mask)
            total+=schedules
            split_witnesses+=splits
        self.assertEqual(total,130680)
        self.assertGreater(split_witnesses,0)
        print(f"Enumerated {total} SC schedules, raw per-bit queue splits in "
              f"{split_witnesses}; guarded queue splits in ZERO")

    def test_rapid_repress_and_deferred_pulse_use_existing_queue_models(self):
        # The new commit marker only defers a mixed snapshot; once the
        # marker is stable, pulse queue logic is byte-for-byte unchanged.
        s=NEW.read_text()
        self.assertIn("consumed_attack_edge_generation[bit] = observed_edge_generation[bit];",s)
        self.assertIn("if (pending && !attack_pulse_mask)",s)
        self.assertIn("attack_pulse_start_us = now;",s)

if __name__=="__main__":
    unittest.main(verbosity=2)
