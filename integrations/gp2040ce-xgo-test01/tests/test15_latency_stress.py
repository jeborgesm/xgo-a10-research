#!/usr/bin/env python3
"""Deterministic synthetic Core0 publication / Core1 LOAD latency stress.
No claim about actual XGO timing, only relative freshness under identical timeline.
"""
import random

def value_at(t, changes):
    current = 0
    for when, value in changes:
        if when > t:
            break
        current = value
    return current

def run(seed=14015, n=100000):
    rng = random.Random(seed)
    old_stale = new_stale = corrected = both = 0
    for _ in range(n):
        snap = rng.randrange(0, 10000)
        load = snap + rng.randrange(0, 20001)
        change = snap + rng.randrange(-100, 20101)
        before = rng.randrange(4096)
        after = rng.randrange(4096)
        if before == after:
            after ^= 1
        changes = [(0, before), (change, after)] if change >= 0 else [(0, after)]
        old = value_at(snap, changes)
        new = value_at(load, changes)
        expected = value_at(load, changes)
        if old != expected:
            old_stale += 1
        if new != expected:
            new_stale += 1
        if old != expected and new == expected:
            corrected += 1
        if old == expected and new == expected:
            both += 1
    assert old_stale > 0 and new_stale == 0 and corrected == old_stale
    print(f'PASS {n} deterministic schedules seed={seed}: golden stale={old_stale}, candidate stale={new_stale}, corrected={corrected}, both current={both}')
    print('MODEL only: host LOAD-low acquisition and Core0 publication are idealized; no cycle timing modeled')

if __name__ == '__main__':
    run()
