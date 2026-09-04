# Hardware Test 08 — CPS1 content handoff reaches game self-test, frame loop stalls

Status: **HARDWARE PARTIAL PASS; CONTENT PATH CLOSED ENOUGH TO INITIALIZE CPS1**

Observed on physical XGO with Test 08:

- CPS1 selection no longer immediately returns to the list;
- no stock per-file "Loading ..." feedback is shown;
- Street Fighter II reaches its own CPS1 startup/RAM self-test screen;
- execution remains frozen on that screen and does not progress into gameplay.

The attached hardware photograph shows the SFII board self-test display rendered on the XGO LCD.

## Interpretation

This is materially different from Tests 06/07.

Test 08's use of the stock-produced arcade path globals is sufficient for FBA2012 to locate/load enough of the real ROM set to initialize the game and render its startup state.

Therefore the primary content-path blocker is no longer "wrong .zfb wrapper path."

The new failure boundary is later:

```text
external FBA2012 retro_load_game()
  -> CPS1 driver/ROM initialization succeeds far enough to render self-test
  -> sustained frame execution / runtime loop does not progress
```

## Important visual distinction

The original XGO arcade emulator displays frontend-driven per-file loading feedback because stock XGO performs its own archive preprocessing before launching the embedded FBA runtime.

External FBA2012 opens the real ZIP itself, so those stock loading messages are not expected.

Their absence is not evidence of failed ROM loading once the CPS1 self-test is visibly rendered.

## Next target

Trace stock `run_emulator()` family `0x40` behavior and compare it to FBA2012's requirements:

- whether family 0x40 has special AV/audio initialization;
- whether `retro_get_system_av_info()` is skipped/overridden;
- whether stock frame scheduling calls the active `retro_run` callback for arcade;
- whether FBA2012's audio callback expectations can block frame progression;
- whether the stock arcade wrapper installs a non-generic frameskip callback/flag;
- whether active callback slots differ from NES/SNES.

Do not change content-path resolution until runtime-loop evidence requires it.

## Baseline remains protected

- mapper v19 unchanged;
- NES unchanged;
- Snes9x2005 unchanged;
- CPS2/IGS/Neo Geo stock fallback unchanged;
- CPS1-only list gate unchanged;
- stock arcade cleanup unchanged.
