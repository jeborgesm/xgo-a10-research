# Arcade Test23 — family-style API-table MAME2000 candidate

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **CI PASS; hardware test pending**

## Purpose

Replace the failing custom MAME ownership model with the family-proven SF2000/GB300 architecture while preserving golden Test08 behavior.

## Architecture

Golden Test08 remains the firmware baseline.

Only fifth Arcade / list ID 11 is redirected.

```text
list 7-10
  -> stock XGO FBA
  -> unchanged

list 11
  -> XGO external loader
  -> MAME2000 image @ 0x87000000
  -> family-style retro_core_t API table
  -> install XGO stock callbacks / gfn_retro_* slots
  -> golden run_emulator()
```

The family-style core is built from:
- `madcock/libretro-mame2000` commit
  `231929ab69e7538bc1d98f59634b8d7fee2ddde7`
- exact SF2000 Codescape toolchain
- existing XGO admin/service-key patch
- existing Test12 isolated-state patch

The core links cleanly with **zero undefined symbols**.

## Non-regression preservation

This candidate is composed from golden Test08 and does NOT restore old Test12 firmware or old run_emulator.

Therefore the candidate retains:
- Volume OSD v8 and its game-session hooks;
- gray OSD border and timeout behavior;
- CPS1 sibling scheduler transplant;
- mapper v19;
- native SNES work;
- Refresh Games / multi-console scanner;
- existing pause/menu behavior;
- stock Arcade lists 7-10.

The Test20 old-runner restoration is not present.

## Exact candidate

```text
xgo-arcade-test23-family-api-mame2000.zip
size              7,378,684 bytes
ZIP SHA-256        99c591ac0f9c61096997503adb328b3634ca080e79124d338b4ff3aeeb114b8a
firmware SHA-256   98f044cc661ebd63f2b332638c72109bcc4a04a527d8ca4cc3ee3b71c2bb59ed
core SHA-256       62114aeb11035a72111e67fa86c58f47937d4d7e78af220989097d00a914495d
```

Private CI:
- workflow run `34271682744`
- artifact ID `10074162355`
- archive commit `7130e05`

All compile, link, undefined-symbol, XGOC pack, ZIP integrity, upload, and archive steps passed.

## Hardware test

Use MAME2000 / MAME 0.37b5-compatible ROMs.

First:
1. boot normally;
2. verify Volume OSD still behaves normally in menu;
3. launch one known stock Arcade title from lists 7-10 and verify gameplay/audio/pause/Volume OSD;
4. enter fifth Arcade;
5. launch Pac-Man;
6. record video, audio, controls, pause/quit, and Volume OSD;
7. if Pac-Man runs, launch Ms. Pac-Man.

A candidate is not promotable unless both the new list-11 MAME path and existing golden functionality remain intact.
