# SF2000 upstream engineering corpus harvest

Date: 2026-09-16
Branch: `research-a10-hardware-lineage`

## Goal

Treat the SF2000/GB300/HCSEMI research community as an upstream engineering corpus rather than merely searching for an explicit XGO/A10 mention. Recover mechanisms, APIs, patches, hardware discoveries, and failed experiments that can be fingerprinted against the XGO A10 firmware and selectively imported into later modification branches.

## High-value transferable mechanisms recovered

### 1. Multicore core API is a documented stock-frontend compatibility layer

`madcock/sf2000_multicore/core_api.c` exposes a mature wrapper around the stock libretro-style frontend. It installs wrappers for environment, video, audio and input callbacks, supports per-core and per-game options, provides state handlers, and adapts cores that either require a full path or accept an in-memory ROM buffer.

This is directly relevant to XGO because our CLASSIC work independently recovered the same broad raw-core contract (`g_retro_game_info`, `gfn_retro_*`, `RAMSIZE`, loader entry points, stock callback bridge). The upstream source can therefore be used as a semantic reference when naming and validating XGO globals/functions rather than reverse-engineering every behavior independently.

### 2. Save-state implementation recovered in source

The multicore wrapper replaces stock frontend state callbacks:

- `gfn_state_load = state_load`
- `gfn_state_save = state_save`

It translates the frontend-provided slot filename into `/mnt/sda1/ROMS/save/<rom basename>.state<slot>`, loads/saves the core through `retro_unserialize` / `retro_serialize`, and explicitly calls `fs_sync()` after writing.

This is highly relevant to XGO Test52 CLASSIC Save/Load. We should compare our working XGO implementation against this source and determine whether any remaining save-state limitations come from path/slot translation, serialization buffer sizing, or stock snapshot handling.

The SF2000 multicore Makefile also patches the stock snapshot-image buffer size at firmware offset `0x34f8b8`; its comment says `0x0c` (768 KiB) is enough up to 640x480x2. This suggests the stock frontend itself maintains a separate screenshot/snapshot buffer whose size can become a compatibility constraint independently of libretro serialization.

### 3. Stereo-to-mono solution recovered exactly

The mature multicore wrapper intercepts both `retro_set_audio_sample` and `retro_set_audio_sample_batch` and mixes stereo for a single-speaker device using the overflow-safe expression:

`(left >> 1) + (right >> 1)`

For batch audio it writes the mixed sample into the first channel and leaves the second channel unchanged because the second physical channel is reportedly not heard. The wrapper then forwards to the stock `retro_audio_sample_batch_cb` and returns the requested frame count even though the stock callback itself reportedly returns zero.

This is directly relevant to the XGO Test13 audio-revival branch. It independently confirms the overflow-safe mixing formula already selected for revival and gives us an upstream implementation to compare against. Do not modify the cumulative baseline from this archaeology branch.

### 4. Auto-frameskip hook via audio-buffer status

The wrapper handles `RETRO_ENVIRONMENT_SET_AUDIO_BUFFER_STATUS_CALLBACK`, stores the core callback and assigns the stock/global `gfn_frameskip` bridge. Its `frameskip_cb` translates the stock flag into the libretro audio-buffer callback with `underrun_likely=true`.

This is potentially important for XGO performance work. Our CPS1 pacing repair should be fingerprinted against this mechanism before inventing additional timing fixes. The upstream community may already have mapped the frontend's intended relationship between audio starvation and frameskip.

### 5. XRGB8888 -> RGB565 compatibility layer

The multicore wrapper contains explicit XRGB8888-to-RGB565 conversion and allocates a conversion buffer using the core's maximum geometry. This allows cores requesting `RETRO_PIXEL_FORMAT_XRGB8888` to run through a frontend whose native path is RGB565.

This is a concrete possible expansion path for XGO cores that currently fail only because of unsupported pixel format. It should be tested only on a future modification branch after checking available RAM and XGO video callback behavior.

### 6. Per-core and per-game option hierarchy

The wrapper reads:

- `/mnt/sda1/cores/config/multicore.opt`
- `/mnt/sda1/cores/config/<core>.opt`
- `/mnt/sda1/cores/config/<core>/<game>.opt`

