# First fully linked XGO native SNES Core #2 candidate

Status: **OFFLINE BUILD + LOADER CONTRACT CLOSED; HARDWARE EXECUTION PENDING**

Branch: `research-post-mapper-runtime`

## Milestone

The second external libretro core now builds as a complete XGO XGOC image and the corresponding guarded SNES loader fits the same stock firmware injection cave already proven by the native NES work.

This is the first production-shaped proof that the XGO external-core architecture is genuinely reusable beyond FCEUmm.

## Core provenance

```text
core             madcock/snes9x2005
commit           fa69dd6a3caf279cc1f457e65e360f8b9a3683ed
build profile    platform=sf2000 LOAD_FROM_MEMORY=1
toolchain        Codescape GNU Tools 2019.09-03-2
ISA              MIPS32 little-endian soft-float
XGO family       0x08 / SNES
audio profile    11025 Hz stereo
```

The 11025-Hz choice is not inherited blindly from SF2000. Independent XGO stock-firmware disassembly proves that family 0x08 selects the same 11025-Hz sound profile inside stock `run_emulator()`.

## Successful CI

```text
workflow run     33836747646
job              100910728662
result           success
artifact         xgo-native-snes-link-candidate
artifact ID      9923539928
artifact digest  sha256:318a3ff58285cf82d44db05470710c7a62cb9a3e1f6c889adae20dd91089e2c9
```

## External image closure

```text
undefined symbols     0
payload/file-backed   646,644 bytes
runtime image       1,399,284 bytes
reserved window    13,479,424 bytes
remaining          12,080,140 bytes
```

Hashes:

```text
xgo-snes.elf
0c7e53e5beb660ecced4e30ef161b305c9ee541692c6f306e288f714f6f2f94a

xgo-snes.bin
93c177cd903d45ebd8b244a43f3f39c099dccfc9893ef17ae5900481b85f1eb3

core-snes9x2005.xgc
ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

The image occupies only about 10.4% of the reserved external-core runtime window.

## Guarded injected loader

Source:

```text
tools/multicore/native_snes/xgo_snes_loader.c
```

Build result:

```text
loader binary    1,359 bytes
cave capacity    3,200 bytes
entry            0x80001500
GP references    0
GOT/sdata/sbss   absent
```

The loader preserves the native-NES safety model:

1. refuse takeover if live stock heap already reaches the external-core window;
2. open `/mnt/sda1/cores/snes9x2005/core.xgc`;
3. validate XGOC framing, header CRC, payload CRC and bounds;
4. stop the stock sound task using the stock contract;
5. reserve upper RAM;
6. load payload and zero runtime/BSS tail;
7. repair IRQ GP using XGO's own startup instructions;
8. flush D/I caches;
9. enter the external image;
10. restore RAMSIZE after return;
11. fall back to untouched stock SNES on any pre-entry failure.

## Native launch interception

The already-confirmed stock dispatch is:

```text
run_game SNES call     runtime 0x80360e40
ASD offset             0x00360e40
stock target           run_snes @ 0x8035f9d8
stock bytes            76 7e 0d 0c
replacement target     loader @ 0x80001500
replacement bytes      40 05 00 0c
```

The strict patcher is:

```text
tools/multicore/native_snes/build_native_snes_asd.py
```

It requires the exact preserved firmware SHA-256, verifies the zero-filled loader cave and stock SNES JAL bytes, modifies only the cave/JAL plus LCFG metadata, and never creates `Firmware.upk`.

## Shared runtime reuse

Core #2 reuses the same components already exercised by external FCEUmm:

- XGOC image format and upper-RAM window;
- GP-independent injected loader model;
- external entry GP veneer;
- stock <-> external GP bridges;
- stock RGB565 video callback;
- stock stereo audio batch callback;
- stock two-port libretro input callback;
- preloaded-ROM heap policy;
- generic libretro save-state adapter;
- stock save-state UI callback slots;
- controlled environment shim;
- stock `run_emulator()` lifecycle.

The SNES-specific frontend is thin. Its main semantic difference is setting family `0x08`, which deliberately selects XGO's hardware-confirmed native 11025-Hz SNES profile.

## What remains before hardware

The architecture is no longer blocked by linking, memory fit, MIPS ABI, ROM handoff, input, RGB565 transport, serialization or loader cave size.

Remaining offline gates are:

1. independently apply the strict SNES patcher to the preserved stock ASD and record its exact output hash/LCFG CRC;
2. package the patched ASD and `core-snes9x2005.xgc` in the same disposable-SD layout used by native NES testing;
3. audit the final package contents to ensure no firmware updater/SPI-NOR material is present;
4. choose a hardware test ROM with known visible stock slowdown/choppiness.

After those checks, the next meaningful evidence must come from physical XGO hardware.

## Confidence

**CONFIRMED:** exact XGO SNES dispatch target and stock wrapper.

**CONFIRMED:** XGO family 0x08 uses 11025-Hz stereo setup.

**CONFIRMED:** pinned Snes9x2005 uses the same 11025-Hz HC15xx profile.

**CONFIRMED:** memory-backed Snes9x2005 build succeeds.

**CONFIRMED:** complete XGO-linked SNES image has zero undefined symbols and large RAM headroom.

**CONFIRMED:** guarded SNES loader builds GP-free and fits the stock injection cave.

**NOT YET HARDWARE CONFIRMED:** execution/gameplay/performance of external Snes9x2005 on physical XGO.
