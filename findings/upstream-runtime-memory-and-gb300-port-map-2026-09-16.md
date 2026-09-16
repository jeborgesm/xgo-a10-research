# Upstream runtime, memory, and GB300 port archaeology

Date: 2026-09-16
Branch: `research-a10-hardware-lineage`

Continued mining of historical SF2000 multicore commits and cross-device ports produced several high-value constraints for the future XGO multicore/mod path.

## 1. The loader itself can corrupt firmware if `.bss` is not bounded

Commit `63f62a904b5a3d56bb9e595f64895de24202c4db` documents that the SF2000 loader had only a 3200-byte insertion region, `0x80001500` through `0x80002180`. Clearing `.bss` while `.bss` extended beyond that region overwrote live firmware code/data and caused a crash/freeze.

The upstream response was architectural rather than cosmetic:

- move loader to beginning of available cave;
- minimize static `.data`/`.bss`;
- move the debug font to another known empty firmware region;
- dynamically allocate the debug screen buffer;
- remove unnecessary static filename storage;
- add a build-time assertion that `_end` does not cross the loader ceiling.

### XGO significance

Every XGO injected loader/shim should have an explicit **code-cave budget including `.bss`**, not merely a patched-byte or flat-file-size check. Our build tooling should fail closed when text+rodata+data+bss exceeds the audited region.

This is directly relevant to future multicore expansion because convenience features can silently grow static state until a previously stable patch begins corrupting adjacent firmware.

## 2. C++ core support exposes heap ownership and destructor problems

Commit `ec4a6cef1dcf36b980b616e085315c1da2e258c9` got Beetle PCE Fast running by linking C++ runtime support, preserving exception/init/fini sections, calling global constructors, and exposing additional stock functions including `sbrk` and `fstat`.

But the author explicitly warned that exposing stock `sbrk` to a separately linked libc could allow **two malloc implementations to share/manipulate one heap**, with undefined ownership. The initial implementation also called constructors but did not yet have a safe lifecycle point for destructors, so repeated core loads could leak memory.

### XGO significance

For future C++ cores:

- decide which allocator owns the heap;
- avoid mixed allocator/free pairs;
- validate `sbrk` semantics before exposing it;
- call constructors exactly once per load;
- establish a deterministic destructor/unload lifecycle;
- test repeated load->exit->load cycles for memory loss.

A core that works once but freezes after several launches may be a lifecycle/heap bug rather than emulation instability.

## 3. Never mix `FILE *` objects between stock libc and toolchain libc

Historical commits explicitly discovered undefined behavior when a `FILE *` returned by stock firmware libc was passed into an I/O function pulled from the linked toolchain libc.

Commit `2df3e71e3e37a9afd2592879b38ac5a9d315d477` therefore implemented `fprintf` in terms of formatting plus the stock-backed `fwrite` path. Related commits stubbed `setbuf` and added further FILE-related wrappers so the toolchain implementation would not be linked accidentally.

### XGO significance

The XGO compatibility runtime should treat stock `FILE *` as an opaque ABI-owned object. All operations on it must remain within one compatible wrapper family. This applies to fopen/fclose/fread/fwrite/fseek/ftell/fprintf/setbuf and related functions.

This is another likely source of apparently random per-core failures.

## 4. A built-in SD-card log facility is proven useful upstream

The upstream loader added `xlog()` writing `log.txt` at SD root, later adding source file/function/line metadata and finally making logging opt-in simply by creating `log.txt`.

### XGO opportunity

A future diagnostic build could use the same philosophy: zero-cost/disabled normal operation, but when a marker file exists, log core-selection and libretro lifecycle stages to SD. This would greatly improve diagnosis of `Loading... -> menu`, black screen, and freeze cases without needing UART.

Do not add this to the protected baseline casually; make it an isolated diagnostic capability.

## 5. Cross-device GB300 port gives us a portable semantic symbol map

Closed PR #11 in `madcock/sf2000_multicore` is unusually valuable. It ports the same multicore architecture to GB300 using address mappings credited directly to Osaka's Discord work and preserves the original Discord message:

`https://discord.com/channels/741895796315914271/1099465777825972347/1195107365117235230`

The PR changes addresses but preserves the same semantic interface, including:

- `fs_open/read/write/lseek/close/access/fstat/stat/mkdir/opendir/readdir/closedir/sync`
- interrupt disable/enable
- tick/delay functions
- LCD/video functions
- `vpo_ioctl`
- `osddrv_open/close/create_region/region_write/scale`
- `dev_get_by_id`
- ST7789 display functions
- `run_osd_region_write`
- `run_screen_write`
- `run_sound_advance`
- libretro video/audio/input/environment callbacks
- `run_emulator`
- `run_gba`
- `RAMSIZE`
- `g_errno`
- sound-task flags
- `g_retro_game_info`
- state save/load function pointers
- libretro core callback pointers
- `gfn_frameskip`
- `g_run_file_size`

This is strong evidence that the useful object is not one firmware's absolute address table but a **portable semantic ABI map** whose addresses move between family firmware builds/devices.

### XGO action

Formalize our XGO symbol work in the same semantic vocabulary and build a three-column family map:

`semantic symbol | SF2000 address | GB300 address | XGO address/evidence`

Then add SF3000/other HCSEMI devices where reliable mappings exist.

This should make upstream patch transfer dramatically safer: patches can be translated by meaning rather than by copied addresses.

## 6. Some GB300 mappings were still incomplete

The GB300 PR explicitly left at least `gfn_retro_unload_game` and `gp_buf_64m` as not present in the mapping and temporarily defaulted them to SF2000 values. That is a warning not to treat a port's linker map as equally proven for every symbol.

### Evidence grades for family map

Use per-symbol confidence:

- `verified-by-code/use`
- `mapped-but-not-runtime-verified`
- `inferred-by-structure`
- `placeholder/copied-from-sibling`
- `absent/unknown`

XGO should never inherit a sibling address simply because a historical port did.

## 7. New durable Discord coordinate

Recovered from PR #11:

- server: `741895796315914271`
- channel/thread: `1099465777825972347`
- message: `1195107365117235230`
- attributed subject: Osaka GB300 address mapping used for multicore port

This message ID should be added to the Discord shadow-index and searched independently across GitHub/forums/docs.

## Bottom line

The upstream corpus is now revealing not only features but the **engineering rules required to make broad core import stable**: bounded injected memory, one allocator strategy, correct C++ lifecycle, one coherent stdio ABI, optional SD logging, and semantic rather than absolute cross-device symbol mapping.

The GB300 port is especially important because it demonstrates the exact translation process we need for XGO: preserve the multicore architecture while remapping the stock firmware ABI to a sibling device.
