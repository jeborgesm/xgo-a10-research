# CPS1 Test 09 — first-frame no-input diagnostic candidate

Status: **READY FOR HARDWARE DIAGNOSTIC**

## Purpose

Test 08 proves the external FBA2012 CPS1 core reaches Street Fighter II's own startup/self-test screen but does not progress.

Static tracing also confirms XGO family 0x40 uses the normal generic run_emulator loop and invokes the active retro_run callback each iteration.

The first unique operations inside FBA2012 retro_run() are:

```text
poll_input()
BurnDrvFrame()
video_cb(...)
audio_batch_cb(...)
```

Test 09 isolates the first boundary by disabling only:

```c
poll_input();
```

inside the external CPS1 core.

## Interpretation

If SFII advances beyond the self-test:

```text
blocker = FBA2012 input polling / XGO input callback contract
```

If SFII remains frozen at the same self-test:

```text
blocker is later than input polling,
most likely BurnDrvFrame() / CPU-device execution
```

Controls are intentionally unavailable in the diagnostic core, so pause-menu behavior is not an acceptance criterion for this test.

## Baseline protection

Test 09 is based on Test 08 and changes only:

```text
cores/fbalpha2012_cps1/core.xgc
```

Unchanged:

- mapper v19;
- NES;
- external Snes9x2005;
- firmware/runtime hook;
- CPS1 list-ID gate;
- CPS2/IGS/Neo Geo stock paths;
- stock arcade cleanup.

## Diagnostic core

```text
SHA-256
27b5253406320a0712247430f5241a14145810f1f2fba7d7cfb8543d4ee57f4b
```

Build workflow:

```text
.github/workflows/xgo-cps1-test09-no-input.yml
```

Patch:

```text
tools/multicore/native_cps1/patch_test09_no_input.py
```

The diagnostic is deliberately not a production change.
