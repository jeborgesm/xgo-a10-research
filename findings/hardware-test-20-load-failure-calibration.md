# Hardware Test20 — immediate load failure reaches black screen

Hardware result for SFII:

1. Game selected.
2. XGO displays `Loading.....`.
3. Screen transitions to black.
4. Device then freezes on black.

Test20 forces `Cps1LoadRoms(1)` to return failure immediately on entry.

## Interpretation

This calibrates the frontend failure presentation.

A deliberate failure from inside the second ROM-load pass does **not** remain on the `Loading.....` screen. It progresses to a black screen before freezing.

Therefore Test19's distinct result — remaining indefinitely on `Loading.....` with a forced `return 1` immediately *after* `Cps1LoadRoms(1)` — means execution did not reach that return.

Conclusion: the Test15/A68K+ABI build stalls inside the second `Cps1LoadRoms(1)` pass.

Next zero-I/O probe: force failure immediately after the 68000 program-ROM loading phase. If hardware reaches black, program ROM loading completes and the blocker is later. If it remains on Loading, the blocker is within the program ROM phase.