and services `RETRO_ENVIRONMENT_GET_VARIABLE` from the resulting configuration.

This is an attractive architecture for XGO CLASSIC expansion: global defaults, core-specific settings and game-specific overrides without rebuilding firmware for every compatibility quirk.

### 7. Core entry / runtime initialization contract

The core binary places `__core_entry__` at a known beginning location because the loader places the binary at `0x87000000` and calls the first function. Entry clears BSS, initializes newlib reentrancy and libc constructors, then returns a `retro_core_t` export table.

The loader work also explicitly restores the stock `$gp` value. This is especially relevant because XGO independently required a bidirectional `$gp` bridge during raw-core work. The matching design pattern is strong evidence that this upstream loader source should be treated as a first-class semantic reference for XGO raw-core integration.

### 8. Input compatibility filtering

The wrapper installs an input-state shim that accepts joypad requests only for ports 0 and 1 and returns zero for unsupported device classes. It explicitly configures both first controllers as `RETRO_DEVICE_JOYPAD` after successful load.

This may help explain core-specific crashes or strange input behavior on XGO when a libretro core probes keyboard/mouse/analog device classes the stock frontend never implemented.

### 9. ROM loading supports both libretro contracts

If a core advertises `need_fullpath`, multicore passes the file path directly. Otherwise it loads the complete ROM into a temporary buffer and passes `path + data + size` to `retro_load_game`, then frees the buffer after load.

This is useful when diagnosing XGO cores that return to menu or freeze at Loading: failure may be caused by using the wrong content-loading contract rather than emulator incompatibility.

## Broader community discoveries to fingerprint against XGO

The public SF2000 documentation preserves additional reverse-engineered mechanisms attributable to the Discord community:

- per-game `.kmp` mappings and default mappings inside `bisrv.asd` (bnister + notv37);
- battery calibration constants inside stock firmware (bnister + dteyn);
- SNES first-launch/full-speed firmware patch (bnister);
- exact emulator provenance/source revisions (bnister + notv37);
- unusual FBA/MAME arcade ROM-set compatibility (adcockm);
- runtime-generated user-ROM catalog `TSMFK.TAX` and static `.tax` catalog resources;
- `nvinf.hsp` game-count behavior (kid_sinn);
- save-state and disguised arcade `.skp` state formats;
- Favorites/History binary formats;
- boot logo stored as RGB565 inside `bisrv.asd`;
- menu audio sample-rate investigation;
- stock firmware update mechanism using an `UpdateFirmware` folder;
- battery/power-management limitations and firmware calibration.

Each of these is now a candidate for XGO fingerprinting. Several already have clear XGO analogues from our independent work.

## New research methodology

For each upstream discovery:

1. recover source, patch, offsets, symbols and author/context;
2. identify stable fingerprints: strings, constants, instruction sequences, function shapes, callback structures, paths;
3. search the original XGO `bisrv.asd` and cumulative firmware for those fingerprints;
4. classify as `exact`, `modified`, `analogous`, or `absent`;
5. document the XGO address/function mapping;
6. only if useful, implement on a separate modification branch;
7. use normal build -> offline audit -> hardware test -> artifact archive discipline.

## Highest-priority transfer targets

1. Complete stock frontend/libretro global and callback map using multicore source as semantic oracle.
2. Compare XGO Test52 Save/Load to upstream state handlers and snapshot buffer behavior.
3. Compare Test13 audio revival against Osaka's mature mono-mix implementation.
4. Locate and characterize XGO equivalent of `gfn_frameskip` / audio-buffer-status pacing.
5. Test whether XGO can support XRGB8888 cores through a conversion shim.
6. Evaluate per-core/per-game `.opt` support for CLASSIC without disturbing stock lists.
7. Recover more Discord-derived patches, especially performance, memory/cache, video scaling and loader fixes.

## Evidence discipline

These are SF2000/GB300 community mechanisms, not assumptions that every implementation is byte-identical on XGO. Transfer requires binary fingerprinting or hardware confirmation. The purpose of this corpus is to stop rediscovering known family behavior blindly and to turn upstream work into testable XGO hypotheses.
