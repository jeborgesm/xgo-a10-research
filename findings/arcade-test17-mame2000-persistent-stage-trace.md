# Arcade Test17 — persistent MAME2000 core-stage trace

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

Status: **CI PASS; hardware diagnostic pending**

## Why Test17 exists

Test15 and Test16 both fail identically on hardware:

```text
select Pac-Man or Ms. Pac-Man
 -> Loading.....
 -> black screen
 -> device unresponsive
```

No pause menu or volume OSD remains available after the black screen.

Test16 proved that temporarily spoofing active list ID 7 during external MAME execution does not change the failure. The list-ID runtime hypothesis is therefore closed.

Rather than continue changing runtime assumptions, Test17 instruments the external MAME2000 core itself.

## Diagnostic design

The loader is kept at the proven-size Test16 implementation. Loader-side file logging was intentionally rejected because adding persistent filesystem trace code exceeds the verified `0x80001900..0x8000217f` firmware cave.

The external MAME2000 core has ample space and creates persistent, fs-synced files at the SD-card root:

```text
MAME17-11.txt
MAME17-12.txt
...
MAME17-17.txt
```

Each file contains `ok\n`.

Checkpoint meanings:

```text
11  entered __core_entry_c
12  completed newlib/C runtime initialization
13  constructed/validated stock-resolved ROM ZIP path
14  immediately before retro_init()
15  retro_init() returned
16  callbacks/game-info installed; immediately before xgo_stock_run_emulator()
17  xgo_stock_run_emulator() returned
```

Interpretation after a hard-power recovery:

- **No `MAME17-11.txt` exists**: failure occurs before the external core reaches its C entry. Focus on loader/control transfer/cache/upper-RAM handoff.
- **Highest file = 11**: failure during C/newlib runtime initialization.
- **12**: failure during content-path validation/construction.
- **13 or 14**: failure entering/inside `retro_init()`.
- **15**: failure during frontend callback/game-info setup before stock run loop.
- **16**: stock `run_emulator()` entered and does not return; next instrument its load-game/run callbacks.
- **17**: run loop returned; failure is cleanup/return path.

## Exact candidate

```text
xgo-arcade-test17-mame2000-stage-trace.zip
size              7,400,929 bytes
ZIP SHA-256        6e15e251c10193ca0a09aba278d467ed00f191d5b7f322bb27e7185e894c3e24
firmware SHA-256   9e9268226ed7315acf838180d68c9de138fce9dd4f80233cb65a55a2bb4585be
loader size        1,389 bytes
loader SHA-256     3e4207b31d608275f5fad0592c73e4072f9f8431967864e623a980f3fce05179
traced core size   9,128,304 bytes
core SHA-256       20519be70fe6ca8a35a58e7eb0ade2195fd1fdc04095cc641bd06ab249be100f
```

Private CI run:
`34242919132`

Workflow artifact:
`10062878283`

All build, link, core packing, loader cave-size, ZIP-integrity and archive steps passed.

## Hardware procedure

1. Install Test17 over the current disposable test card.
2. Before launching, delete any old `MAME17-*.txt` files from the SD-card root if present.
3. Launch **Pac-Man only**.
4. When the known black-screen freeze occurs, wait a few seconds.
5. Hard-power the device off.
6. Remove the SD card and inspect its root on a PC.
7. Report which `MAME17-xx.txt` files exist, especially the highest number.

Only one game needs to be tested for this trace because Test15/Test16 already established the identical failure on both Pac-Man and Ms. Pac-Man.
