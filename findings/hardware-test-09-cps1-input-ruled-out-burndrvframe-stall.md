# Hardware Test 09 — input ruled out; FBA2012 stalls inside first frame

Status: **HARDWARE FAIL / INPUT PATH EXONERATED**

Observed on physical XGO:

- Street Fighter II shows the same frozen CPS1 self-test image as Test 08.
- Other CPS1 titles remain on a black screen and freeze.
- Test 09 intentionally disabled FBA2012 `poll_input()` inside `retro_run()`.
- Behavior is unchanged from Test 08.

## Conclusion

The XGO <-> FBA2012 input callback contract is **not** the cause of the startup stall.

The failure boundary is now:

```text
retro_load_game() succeeds far enough to initialize the selected CPS1 driver
run_emulator() calls external retro_run()
poll_input() skipped
-> BurnDrvFrame() / CPS1 CPU-device execution does not return/progress normally
```

For SFII, a self-test frame is already visible when the stall occurs.
For other games, the same failure happens before a useful frame is rendered, leaving black video.

## Next investigation

Trace:

- CPS1 `BurnDrvFrame()` implementation;
- 68000 execution backend selected by the SF2000 build;
- Z80 execution/timer coupling;
- sound/timer callbacks that run inside the first frame;
- SF2000-specific FBA2012 history and known limitations.

In parallel, evaluate MAME2000 as an alternative low-end CPS1 core. The upstream SF2000 multicore repository explicitly described its general FBA2012 integration as:

```text
working but major issues, not to release
```

This raises the probability that the current failure is a known FBA-on-HC15xx weakness rather than an XGO frontend defect.

## Baseline protection

Remain unchanged:

- mapper v19;
- external NES;
- external Snes9x2005;
- CPS2/IGS/Neo Geo stock fallback;
- CPS1-only list discriminator;
- corrected arcade runtime hook;
- stock arcade cleanup.

Do not alter the shared runtime based on this result.
