#!/usr/bin/env python3
"""XGO two-sampler and P1-conditional P2 slot-0 MODEL. Not hardware proof.

Core0 publishes latest physical state; the 16ms XGO host samples at an
independent cadence. Parameterized first-slot DATA settling is speculative.
No firmware changed, no game-specific behavior modeled.
"""
from bisect import bisect_right

OLED_FULL_MS = 1025 * 9 / 400000 * 1000
OLED_PAGE_MS = 129 * 9 / 400000 * 1000
XGO_POLL_MS = 16.03

def host_observes_pulse(duration_ms, core_period_ms, host_period_ms, core_phase_ms, host_phase_ms):
    """Physical press [0,duration). Last Core0 sample controls host word."""
    core_times, core_states = [], []
    scan=core_phase_ms
    while scan <= duration_ms + 2*(core_period_ms + host_period_ms):
        core_times.append(scan)
        core_states.append(0 <= scan < duration_ms)
        scan += core_period_ms
    host=host_phase_ms
    while host < duration_ms + 2*(core_period_ms + host_period_ms):
        prev=bisect_right(core_times,host)-1
        if prev >= 0 and core_states[prev]:
            return True
        host += host_period_ms
    return False

def grid_coverage(duration_ms, core_period_ms, host_period_ms, steps=40):
    """Uniform deterministic phase *grid*, not measured input statistics."""
    observed=0
    for a in range(steps):
        for b in range(steps):
            observed += host_observes_pulse(duration_ms, core_period_ms, host_period_ms,
                 a/steps*core_period_ms, b/steps*host_period_ms)
    return observed, steps*steps

def first_slot0_bits(correct_mask, p1_slot0_released, rise_delay_us,
                     first_sample_offset_us, extra_p1_low_path_us):
    """Assumed DATA digital threshold low tail. Timing is unmeasured."""
    offset = first_sample_offset_us
    if not p1_slot0_released:
        offset += extra_p1_low_path_us
    return correct_mask | (1 if offset < rise_delay_us else 0)

def run():
    for period in (OLED_FULL_MS,OLED_PAGE_MS):
        for a in range(40):
            for b in range(40):
                assert not host_observes_pulse(0, period, XGO_POLL_MS,
                    a/40*period, b/40*XGO_POLL_MS)
        for a in range(20):
            for b in range(20):
                assert host_observes_pulse(250, period, XGO_POLL_MS,
                    a/20*period, b/20*XGO_POLL_MS)
    print(f"MODEL nominal I2C full={OLED_FULL_MS:.3f}ms/page={OLED_PAGE_MS:.3f}ms; host ~{XGO_POLL_MS:.2f}ms")
    print("Tap       full-OLED coverage     paged-OLED coverage (40x40 phase grid)")
    for duration in (4,8,12,16,20,24,40):
        a,n=grid_coverage(duration,OLED_FULL_MS,XGO_POLL_MS)
        b,_=grid_coverage(duration,OLED_PAGE_MS,XGO_POLL_MS)
        assert b >= a
        print(f"{duration:2d}ms       {a}/{n}={100*a/n:.1f}%          {b}/{n}={100*b/n:.1f}%")
    assert first_slot0_bits(0x820,True,.20,.10,.20) == 0x821
    assert first_slot0_bits(0x820,False,.20,.10,.20) == 0x820
    assert first_slot0_bits(0x820,True,0,.10,.20) == 0x820
    assert first_slot0_bits(0x820,False,0,.10,.20) == 0x820
    print("MODEL P1-dependent slot0: assumed low-tail .20us/early read .10us/extra P1 path .20us -> false R only when P1 idle")
    print("LIMIT: timings beyond nominal I2C / ~16ms host, actual P2 voltage, Core0 scan cadence, SFII binding and user input phases are UNMEASURED")

if __name__ == "__main__":
    run()
