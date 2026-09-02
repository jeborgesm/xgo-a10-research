# First full native XGO FCEUmm core

Status: **offline build/link/packaging confirmed; physical XGO execution not yet tested**.

## Milestone

The native NES path now produces a complete FCEUmm external-core image using the exact HC15xx/SF2000 Codescape toolchain and the real XGO-native handoff contract.

This is distinct from the earlier generic/semicolon GBA-dispatch experiment. The native path intercepts the normal NES dispatch inside `run_game()` only after stock firmware has already opened and preloaded the selected `.nes` ROM into the 64 MiB game arena.

## Reproducible full-link evidence

Workflow: `XGO native FCEUmm full link`

Actions run: `33645462778`

Source commit: `ad43718a8de6354e88288991b4b6170d26bc778e`

The first run succeeded without linker/runtime workaround iterations.

The production link includes:

- native `__core_entry__` frontend;
- `XGO_WITH_NEWLIB` initialization (`_REENT_INIT_PTR`, `__sinit`, `__libc_init_array`);
- pinned HC15xx FCEUmm `e6111e684e7a7761f3f1d6c80d0a825e2c8cdc7e`;
- pinned HC15xx libretro-common `9362316bf1da38160b324a1515bfb83e44ebd7af`;
- exact Codescape newlib/libm/libgcc;
- private preloaded-ROM-aware `sbrk()` heap;
- XGO filesystem/time/directory syscall bridge;
- explicitly mapped stock XGO low-level services and libretro callbacks;
- no stock generic `malloc`/`free`/libc imports.

The final ELF has **zero undefined symbols**.

## Absolute image layout

```text
image_start       0x87000000
entry             0x87000000
entry_offset      0x0
file_end          0x87186f08
linked_file_span  1,601,288 bytes
payload_size      1,601,288 bytes
bss_start         0x87186f08
image_end         0x873b1f78
memory_size       3,874,680 bytes
reserved_size     13,479,424 bytes
headroom           9,604,744 bytes
```

The native entry is therefore the very first payload instruction and the complete runtime image occupies only about 29% of the reserved external-core window.

## XGOC image

The production raw image packs successfully as XGOC v1:

```text
load          0x87000000
entry         0x87000000
payload       1,601,288 bytes
runtime       3,874,680 bytes
zero tail     2,273,392 bytes
payload CRC   0xc30d3189
header CRC    0xac216777
```

Output SHA-256 values from the successful run:

```text
xgo-native-fceumm.elf
5d0f33056a29bf40c6238f9149ac1e95d5ab9c2eed58a605f5e4ad37e9659e60

xgo-native-fceumm.bin
6363aab2dd7d68ede20458d16cbdda42f731d5d3e409082ccadc15d104bd4478

core-native-nes.xgc
8a1ab8193707c8491a3cff2830a74c6d1f85c47be8dbc7bfc6c2d30c36273871
```

## Native injected loader

The matching handoff is `native_nes/xgo_nes_loader.c`, not the older semicolon/GBA loader.

Exact Codescape preflight run `33645887563` produced:

```text
loader_start      0x80001500
loader_size       924 bytes
loader_capacity   3,200 bytes
loader_headroom   2,276 bytes
patch_site        0x80360e20
stock_fallback    0x8035f63c
```

Loader binary SHA-256:

```text
be1f097373209967bfca6fad58dc5ff8d1ce71d8434537f9384deba74e7c0958
```

The preflight proves:

- no undefined symbols;
- no `$gp`-relative instructions;
- no GOT/small-data sections;
- no private BSS/NOBITS dependency;
- exact entry at the verified firmware cave `0x80001500`;
- comfortable fit in the 3,200-byte cave.

## Correct launch path

The stock instruction at XGO address `0x80360e20` is:

```text
jal 0x8035f63c   # stock run_nes
```

`build_native_nes_asd.py` verifies both the exact preserved firmware SHA-256 and the exact original JAL bytes before replacing only that call with:

```text
jal 0x80001500   # native XGO NES external-core loader
```

This location is important. `run_game()` has already preloaded the real selected NES file before the interception occurs. Consequently:

1. the user launches an ordinary `.nes` ROM from the normal NES browser;
2. stock firmware reads that ROM into `gp_buf_64m` exactly as before;
3. the patched NES JAL enters the 924-byte native loader;
4. the loader validates and loads `/mnt/sda1/cores/fceumm/core.xgc` at `0x87000000`;
5. it reconstructs the zero/BSS tail, repairs the stock IRQ `$gp` path, and flushes caches;
6. `__core_entry__` receives the real NES filename and consumes the already-preloaded ROM buffer directly;
7. pre-entry validation failures restore `RAMSIZE` and fall back to untouched stock `run_nes()`.

## The older semicolon/GBA staging path is not this path

`tools/multicore/stage_fceumm_test.py` and `probe/xgo_probe_loader.c` belong to the first-generation generic external-core experiment. They use a synthetic zero-byte `fceumm;<rom>.gba` browser token and intercept the GBA family before a real NES ROM is preloaded.

That mechanism was useful for proving the generic external-core architecture, but it does **not** satisfy the native frontend's preloaded-ROM contract and must not be used to test this production native NES core.

The native test path is now staged by:

```text
tools/multicore/native_nes/stage_native_nes_test.py
```

It creates only the patched SD-loaded `bios/bisrv.asd`, `/cores/fceumm/core.xgc`, and explicit test documentation. It creates no fake GBA token and copies no ROM. The tester launches an ordinary known-good NES ROM through the stock NES browser.

## Current boundary

The software dependency, absolute-link, memory-layout, XGOC, loader-size, patch-site, and fallback contracts are now all reproducibly validated offline.

The remaining unknown is physical execution on XGO hardware:

- live heap break at native NES dispatch time;
- large-core file read into the reserved window;
- cache/IRQ transition under a production 1.6 MiB FCEUmm payload;
- first FCEUmm initialization/frame/audio/input behavior using stock XGO callbacks;
- return behavior from the stock emulator loop.

Those are now hardware observations rather than unresolved linker architecture.
