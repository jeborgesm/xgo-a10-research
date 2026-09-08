# Arcade Test23 hardware result and Test25 corrected family candidate

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

## Test23 hardware result

Golden functionality regression check:
- Cadillac & Dinosaurs works normally.
- Existing stock Arcade path remains functional.

Fifth Arcade / list 11:
- Pac-Man: `Loading.....` then clean return to fifth menu.
- Ms. Pac-Man: `Loading.....` then clean return to fifth menu.
- no black-screen freeze.

## Test23 postmortem

The clean bounce-back was initially suspected to be a ROM-path failure.

A CI identity audit then exposed the real architecture bug:
- the new family frontend source was linked into the build command;
- linker garbage collection removed it because nothing referenced it;
- the production core entry returned the `retro_core_t *` API table;
- the low list-11 loader still used the old `entry(filename,load_state)` calling convention and ignored the returned pointer.

Therefore Test23 effectively did:

```text
loader
 -> upper-RAM core entry
 -> return retro_core_t *
 -> loader ignores return value
 -> clean return to fifth menu
```

This matches the observed hardware behavior exactly.

The Test24 package rebuilt the same dead architecture and must NOT be hardware-tested or promoted.

## Test25 correction

Test25 implements the actual SF2000/GB300 ownership contract.

### Low stock-side loader

The list-11 loader now:
1. validates and loads the XGOC payload to `0x87000000`;
2. clears runtime/BSS and repairs IRQ GP/cache state;
3. calls the core entry and captures `struct retro_core_t *`;
4. builds the already-proven stock archive path from:
   - `0x810a0eb0` current system directory;
   - `0x8109fce8` current archive filename;
   - resulting path `<system>/bin/<archive>`;
5. saves current golden stock callback/global state;
6. installs XGO stock video/audio/input callbacks through the core API;
7. calls the core's `retro_init()`;
8. populates the stock `g_retro_game_info` and `gfn_retro_*` slots;
9. calls the current golden `run_emulator()`;
10. calls `retro_deinit()`;
11. restores all saved stock callback/global state and RAMSIZE.

Lists 7-10 remain untouched stock FBA.

### Upper-RAM MAME core wrapper

Built from pinned family MAME2000:
`madcock/libretro-mame2000@231929ab69e7538bc1d98f59634b8d7fee2ddde7`

Retains:
- XGO admin/service-key patch;
- Test12 isolated-state patch;
- joypad-only input filtering;
- MAME2000-specific environment policy;
- family stereo fold-down: L+R mixed into first/internal-speaker channel while retaining the second channel.

### Golden non-regression contract

Base remains golden Test08:
`45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444`

No rollback of:
- Volume OSD v8;
- OSD timeout/border behavior;
- CPS1 scheduler improvements;
- mapper v19;
- native SNES;
- Refresh Games / multi-system scanner;
- stock pause/menu;
- stock Arcade lists 7-10.

## Exact Test25 candidate

```text
xgo-arcade-test25-true-family-mame2000.zip
size              7,400,397 bytes
ZIP SHA-256        927d6a33a42d8ddc239e64575ab19e07341d99a101051e3ddb202e9d0b5c5e8a
firmware SHA-256   9faddef2648868b856a2be084376cb7e3204505ae113fcefe1f884ae8957f316
loader size        2,009 bytes
loader SHA-256     bac994cd65c8da55fdc49b5cc92ad0aff7a4b2abf98086fab51f5b7d5e3277c
core XGOC size     9,124,304 bytes
core SHA-256       14a5303decb74df31d9c05c1c6336f57447d7f0cc6bb29e4501d621fe4e3eb5c
```

Private CI:
- run `34276092808`;
- artifact `10075859223`;
- archive commit `13f0869`.

All compile, link, undefined-symbol, loader-size, XGOC-pack, ZIP-integrity, upload, and archive checks passed.

## Hardware test order

1. Verify menu Volume OSD.
2. Launch Cadillac & Dinosaurs or another known-good stock Arcade game.
3. Verify stock audio, pause, and in-game Volume OSD.
4. Launch Pac-Man on fifth Arcade page.
5. Record whether it:
   - reaches gameplay;
   - returns cleanly to menu;
   - freezes;
   - has audio;
   - accepts controls;
   - supports pause/quit;
   - preserves Volume OSD.
6. If Pac-Man reaches gameplay, test Ms. Pac-Man.
