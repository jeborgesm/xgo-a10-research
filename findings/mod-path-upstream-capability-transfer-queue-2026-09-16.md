# Mod-path handoff: upstream HCSEMI/SF2000 capability transfer queue

Date: 2026-09-16
Source branch: `research-a10-hardware-lineage`
Purpose: preserve high-value upstream engineering discoveries specifically for future XGO modification work.

## Why this exists

The SF2000/GB300 community corpus is no longer useful merely as lineage evidence. XGO work has independently demonstrated enough compatibility with the family frontend/core contract that upstream patches, abandoned branches, and mature multicore code should be treated as a library of candidate capabilities.

This document is a handoff into the modification path. It does **not** authorize changes to the protected cumulative baseline. Each item still requires XGO binary fingerprinting, an isolated modification branch, offline audit, hardware test, and artifact archival.

## Protected XGO baseline

Do not regress Mapper v19, CPS1 pacing, Audio OSD v8, fine-volume +9 behavior, generalized stock Refresh, CLASSIC importer/core path, Test52 CLASSIC Save/Load, stock consoles, stock Arcade, or later proven metadata/artwork work.

## 1. Large external-core import opportunity

`madcock/sf2000_multicore/buildcoresworking.sh` documents a substantial set of cores classified upstream as fully working, plus another set working with issues.

High-interest fully-working families include:

- MAME2000
- Atari 2600 / 5200 / 7800 / 800
- Lynx
- WonderSwan
- ColecoVision
- Intellivision
- PC Engine
- Neo Geo Pocket
- MSX
- Game & Watch
- Vectrex
- ZX81 / ZX Spectrum
- PokeMini
- alternate GB / NES / SNES cores
- PicoDrive / Game Gear
- PrBoom / Doom
- ECWolf / Wolfenstein 3D
- Cannonball / OutRun
- REminiscence / Flashback
- additional small/homebrew cores

Upstream also lists cores that execute with known issues, including C64/VIC20, Arduboy, Fake-08, Cave Story, PC-FX, Virtual Boy, Genesis Plus GX, Geolith, mGBA and others.

### XGO significance

CLASSIC already proved that XGO can execute a family-derived external-core contract. Future work should therefore test the upstream core catalog systematically rather than treating every new emulator as a fresh port.

Recommended future project: build an XGO core-compatibility matrix with categories `direct`, `ABI-adapted`, `frontend-shim`, `core-patch`, `fails`.

## 2. Stock audio callback return-value bug

Upstream commit `3ce1a3ee6f60662ef509a8ffd8592754d6899ad3` documents that the stock frontend `audio_batch_cb` returns zero rather than the number of frames consumed. Some cores ignore this, but cores such as PrBoom can retry forever and appear hung.

Upstream workaround:

1. call the stock audio callback;
2. ignore its zero return value;
3. return the requested `frames` count to the core.

### XGO action

Fingerprint XGO `retro_audio_sample_batch_cb` behavior. A future external core that hangs after successful initialization must not automatically be classified as emulator incompatibility until this contract is checked.

This also belongs in the Test13/audio-revival semantic map, but do not combine unrelated modifications in one hardware candidate.

## 3. `$gp` safety extends into interrupt context

The community discovered that dynarec code can execute with a core-specific/foreign `$gp`. If an interrupt occurs during that interval, the stock IRQ handler may enter expecting firmware `$gp` and access globals through the wrong base, freezing the device.

This extends the problem beyond ordinary core->frontend calls.

### XGO action

Our bidirectional `$gp` bridge solved the synchronous raw-core boundary. Before importing dynarec/JIT cores, audit XGO interrupt entry behavior and determine whether firmware `$gp` must be restored in IRQ context.

Treat this as a prerequisite for gpSP-style dynarec experiments.

## 4. MIPS cache maintenance for loaded/dynamic code

Upstream commit `25c8dfdaa088b44bac2d12e72495a8913df93389` records an incorrect attempt to use Index-based cache operations as though their operand were an ordinary address range.

Commit `e07d14a55282feb5a07eb16895a886987ae2bfe2`, credited with Osaka diagnostic input, reverted to full cache maintenance because range-specific flushing was unstable:

- full D-cache writeback/invalidate
- synchronization
- full I-cache invalidate
- post-operation barrier/nops

The upstream `_flush_cache()` ultimately ignores the requested range and flushes all cache for stability with dynarec code.

### XGO action

Before dynarec imports, map XGO cache geometry/CPU behavior and compare its loader/cache path. Do not copy SF2000 addresses blindly, but preserve the semantic lesson: generated executable code requires correct D->I coherency, and Index cache operations operate on cache indices rather than arbitrary virtual ranges.

## 5. Configurable scaling through HCSEMI OSD

