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
- stock `Select+Start` exit gesture worked
- exiting entered the stock XGO save-state menu normally
- direct A/B comparison against the original unmodified SD card showed the external-core image is brighter than stock; most notably, blacks appear gray rather than black

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

The successful `Select+Start` exit into the stock save-state UI is additional evidence that the external core is participating correctly in the stock frontend lifecycle rather than merely rendering/running in isolation. It demonstrates compatibility with the stock input/exit handling and transition back into the XGO's surrounding emulator UI.

This is therefore the first hardware-confirmed successful native external NES core execution in this research branch.

## Root cause immediately preceding success

Transactional Stage-6 bisection produced:

- 51: PASS — `GAME_INFO` write/restore
- 52: PASS — external `GFN_*` slot install/restore
- 53: FAIL — first pre-load `retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD)` call

Pinned FCEUmm defines `RETRO_DEVICE_AUTO == RETRO_DEVICE_JOYPAD`; its Auto path dereferences `GameInfo->input[port]` before `retro_load_game()` has established `GameInfo`. Removing both redundant pre-load controller calls allowed the same device/ROM to load and play normally.

## Remaining visible discrepancy: elevated black level / brightness

A direct comparison with the original stock SD card refined the initial description of 'muted colors':

- the external-core image is visibly brighter
- areas that are black on the stock emulator appear gray on the external core
- the rest of the image/gameplay is otherwise normal

This is a stronger diagnostic clue than a generic palette difference. A raised black level suggests investigating whether zero/near-zero NES palette RGB values remain zero through the external FCEUmm RGB565 path, and whether any conversion, palette-generation, or frontend pixel treatment introduces a nonzero floor. It makes a simple red/blue channel swap substantially less likely.

Next comparison targets:

- exact FCEUmm palette entries for NES black/background colors
- RGB565 packing of zero and near-zero RGB values
- stock NES core framebuffer/palette generation before the shared XGO video callback
- any brightness/gamma/range adjustment unique to either core path

This remains a post-bring-up fidelity issue, not an execution blocker.
