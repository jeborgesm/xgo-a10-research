#!/usr/bin/env python3
"""Source-order model: Core1 snapshot is read BEFORE wait_data(false).
MODEL, not measured XGO poll cadence. Deterministic counterexamples.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Frame:
    snapshot_at: int
    load_at: int

def published_at(t, transitions):
    state = 0
    for at, mask in transitions:
        if at <= t:
            state = mask
    return state

def core1_observed(frames, transitions):
    return [published_at(f.snapshot_at, transitions) for f in frames]

def expected_at_load(frames, transitions):
    return [published_at(f.load_at, transitions) for f in frames]

def main():
    frames = [Frame(0, 15000), Frame(16000, 32000)]
    transitions = [(1000, 1), (20000, 0)]
    observed = core1_observed(frames, transitions)
    expected = expected_at_load(frames, transitions)
    assert observed == [0, 1], observed
    assert expected == [1, 0], expected
    print('stale snapshot:', observed, 'state at LOAD:', expected)
    short = [(1000, 1), (3000, 0)]
    observed = core1_observed(frames, short)
    assert observed == [0, 0], observed
    print('short press between snapshots:', observed)
    held = [(1000, 1)]
    observed = core1_observed(frames, held)
    assert observed == [0, 1], observed
    print('held press:', observed)
    print('PASS: three source-order counterexamples')

if __name__ == '__main__':
    main()
