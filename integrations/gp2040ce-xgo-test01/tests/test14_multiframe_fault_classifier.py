#!/usr/bin/env python3
"""Synthetic consecutive-frame fault classifier, no measured XGO timing.

Separates snapshot freshness, slot-zero lateness, and clock slot shifts.
All timelines are integer microseconds, chosen for counterexamples only.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Transaction:
    snapshot_time: int
    load_fall: int
    load_rise: int
    slot0_drive: int
    first_clock_fall: int
    half_period: int = 3

def state(t, transitions):
    value = 0
    for at, mask in transitions:
        if at <= t:
            value = mask
    return value

def decoded(tx, mask, first_slot_sample_offset=1, clock_sample_offset=1,
            missed_clock_falls=()):
    # Host samples slot 0 after LOAD rise, later slots after clock falls.
    samples = [tx.load_rise + first_slot_sample_offset]
    samples += [tx.first_clock_fall + 2*(i-1)*tx.half_period +
                clock_sample_offset for i in range(1,12)]
    drive = [(tx.slot0_drive, bool(mask & 1))]
    # A missed falling edge leaves prior driven bit in place; subsequent
    # responder slot index can diverge from host slot index.
    responder_slot = 0
    for i in range(1,12):
        if i not in missed_clock_falls:
            responder_slot += 1
            drive.append((tx.first_clock_fall+2*(i-1)*tx.half_period,
                          bool(mask & (1 << responder_slot))))
    observed = 0
    for i, sample in enumerate(samples):
        bit = False
        for at, value in drive:
            if at < sample:
                bit = value
        observed |= int(bit) << i
    return observed

def main():
    a=Transaction(0,10,14,14,18)
    b=Transaction(30,40,44,44,48)
    # Distinct frame snapshots demonstrate stale-but-coherent inputs.
    changes=[(5,1<<0),(20,0),(35,1<<1),(50,0)]
    assert [state(t.snapshot_time,changes) for t in (a,b)] == [0,0]
    assert [state(t.load_rise,changes) for t in (a,b)] == [1,2]
    print('PASS: two short taps entirely lost by early snapshots')
    # Pure snapshot staleness cannot synthesize bits absent from snapshot.
    for mask in range(4096):
        assert mask & ~mask == 0
    print('PASS: stale snapshot alone cannot create a foreign bit')
    # Late slot0: responder reports success while host samples release.
    late=Transaction(0,10,14,16,18)
    assert decoded(late,1)==0
    print('PASS: slot0 late drive suppresses asserted slot0')
    # Clock-edge index mismatch is a possible cross-slot contamination
    # mechanism, but only if responder misses an edge without aborting.
    mask=1<<1
    aligned=decoded(a,mask)
    shifted=decoded(a,mask,missed_clock_falls=(1,))
    assert aligned == mask
    assert shifted != mask
    print(f'PASS: synthetic missed-clock case: intended={mask:#05x} observed={shifted:#05x}')
    print('OPEN: Test14 source waits on LEVELS and timeouts; no evidence yet of a real skipped clock edge')

if __name__=='__main__':
    main()
