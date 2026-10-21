#!/usr/bin/env python3
"""Offline behavioral oracle for XGO Handle-as-P1 routing; no firmware writes.

Run: python3 tools/handle_p1_routing_oracle.py
Masks are active-high *after* the scanner has decoded the active-low wire.
This is a specification test, NOT MIPS execution or hardware verification.
"""
from itertools import product

BITS = tuple(1 << i for i in range(12))
FULL_MASK = (1 << 12) - 1

def route(local_p1: int, handle_p2: int, *, external_as_p1: bool) -> tuple[int, int]:
    """Physical XGO: built-in P1 and one external Handle port; no RF input."""
    if external_as_p1:
        return (local_p1 | handle_p2, 0)
    return (local_p1, handle_p2)

def test() -> None:
    patterns = (0, FULL_MASK, *BITS, 0x555, 0xAAA, 0x123, 0x842)
    count = 0
    for local, handle, mode in product(patterns, patterns, (False, True)):
        p1, p2 = route(local, handle, external_as_p1=mode)
        assert (p1, p2) == ((local | handle, 0) if mode else (local, handle))
        assert p1 & ~FULL_MASK == 0 and p2 & ~FULL_MASK == 0
        assert (p1 & local) == local
        if mode:
            assert (p1 & handle) == handle and p2 == 0
        else:
            assert p2 == handle
        count += 1
    print(f"PASS: {count} routing combinations; no firmware touched")

if __name__ == "__main__":
    test()
