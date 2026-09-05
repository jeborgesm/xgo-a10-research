# Hardware Test 12 — MAME2000 playable, but global emulation speed is far too slow

Status: **PLAYABILITY PASS / TIMING FAILURE**

Physical XGO result:

- Street Fighter II no longer enters the TEST MENU.
- The isolated Test 12 MAME2000 state namespace successfully avoids the poisoned prior SFII configuration.
- Coin/start/gameplay controls work.
- The game can be played.
- No obvious frame dropping/choppiness is observed.
- However gameplay is dramatically too slow: character movement and the whole game feel like "underwater" slow motion.

This is qualitatively different from the embedded stock CPS1 emulator, whose problem was visible choppiness/frame dropping under load.

## Interpretation

The absence of obvious dropped frames while the entire game advances too slowly points first to a cadence/throttle mismatch rather than pure rendering overload.

Highest-priority timing seam:

- MAME2000 `retro_get_system_av_info()` reported FPS;
- MAME2000 sample-rate/core option;
- XGO family-0x40 `run_emulator()` timing/audio initialization;
- MAME2000 internal throttle/frameskip state;
- SF2000-specific libco/frontend assumptions.

Do not enable frameskip as a first response. Frameskip can hide rendering cost but will not correct a globally slow emulation clock.

## Closed items from Test 12

**CONFIRMED:**
- MAME2000 executes CPS1 on XGO.
- XGO SFII archive is compatible enough for gameplay.
- Test 11 joypad isolation works.
- SFII TEST MENU was caused by persisted per-game state/config contamination.
- fresh state namespace restores normal SFII startup/gameplay.

## Open defects

1. global CPS1 emulation speed is much too slow;
2. audio remains choppy/out of sync;
3. pause/quit needs final confirmation after timing is corrected;
4. MAME2000 save-state API remains unavailable/size zero.

## Baseline protection

Keep unchanged:

- mapper v19;
- external NES;
- external Snes9x2005;
- CPS2/IGS/Neo Geo stock fallback;
- CPS1-only list gate;
- corrected arcade runtime hook;
- stock arcade cleanup;
- Test 11 input isolation;
- Test 12 clean-state namespace.

Next candidate should target timing/audio policy only.
