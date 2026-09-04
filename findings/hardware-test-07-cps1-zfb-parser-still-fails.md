# Hardware Test 07 — CPS1 ZFB parser still returns immediately

Status: **HARDWARE FAIL; STALE-COPY ERROR RULED OUT**

The user tested Test 07 twice, explicitly recopying the package to ensure the latest files were in use.

Observed behavior is unchanged from Test 06:

- selecting a CPS1 title shows the stock `Loading......` message;
- control immediately returns to the CPS1 game list;
- external CPS1 gameplay does not begin;
- this is reproducible across repeated copies of the Test 07 package.

Therefore the failure is genuine and not attributable to accidentally testing stale Test 06 files.

## Interpretation

The Test 07 frontend still returns before entering FBA2012.

The tolerant parser that probes both 59904-byte and 59905-byte thumbnail boundaries therefore still does not match the actual XGO .zfb content layout available through `ROM_BUFFER`.

This invalidates the assumption that the SF2000-family wrapper geometry can be applied directly to XGO without direct byte-level confirmation.

## Required next step

Stop inferring .zfb structure from related-device documentation.

Recover the XGO-specific wrapper contract directly from:

1. preserved card artifacts, if actual .zfb samples are available;
2. stock firmware preprocessing code that consumes the selected .zfb before the arcade runtime wrapper;
3. any stock in-memory structure populated from that preprocessing stage.

The CPS1 runtime hook/list-ID separation remains valid and should not be changed while investigating content handoff.

## Baseline protection

Do not modify:

- mapper v19;
- external Snes9x2005;
- NES path;
- CPS2/IGS/Neo Geo stock fallback;
- corrected CPS1 runtime hook;
- stock arcade cleanup path.

The next candidate should ideally change only CPS1 `core.xgc` or, if necessary, a CPS1-only content adapter.
