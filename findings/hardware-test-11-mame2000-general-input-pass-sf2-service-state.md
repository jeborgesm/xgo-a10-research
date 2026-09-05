# Hardware Test 11 — general MAME2000 input works; SFII enters persisted service mode

Status: **GENERAL INPUT PASS / SFII-SPECIFIC CONFIGURATION SUSPECTED**

Hardware observations:

- Cadillacs & Dinosaurs can be played normally.
- Gameplay controls are usable.
- Audio is choppy and appears out of sync.
- Street Fighter II accepts coin and Start, but then enters the game's own TEST MENU.
- The pictured menu is the CPS1/SFII service/test menu, not the generic MAME UI.

## Why this is no longer a general input-mapping failure

Test 11 changed MAME2000 so:

- keyboard-device queries return zero;
- SF2000 controller-to-MAME-admin hotkeys are disabled;
- ordinary joypad B/A/Y/X/L/R, D-pad, Select and Start remain.

Cadillacs & Dinosaurs working normally on the same core confirms that basic XGO -> libretro -> MAME joystick translation is viable.

## SFII-specific persistent service mode

The MAME2000 SFII driver defines:

```text
DSWC bit 0x80
PORT_SERVICE(... IP_ACTIVE_LOW)
keyboard default: F2
```

MAME2000 persists per-game input/DIP state in:

```text
<core_save_directory>/cfg/<game>.cfg
```

For SFII:

```text
.../mame2000/cfg/sf2.cfg
```

During Test 10 the broken input path exposed MAME configuration/admin UI. It is therefore plausible that SFII's Service Mode DIP was toggled and persisted in `sf2.cfg`.

Test 11 fixes live input but still reads the same persisted configuration, so the bad service-mode state can survive indefinitely.

The fact that Cadillacs works normally while SFII alone enters its game-level TEST MENU strongly supports per-game persisted state over a global input bug.

## Test 12 policy

Do not delete or overwrite Test 10/11 state.

Instead, build MAME2000 to use a fresh XGO-specific state namespace so no existing cfg/nvram/high-score data can be loaded.

If SFII starts normally under the fresh namespace, persisted `sf2.cfg` contamination is confirmed.

## Audio

Cadillacs gameplay also proves enough runtime to assess audio:

- sound is choppy;
- sound is out of sync.

Do not combine the audio fix with Test 12. First close SFII service-mode state cleanly; then investigate sample cadence/rate separately.
