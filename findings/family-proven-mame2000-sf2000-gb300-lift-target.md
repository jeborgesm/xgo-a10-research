# Family-proven MAME2000 path — SF2000/GB300 multicore lift target

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

## Key finding

Closely related HC15xx family devices already have a working MAME2000 implementation.

Authoritative family sources:
- `madcock/sf2000_multicore`
- `madcock/sf2000_multicore_cores`
- `tzubertowski/gb300_multicore`

SF2000 Multicore explicitly ships MAME2000 as console/core `m2k`.
GB300 Multicore also ships `m2k` and states that its multicore behavior follows the SF2000 architecture.

Community documentation reports the family MAME2000 core uses MAME 0.37b5 sets and can address roughly 2,241 sets. Performance is significantly worse than stock FBA for larger/more graphically demanding titles, but this does not invalidate the classic 1979-1984 target set.

## Most important architectural discovery

The family-proven MAME path is NOT the custom XGOC/frontend bridge currently being debugged on XGO.

SF2000 Multicore contract:

```text
stock GBA launch hook
 -> multicore loader
 -> raw core binary loaded directly at 0x87000000
 -> call core_entry_t at 0x87000000
 -> core entry clears BSS + initializes newlib/ctors
 -> returns struct retro_core_t API table
 -> loader installs stock video/audio/input/environment callbacks
 -> core_api->retro_init()
 -> populate stock g_retro_game_info
 -> assign stock gfn_retro_* callbacks
 -> stock run_emulator(load_state)
 -> retro_deinit()
```

The core is built as:
`core_87000000`
not as XGOC.

## Family loader/runtime details worth lifting

From `madcock/sf2000_multicore/main.c`:

- core load address: `0x87000000`;
- sound task is stopped before loading;
- `RAMSIZE = 0x87000000`;
- raw core is fread directly into upper RAM;
- full I/D cache flush;
- entry at first byte returns `struct retro_core_t *`;
- stock libretro callbacks are installed by the loader;
- stock `run_emulator()` owns the normal runtime loop.

Critically, family multicore patches the IRQ handler itself:

```text
PATCH_JAL(0x80049744, restore_stock_gp)
```

and `restore_stock_gp()` restores the stock firmware GP on every interrupt.

This differs materially from the current XGO bridge, which copies two startup GP-init words into the IRQ path once before entering the core.

That is now a high-priority candidate for why:
- the 16-byte XGO1 external probe succeeds on XGO;
- the full MAME runtime freezes.

Minimal external code does not survive long enough to exercise interrupt-driven runtime heavily, while MAME does.

## Family core wrapper

`core_api.c` provides the family wrapper around libretro cores.

`__core_entry__()`:
- clears core BSS;
- initializes newlib reentrancy;
- runs libc init arrays;
- returns `&core_exports`.

The loader then uses the returned API table.

The wrapper also:
- loads per-core/per-game options;
- installs filtered joypad input;
- supports state load/save;
- supports XRGB8888 conversion when needed;
- exposes frameskip through the family frontend;
- handles cores that need full paths vs in-memory content.

Notably, the family wrapper already contains a single-speaker stereo fold-down helper:
`mono_mix_audio_batch_cb()`.
It mixes L+R into the first channel and leaves the second channel unchanged.

## Direction change

Stop treating MAME2000 as an XGO-specific external-core integration problem.

Do not continue the custom staged-return ladder unless the family lift fails.

New primary engineering target:

1. port the SF2000/GB300 multicore loader contract to XGO list ID 11;
2. adapt stock addresses/globals to the already-recovered XGO equivalents;
3. load the family-format raw `m2k/core_87000000` directly at 0x87000000;
4. use the family `retro_core_t` API-table contract;
5. implement the family IRQ GP-restoration hook correctly on XGO;
6. feed the already-resolved Classic Arcade ROM path into the family wrapper;
7. leave lists 7-10 on stock FBA;
8. test Pac-Man/Ms. Pac-Man with MAME 0.37b5 sets.

This is now preferred over further custom MAME frontend archaeology.
