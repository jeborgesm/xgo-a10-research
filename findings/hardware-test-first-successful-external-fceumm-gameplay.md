# Hardware finding: first successful external FCEUmm gameplay on XGO A10

## Status

**Confirmed on hardware.**

The XGO A10 successfully loaded and ran Contra through the external FCEUmm core packaged as `cores/fceumm/core.xgc`, with the stock XGO firmware patched only to intercept the NES launch path and load the external core.

## Hardware observation

Test configuration:

- same experimental patched `bios/bisrv.asd` used throughout the native NES bring-up series
- only `/cores/fceumm/core.xgc` replaced
- test ROM: Contra, same ROM used for the staged return ladder
- full-path Stage-0 build from source commit `04ee153bfaf685241dbfbe5d899e74137014cc2c`
- controller pre-load calls removed after transactional substage 53 proved they dereferenced FCEUmm `GameInfo` before `retro_load_game()`

Observed result:

- game loaded successfully
- gameplay started normally
- controls worked
- audio worked
- timing/gameplay appeared normal
- only obvious difference versus the stock emulator was that colors appeared somewhat muted

## Why this proves external-core execution

The tested build is not a return probe and does not intentionally fall back to the stock NES emulator after a successful XGOC load.

The active control flow is:

```text
stock XGO NES menu
  -> stock ROM preload
  -> patched run_game() NES call site
  -> injected loader @ 0x80001500
  -> /cores/fceumm/core.xgc
  -> external entry @ 0x87000000
  -> XGO native frontend
  -> external FCEUmm libretro lifecycle
  -> stock XGO video/audio/input callbacks through bidirectional GP veneers
```

Earlier continuity testing separately proved the loader/XGOC/entry/return boundary. The successful full-path build now proves that the external core can continue through `retro_init()`, `retro_load_game()`, stock frontend AV setup, `retro_run()`, stock video/audio callbacks, and stock input callbacks sufficiently to play a real NES title.

This is therefore the first hardware-confirmed successful native external NES core execution in this research branch.

## Root cause immediately preceding success

Transactional Stage-6 bisection produced:

- 51: PASS — `GAME_INFO` write/restore
- 52: PASS — external `GFN_*` slot install/restore
- 53: FAIL — first pre-load `retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD)` call

Pinned FCEUmm defines `RETRO_DEVICE_AUTO == RETRO_DEVICE_JOYPAD`; its Auto path dereferences `GameInfo->input[port]` before `retro_load_game()` has established `GameInfo`. Removing both redundant pre-load controller calls allowed the same device/ROM to load and play normally.

## Remaining visible discrepancy

The user reported that colors look somewhat muted compared with the stock XGO NES emulator.

Because gameplay, timing, audio, and input are otherwise normal, the next investigation should focus specifically on the video color path:

- FCEUmm palette generation
- RGB565 packing/channel order
- stock XGO video callback expectations
- any stock NES-specific color conversion or palette treatment performed before the shared display path

This should be treated as a post-bring-up fidelity issue, not as evidence that the external core is failing to run.
