# Arcade Test17 — persistent MAME2000 stage-trace candidate

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **CI PASS; hardware diagnostic pending**

## Purpose

Tests 15 and 16 both fail identically:

```text
select Pac-Man / Ms. Pac-Man
 -> Loading.....
 -> black screen
 -> device unresponsive
```

No pause menu, no volume OSD, and no recovery path remain alive.

Test16 also proved that temporarily spoofing the active list ID from 11 to the known-good Arcade list ID 7 does not change the failure.

Therefore Test17 stops changing runtime assumptions and adds persistent stage checkpoints inside the external MAME2000 frontend.

## Trace behavior

The current Test17 build emits SD-card-root files:

```text
MAME17-11.txt
MAME17-12.txt
...
MAME17-17.txt
```

The highest file present after a hard power-cycle identifies the last completed MAME frontend stage.

Stage meanings:

```text
11  entered __core_entry_c
12  completed newlib/C runtime initialization
13  constructed stock-derived ARCADE/bin/<archive> path
14  installed libretro callbacks; immediately before retro_init
15  retro_init returned
16  immediately before xgo_stock_run_emulator
17  xgo_stock_run_emulator returned
```

If no `MAME17-11.txt` exists, the freeze occurs before the external core reaches its C frontend entry.

## Exact candidate

```text
xgo-arcade-test17-mame2000-stage-trace.zip
size              7,400,929 bytes
ZIP SHA-256        6e15e251c10193ca0a09aba278d467ed00f191d5b7f322bb27e7185e894c3e24
loader SHA-256     3e4207b31d608275f5fad0592c73e4072f9f8431967864e623a980f3fce05179
MAME2000 SHA-256   20519be70fe6ca8a35a58e7eb0ade2195fd1fdc04095cc641bd06ab249be100f
firmware SHA-256   9e9268226ed7315acf838180d68c9de138fce9dd4f80233cb65a55a2bb4585be
```

Private CI run:
`34242919132`

Workflow artifact:
`10062878283`

All build, link, package, ZIP-integrity, upload and archive steps passed.

## Hardware procedure

1. Remove any old `MAME17-*.txt` files from the SD-card root before testing.
2. Install Test17.
3. Launch Pac-Man from the fifth Arcade page.
4. When the known black-screen freeze occurs, hard-power the device off.
5. Put the SD card in a PC.
6. Report the highest-numbered `MAME17-xx.txt` file present, or report that none exist.

No additional ROM variation is needed for this diagnostic.
