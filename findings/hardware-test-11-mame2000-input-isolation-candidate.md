# Hardware Test 11 candidate — MAME2000 XGO input isolation

Status: **READY FOR HARDWARE**

This is a core-only replacement over Test 10.

## Root cause addressed

MAME2000's SF2000 input layer mixes two different frontend contracts:

1. libretro joypad polling;
2. full libretro keyboard polling plus controller combinations that synthesize MAME admin keys.

XGO's proven stock callback is joypad-only and supports ports 0/1, IDs 0..15.

Test 11 therefore:

- forwards only RETRO_DEVICE_JOYPAD, index 0, ports 0/1, IDs 0..15 to XGO stock input;
- returns zero for keyboard and all unsupported device/ID requests;
- disables SF2000 MAME admin hotkeys:
  - L+START -> TAB/config;
  - R+START -> TILDE/OSD;
  - R+L -> P/pause;
  - R+SELECT -> F3/reset;
  - A -> ESC/menu cancel;
- preserves normal MAME2000 joystick mapping:
  - D-pad;
  - B/A/Y/X/L/R -> Buttons 1..6;
  - SELECT -> coin;
  - START -> start.

## Candidate identity

MAME2000 XGOC:

```text
1c37a1ea8bb6375e60e5507f024af8c71bca0ad945ec0b023ec89617991d88be
```

Staged Test 11 ZIP:

```text
90e985d37965c8c6d373802e11680b465295e62c9d1fb041f42cc05b8b9624a0
```

## Baseline protection

Unchanged from Test 10:

- firmware;
- mapper v19 resource;
- NES external path;
- Snes9x2005;
- CPS1 loader/hook;
- CPS2/IGS/Neo Geo stock fallthrough.

Only the external CPS1 core changed.

## Hardware acceptance

1. SFII boots.
2. D-pad moves player.
3. SELECT inserts coin.
4. START starts game.
5. all six attack buttons perform gameplay actions.
6. ordinary button presses do not open MAME menus/service/admin screens.
7. Start+Select still reaches stock XGO pause menu.
8. QUIT returns to list.
9. relaunch succeeds.
