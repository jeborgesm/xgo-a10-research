#!/usr/bin/env python3
"""SRC-derived XGO GOLD Handle=P1 normalizer regression (offline MODEL).

At original XGO normalizer 0x8035D53C, mode0 executes stock OR; mode1
calls hardware-passing fixed helper 0x80A398E4 to merge P2 raw into P1
and suppress P2 raw contribution. GOLD keeps this helper unchanged.
No firmware or GP2040-CE modification, and no analog hardware claim.
"""
from itertools import product

MASK = 0xFFFF
SERIAL_R = 0x1000  # host scanner's first R bit; NOT RP2040's 1<<0

def normalize(local, handle, rf1=0, rf2=0, mode=1):
    assert all(0 <= x <= MASK for x in (local, handle, rf1, rf2))
    assert mode in (0, 1)
    if mode == 1:
        return (local | handle | rf1, rf2)
    return (local | rf1, handle | rf2)

def main():
    cases = 0
    # Sixteen per-stream one-hot masks and representative mixed masks.
    masks = [0, MASK, 0x5555, 0xAAAA] + [1 << bit for bit in range(16)]
    for local, handle, rf1, rf2 in product(masks, masks, (0, SERIAL_R), (0, SERIAL_R)):
        for mode in (0, 1):
            p1, p2 = normalize(local, handle, rf1, rf2, mode)
            assert (p1, p2) == ((local | handle | rf1, rf2) if mode
                                else (local | rf1, handle | rf2))
            assert not (p1 & ~(local | handle | rf1))
            assert (p2 == rf2 if mode else not (p2 & ~(handle | rf2)))
            cases += 1
    assert normalize(SERIAL_R, 0) == (SERIAL_R, 0)
    assert normalize(0, SERIAL_R) == (SERIAL_R, 0)
    assert normalize(0, 0) == (0, 0)
    assert normalize(0, SERIAL_R, mode=0) == (0, SERIAL_R)

    # Artificial bad frames on P2 can generate false releases at logical P1
    # if there is no simultaneous built-in P1 hold of the same bit.
    observed = [SERIAL_R, SERIAL_R, 0, SERIAL_R, SERIAL_R, 0, SERIAL_R]
    merged = [normalize(0, x)[0] for x in observed]
    rising = sum(bool(x & SERIAL_R) and not bool((merged[i-1] if i else 0) & SERIAL_R)
                 for i, x in enumerate(merged))
    assert rising == 3
    assert all(normalize(SERIAL_R, x)[0] & SERIAL_R for x in observed)

    # NEW HW context: user is playing with local P1 buttons, while the external
    # GP2040 is connected but PHYSICALLY UNTOUCHED and Handle=P1 is selected.
    # Clean idle electrical/host decoding must contribute ZERO. A spurious
    # decoded raw Handle bit still enters logical P1 despite no GP2040 press.
    LOCAL_NON_R = 0x0200   # generic non-R local held input
    physical_handle_unpressed = 0
    decoded_handle_clean = 0
    decoded_handle_false_r = SERIAL_R  # hypothetical L0 error, not observed bit
    assert physical_handle_unpressed == 0
    assert normalize(LOCAL_NON_R, decoded_handle_clean, mode=1)[0] == LOCAL_NON_R
    assert normalize(LOCAL_NON_R, decoded_handle_false_r, mode=1)[0] == (LOCAL_NON_R | SERIAL_R)
    assert normalize(LOCAL_NON_R, decoded_handle_false_r, mode=0) == (LOCAL_NON_R, SERIAL_R)
    # Competing explanation: built-in B15 source false R reaches P1 in BOTH modes.
    assert normalize(LOCAL_NON_R | SERIAL_R, 0, mode=1)[0] & SERIAL_R
    assert normalize(LOCAL_NON_R | SERIAL_R, 0, mode=0)[0] & SERIAL_R

    print(f"PASS: {cases} P1/P2/RF routing cases, zero phantom bits from the OR alone")
    print("PASS: either serial channel's false R can reach P1; mode0 keeps handle on P2")
    print("PASS: modeled transient P2 false releases can retrigger P1 presses")
    print("PASS: built-in P1 active + untouched external: clean raw Handle cannot ghost; a falsely decoded Handle bit reaches P1 only in P1 mode")
    print("LIMIT: SRC-derived logical oracle; synthesized input corruption, not evidence it occurred on hardware")

if __name__ == "__main__":
    main()
