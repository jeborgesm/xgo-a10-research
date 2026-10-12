#!/usr/bin/env python3
"""Synthetic, source-guided Test14 LOAD/CLOCK waveform model (not hardware timing)."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Host:
    load_start: int = 10
    load_end: int = 14
    first_fall: int = 18
    half_period: int = 3
    sample_offset: int = 1

    def clock(self, t):
        if t < self.first_fall:
            return 1
        return 0 if ((t - self.first_fall) // self.half_period) % 2 == 0 else 1

    def load(self, t):
        return 0 if self.load_start <= t < self.load_end else 1

    def sample_times(self):
        return [self.load_end + self.sample_offset] + [
            self.first_fall + 2 * (i - 1) * self.half_period + self.sample_offset
            for i in range(1, 12)
        ]

@dataclass
class Result:
    mask: int
    decoded: int
    complete: bool
    stage: str
    driven: tuple

def decode(host, mask, drives, complete, stage):
    decoded = 0
    for i, sample in enumerate(host.sample_times()):
        active = False
        for at, value in drives:
            if at < sample:
                active = value
        if active:
            decoded |= 1 << i
    return Result(mask, decoded, complete, stage, tuple(drives))

def simulate(host, mask, poll_start=0, irq_delay=0, deadline=12):
    drives = []
    t = poll_start
    while t <= poll_start + 20000 and host.load(t):
        t += 1
    if t > poll_start + 20000:
        return Result(mask, 0, False, "load_timeout", ())
    t += irq_delay
    start = t
    while t <= start + deadline and not host.load(t):
        t += 1
    if t > start + deadline:
        return Result(mask, 0, False, "release_timeout", ())
    drives.append((t, bool(mask & 1)))
    for slot in range(1, 13):
        start = t
        while t <= start + deadline and host.clock(t):
            t += 1
        if t > start + deadline:
            return decode(host, mask, drives, False, f"clock_fall_{slot}")
        drives.append((t, bool(mask & (1 << slot)) if slot < 12 else False))
        if slot < 12:
            start = t
            while t <= start + deadline and not host.clock(t):
                t += 1
            if t > start + deadline:
                return decode(host, mask, drives, False, f"clock_rise_{slot}")
    # Source ignores result of final clock-high wait.
    return decode(host, mask, drives, True, "success")

def main():
    host = Host()
    nominal = [simulate(host, mask) for mask in range(4096)]
    good = sum(r.complete and r.decoded == r.mask for r in nominal)
    print("nominal masks matching:", good, "/4096")
    delayed = simulate(host, 1, irq_delay=5)
    print("delayed entry slot0:", delayed)
    mismatches = []
    for first in range(15, 36):
        for delay in range(10):
            result = simulate(Host(first_fall=first), 1, irq_delay=delay)
            if result.decoded != 1:
                mismatches.append((first, delay, result.stage, result.decoded))
    print("slot0 synthetic mismatch cases:", len(mismatches), "example:", mismatches[:6])
    assert good == 4096
    assert delayed.complete and delayed.decoded != delayed.mask
    print("PASS: synthetic model assertions")

if __name__ == "__main__":
    main()
