# Hardware Test 13 — adaptive frameskip works, but MAME2000 remains slower than stock

Status: **TIMING EXPERIMENT FAIL / MAME2000 NOT ACCEPTABLE AS CPS1 PERFORMANCE REPLACEMENT**

Physical XGO result:

- XGO adaptive frameskip is visibly active in Test 13.
- Frame skips are now noticeable.
- Despite skipping render work, gameplay still feels slow.
- Overall CPS1 speed remains slightly slower than the embedded stock XGO arcade emulator this experiment is intended to replace.

## Conclusion

The Test 13 bridge works mechanically:

```text
stock run_emulator() lag detector
 -> external MAME2000 frameskip adapter
 -> MAME2000 skips expensive draw_screen()/CPS1 vh_update work
```

but the recovered rendering budget is not enough to bring MAME2000 to or above stock XGO performance.

This strongly indicates that the primary bottleneck is not only video rendering. Portable MAME2000 CPU/device emulation on HC15xx/MIPS32 is too expensive for the target use case.

## Performance classification

MAME2000 on XGO:

- content compatibility: PASS
- CPS1 execution: PASS
- controls: PASS after Test 11
- SFII state isolation: PASS after Test 12
- adaptive frameskip: PASS
- real-time performance: FAIL
- better than stock XGO CPS1: FAIL

Therefore MAME2000 should remain documented as a valuable external-core proof, not promoted as the CPS1 replacement.

## Next direction

Stop spending cycles tuning MAME2000 frameskip.

Return to the dedicated FBA2012 CPS1 lineage and investigate alternate CPU backends/compile-time options, specifically whether a faster portable 68000 core such as C68K or another non-Musashi backend is available and usable on MIPS32.

The original FBA2012 hardware failure was a first-frame execution stall, but its much smaller CPS1-specialized design remains more promising for performance if the CPU backend/runtime incompatibility can be resolved.

In parallel, survey other SF2000/GB300 low-end arcade cores, but require evidence that they can plausibly beat stock XGO CPS1 before generating more hardware packages.

## Baseline protection

Do not change the proven mapper v19 + NES + Snes9x2005 baseline or stock CPS2/IGS/Neo Geo fallback while continuing CPS1 research.
