#!/usr/bin/env python3
"""Offline XGO 12-bit state contract. MODEL only, not hardware waveform evidence."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Sample:
    at_us: int
    mask: int

def state_at(samples, at_us):
    return next((s.mask for s in reversed(samples) if s.at_us <= at_us), 0)

def serialize(mask):
    return tuple((mask >> slot) & 1 for slot in range(12))

def decode(bits):
    return sum(bit << slot for slot, bit in enumerate(bits))

def run():
    for mask in range(4096):
        assert decode(serialize(mask)) == mask

    # Generic slots only: game-specific HP/HK assignments are not yet verified.
    a, b, c, d = (1 << i for i in (2, 3, 4, 5))
    timeline = [Sample(0, 0), Sample(100, c), Sample(200, 0),
                Sample(300, d), Sample(400, 0), Sample(500, a),
                Sample(5000, 0), Sample(6000, b), Sample(6050, 0)]
    loads = [50, 150, 250, 350, 450, 550, 1000, 2000,
             4900, 5100, 6010, 6100]
    expected = [0, c, 0, d, 0, a, a, a, a, 0, b, 0]
    assert [decode(serialize(state_at(timeline, t))) for t in loads] == expected

    # Old snapshot before waiting for LOAD misses a press present at LOAD.
    assert state_at(timeline, 5900) == 0
    assert state_at(timeline, 6010) == b
    # No press cache: a tap wholly between two LOAD polls is unobserved.
    assert [state_at(timeline, t) for t in (5900, 6100)] == [0, 0]

    # Model a single-slot shift: foreign button identity despite stable input.
    bits = serialize(a)
    assert decode((0,) + bits[:-1]) == b
    assert all(decode(serialize(a)) == a for _ in range(1000))
    print("PASS: 4096 masks, held states, transitions, no-cache taps, shift discriminator")
    print("MODEL ONLY: not proof of a real phase shift or host sample times")

if __name__ == "__main__":
    run()
