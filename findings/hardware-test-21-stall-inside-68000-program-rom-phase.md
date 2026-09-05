# Hardware Test21 — stall is inside CPS1 68000 program-ROM phase

Hardware result for SFII:

- Device remains indefinitely on `Loading.....`.
- Test21 forces `return 1` immediately after the complete 68000 program-ROM loop and before graphics loading.
- Test20 calibrated a reached forced-failure point as `Loading..... -> black screen -> freeze`.

Interpretation:

The Test21 forced return was not reached.

Therefore the stall is inside the 68000 program-ROM phase of the second `Cps1LoadRoms(1)` pass, before graphics loading begins.

Next step: identify SFII's exact 68000 ROM ordering from the pinned FBA2012 driver and add zero-I/O forced-return probes after selected `BurnLoadRom()` calls to bisect the failing ROM operation.
