#!/usr/bin/env python3
"""Generic held-input / missing-host-frame transition MODEL for XGO debugging.

No assertion that SFII's game engine has this precise event policy.
The input sequence is a host-observed bit; synthetic false releases may
trigger repeated rising transitions downstream without RP2040 turbo.
"""

def rising_events(states):
    old = False
    events = 0
    for current in states:
        if current and not old:
            events += 1
        old = current
    return events

def run():
    physical_held = [False] + [True]*8 + [False]
    assert rising_events(physical_held) == 1
    clean_host = list(physical_held)
    assert rising_events(clean_host) == 1
    # Controller continuously holds true, but two wrong host frames appear
    # released. Returning to true forms three logical rising transitions.
    corrupt_host = [False, True, True, False, True, True, False, True, True, False]
    assert rising_events(corrupt_host) == 3
    # A genuine physical pulse entirely absent from host samples yields zero.
    missed_host = [False]*len(physical_held)
    assert rising_events(missed_host) == 0
    # An always-released button cannot generate a ghost positive from mere
    # missing samples; a false-positive bit must enter in some other layer.
    released_host = [False]*8
    assert rising_events(released_host) == 0
    print("MODEL PASS: clean held=1 rising edge, two false-release frames=3, missing all pressed frames=0")
    print("LIMIT: This tests possible transition outcomes only. Neither SFII event semantics nor actual faulty host words have been measured.")

if __name__ == "__main__":
    run()
