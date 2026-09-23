# Test127/Test130 root cause — signed ADDIU pathname pointer construction

Date: 2026-09-23
Status: **BIN/SRC root-cause closure**

The GB execution island introduced at 0x80A39050 contains a deterministic pathname
pointer bug. This explains Test127, Test128 and Test130 failing before helper entry.

## Fault

The Test127 builder placed strings at:
- 0x80A390C0 = /mnt/sda1/GB/refresh.xgc
- 0x80A390E0 = /mnt/sda1/GB/catalog.xgc

but emitted each pointer using:

    lui   a0, 0x80A3
    addiu a0, a0, 0x90C0   # or 0x90E0

MIPS ADDIU sign-extends its 16-bit immediate. 0x90C0 and 0x90E0 have bit 15 set.

Therefore the actual effective addresses are:

    0x80A30000 + signext(0x90C0) = 0x80A290C0
    0x80A30000 + signext(0x90E0) = 0x80A290E0

not the intended 0x80A390C0 / 0x80A390E0.

The correct high half for ADDIU relocation is 0x80A4:

    lui   a0, 0x80A4
    addiu a0, a0, 0x90C0   -> 0x80A390C0

and likewise for 0x90E0.

## Why MD worked

The protected MD body already uses the correct compensated form:

    lui a0,0x80A4
    addiu a0,a0,0x8980

0x8980 is negative as a signed 16-bit immediate, so 0x80A4 is required to land at
0x80A38980. FC/SFC/MD therefore preserved the standard MIPS HI16/LO16 relocation
rule. The new GB builder incorrectly used the raw address high half.

## Hardware-result explanation

Test130's trivial helper could never return -1, yet hardware reported Refresh Failed.
With the malformed pointer, the generic runner passes 0x80A290C0 to fopen instead
of the real pathname at 0x80A390C0. The failure therefore occurs at the runner's
pre-helper open boundary exactly as Test130 demonstrated.

This removes the GB materializer, helper-size, catalog, and heap-state hypotheses
from the current root cause.

## Required fix

Change only the two GB pathname LUI instructions:
- 0x80A39050: 0x3C0480A3 -> 0x3C0480A4
- 0x80A3907C: 0x3C0480A3 -> 0x3C0480A4

No protected FC/SFC/MD/CLASSIC path changes are required.

The Test127 builder must use a HI16 helper that adds 0x10000 before taking the high
half whenever the LO16 used by ADDIU has bit 15 set.
