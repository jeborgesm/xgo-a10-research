# Hardware Test 06 — immediate CPS1 return and ZFB boundary correction

Status: **TEST 06 FAILED BEFORE CORE ENTRY; TEST 07 CANDIDATE BUILT**

Hardware observation:
- selecting any CPS1 title shows stock `Loading......`;
- execution immediately returns to the CPS1 list;
- no RAM/self-test screen appears;
- CPS2 remains on the stock path.

Interpretation:
- the CPS1 list discriminator and corrected runtime hook remain valid;
- Test 06 failed inside the external frontend before `retro_load_game()`;
- the only new early-return gate in Test 06 was the .zfb wrapper parser.

Root cause:
- Test 06 hard-coded a 59,904-byte arcade thumbnail boundary;
- independent SF2000-family documentation specifies 59,905 bytes before the four-zero separator;
- the XGO failure mode is exactly what the off-by-one check predicts: byte 59,904 is still thumbnail data, so the four-zero separator test fails and the frontend returns.

Test 07 changes only the CPS1 XGOC. It probes both family layouts:
```text
59904 + four zero bytes + valid *.zip basename
59905 + four zero bytes + valid *.zip basename
```
and accepts only a bounded, NUL-terminated .zip basename.

No firmware, mapper, SNES, CPS2/IGS/NeoGeo dispatch or stock arcade cleanup bytes change.
