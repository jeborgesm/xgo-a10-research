#!/usr/bin/env python3
"""Read-only retrospective of photographed Test48/Test49 XGO GP2040-CE error counters.

These are RP2040 local timing classifiers, not captured XGO decoded 12-bit words.
The Test49 input is the 2026-10-23 corrected CONTROLLED run, not preliminary photos.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class T48:
    err: int
    clk: int
    rel: int
    lo: int
    hi: int
    slot12: int


@dataclass(frozen=True)
class T49:
    clk: int
    slot12: int
    lo: int
    hi: int
    right_attack: int
    right_attack_error: int


T48_PHOTOS = (
    T48(350, 339, 11, 299, 40, 281),
    T48(543, 518, 25, 422, 96, 0),  # S12 not captured; placeholder unused.
    T48(628, 597, 31, 480, 117, 421),
)
T49_CONTROLLED = (
    T49(59, 40, 48, 11, 0, 0),
    T49(172, 126, 140, 32, 29, 6),
    T49(320, 226, 259, 61, 169, 28),
)


def main():
    for x in T48_PHOTOS:
        assert x.err == x.clk + x.rel
        assert x.lo + x.hi == x.clk
    for x in T49_CONTROLLED:
        assert x.lo + x.hi == x.clk
        assert x.slot12 <= x.clk
        assert x.right_attack_error <= x.right_attack

    for label, x in (("Test48 final", T48_PHOTOS[-1]),
                     ("Test49 controlled final", T49_CONTROLLED[-1])):
        # Test48/49 source groups terminal CLOCK FALL and trailing HIGH
        # timeout under slot12. Every S12 not explainable by all HIGH errors
        # has to be a terminal FALL classification.
        min_terminal_fall = max(0, x.slot12 - x.hi)
        earlier_slot_errors = x.clk - x.slot12
        assert min_terminal_fall and earlier_slot_errors
        print(f"{label}: CLK={x.clk} S12={x.slot12} "
              f"({x.slot12 / x.clk:.1%}); non-S12={earlier_slot_errors}; "
              f"S12 terminal FALL at least {min_terminal_fall}")
    for i in (1, 2):
        dclk = T49_CONTROLLED[i].clk - T49_CONTROLLED[i - 1].clk
        ds12 = T49_CONTROLLED[i].slot12 - T49_CONTROLLED[i - 1].slot12
        assert 0 <= ds12 <= dclk
        print(f"Test49 controlled photo {i}->{i + 1}: CLK +{dclk}; "
              f"S12 +{ds12} ({ds12 / dclk:.1%} of CLOCK errors)")
    x = T49_CONTROLLED[-1]
    print(f"Test49 controlled classified RIGHT+attack failures "
          f"{x.right_attack_error}/{x.right_attack} "
          f"({x.right_attack_error / x.right_attack:.1%}); "
          "does NOT equal wrong-button rate")
    print("PASS: count identities + terminal-versus-nonterminal bounds")
    print("LIMIT: no host-received bitwords nor current transparent-release error counts.")


if __name__ == "__main__":
    main()