bnister/osaka-era video work demonstrates configurable scaling using the HCSEMI OSD path, including stock/core-provided ratio, full screen, square pixels, custom ratio, filtered scaling, and unfiltered/integer-like scaling.

XGO has independently mapped related OSD functions including `osddrv_scale`, making this a particularly strong transfer candidate.

### Future XGO feature

Per-core and eventually per-game display configuration:

- original/core aspect
- full screen
- square-pixel aspect
- custom aspect ratio
- filtered/unfiltered scaling
- possible integer scaling where geometry permits

This should be implemented as a frontend capability, not patched independently into every core.

## 6. XRGB8888 -> RGB565 compatibility shim

Upstream commit `b12d8c72f67f865dc8039278ac732665bcaa6d27` added software XRGB8888-to-RGB565 conversion for cores requesting a pixel format unsupported by the stock frontend.

Later community work found that in-place conversion could corrupt output for REminiscence/Flashback; the mature approach uses a separate RGB565 framebuffer sized from the core's maximum geometry.

### XGO action

Add this only as a future isolated frontend shim after measuring available RAM and confirming XGO video callback semantics. Use a separate destination buffer from the beginning; do not repeat the abandoned in-place implementation.

## 7. Save-state snapshot buffer is separate from core serialization

Upstream commit `a01505ddca2e35d8e9d93c1ef150432c6c255cce` attributes to Osaka a patch increasing the stock save-state snapshot-image buffer. Upstream comment documents `0x0c` / 768 KiB as sufficient through 640x480x2.

This is distinct from `retro_serialize()` state data.

### XGO action

Test52 CLASSIC Save/Load is already proven and should not be disturbed. For future higher-resolution cores, diagnose serialization and frontend screenshot/snapshot allocation separately.

## 8. Per-core and per-game keymaps

Closed/unmerged Geonux work (`89edc5749e4698b750e88e3bc64d2f37bd1cafdd`) exposes a useful design:

- ROM-specific `.kmp`
- core-level `keymap.kmp` fallback
- stock `set_keymap()` call
- direct stock input-state access

XGO has independently demonstrated keymap ABI compatibility through Mapper v19.

### Future XGO hierarchy

1. game-specific mapping
2. core-specific mapping
3. Mapper v19/global mapping
4. stock default

This is preferable to hardcoding compatibility mappings into individual cores.

## 9. Cheats

The same abandoned branch implemented game-linked `.cht` loading and normal libretro `retro_cheat_set`/reset handling.

### XGO action

Once external-core infrastructure is stable, cheats can be implemented as a generic frontend feature rather than emulator-specific patches. Keep it lower priority than core loading, video, input, audio, and save-state correctness.

## 10. Explicit controller-device initialization

Upstream commit `51646c7a9f929136c0de5005a96245191589bde5` fixes a non-responsive VICE/C64 core by explicitly configuring controller ports 0 and 1 as `RETRO_DEVICE_JOYPAD` and filtering unsupported input device requests.

### XGO action

If a newly imported core runs but has dead or erratic controls, inspect device negotiation before altering Mapper v19. This is a frontend/libretro-contract issue, not necessarily a button-map issue.

## 11. Per-core/per-game options

Mature multicore supports a layered option model resembling:

- global multicore options
- core-specific options
- game-specific options

and services `RETRO_ENVIRONMENT_GET_VARIABLE` from those files.

### XGO opportunity

This is likely the correct long-term architecture for compatibility quirks, scaling choices, core options, and game overrides. It avoids firmware rebuilds for every title-specific setting.

## Suggested future import order

Do not attempt a giant all-at-once firmware patch. Recommended engineering sequence:

1. Build an XGO external-core compatibility harness/matrix around the proven CLASSIC loader contract.
2. Fingerprint/fix generic frontend contracts: audio return value, input device negotiation, fullpath vs memory-loaded content.
3. Import several low-risk fully-working upstream cores to validate repeatability.
4. Add per-core/per-game options and mapping hierarchy.
5. Add scaling controls.
6. Add XRGB8888 conversion.
7. Audit IRQ `$gp` and cache coherency, then attempt dynarec cores.
8. Expand to the broad upstream core catalog.
9. Add generic cheats and convenience features after runtime stability.

## Evidence discipline

Upstream `fully working` means working on the upstream SF2000 multicore environment, not automatically working on XGO. XGO compatibility must be measured. Conversely, an XGO failure should be classified by contract stage (load, entry, init, environment, content, video, audio, input, run, state, exit) before concluding the core itself is incompatible.

## Bottom line

The mod path should now treat the SF2000/GB300 engineering corpus as an upstream compatibility SDK in all but name. XGO has already independently reproduced enough of its runtime contract that importing capabilities is a realistic near-term project rather than a speculative lineage exercise.
