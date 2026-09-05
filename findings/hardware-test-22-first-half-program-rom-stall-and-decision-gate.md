# Hardware Test22 — stall is in first half of SFII 68000 program ROMs

Hardware result:

- SFII remains indefinitely on `Loading.....`.
- Test22 forces failure after the first two 68000 ROM pairs (first four program ROMs).
- Test20 calibrated a reached forced failure as `Loading..... -> black screen -> freeze`.

Therefore Test22's forced return was not reached.

The current FBA2012 + native-MIPS A68K path stalls within the first two SFII program-ROM pairs:

1. `sf2e_30g.11e` + `sf2e_37g.11f`
2. `sf2e_31g.12e` + `sf2e_38g.12f`

This is a real localization result, but it does not yet advance the project goal of outperforming the stock CPS1 experience.

## Decision gate

Known hardware baselines:

- Stock XGO CPS1: functional; can become laggy.
- External FBA2012 / Musashi: content path works; SFII reaches self-test; stalls during first frame.
- External MAME2000: boots and plays; controls repaired; slower than stock even with adaptive frameskip.
- External FBA2012 / native-MIPS A68K: stalls during second ROM-load pass, now localized to first two 68000 ROM pairs.

Do not continue blind per-ROM bisection without a concrete mechanism hypothesis.

Recommended next direction:
1. preserve stock CPS1 as usable baseline;
2. keep external CPS1 experiments isolated;
3. analyze why enabling A68K changes behavior before CPU execution, especially binary layout / heap / ROM destination memory, because A68K has not run yet;
4. compare Test08 Musashi vs Test14/15 A68K memory maps and allocations rather than assuming a ROM-file problem;
5. investigate stock CPS1 runtime/performance path as a potentially lower-risk optimization target.
