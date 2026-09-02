# First GP-safe native NES hardware candidate

Status: **offline staging and cross-artifact validation complete; physical XGO execution not yet tested.**

This finding records the first hardware-test overlay assembled from the native NES loader and a production FCEUmm core whose bidirectional `$gp` transitions were verified in final Codescape machine code.

No firmware binary or copyrighted stock image is committed to this repository. The values below are provenance fingerprints for recreating the overlay from the researcher's preserved stock SD image.

## Inputs

### Preserved stock XGO firmware

```text
bios/bisrv.asd
SHA-256: 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
bytes:   12,768,452
```

### Native NES injected loader

CI workflow: `XGO native NES loader preflight`

Run: `33648735009`

Source commit: `7e6c526228c5e9d98ea57308ac68547817d1b9ae`

The loader source blob at that commit is identical to the current branch blob:

```text
tools/multicore/native_nes/xgo_nes_loader.c
blob: 209430a380c3b522bcb87ce4231425d000ccfc79
```

Binary fingerprint:

```text
xgo_nes_loader.bin
SHA-256: 4318d00c9096c5483d3ac5711be3a732515abb35bfc0e9ce7d9e152d04e86586
bytes:   964
load:    0x80001500
cave:    3,200 bytes
headroom: 2,236 bytes
```

### Bidirectional-GP FCEUmm core

CI workflow: `XGO native FCEUmm full link`

Run: `33654506801`

Source commit: `47d217d84976bbf59f8f5dd6e11daa9f2e235639`

```text
core-native-nes.xgc
SHA-256: 32cc83f733954020361259badee0592af9c223d1dab1b7aa30a7d7c585d8625f
load:    0x87000000
entry:   0x87000000
_gp:     0x8718f450
payload: 1,602,672 bytes
runtime: 3,876,104 bytes
```

See `findings/xgo-bidirectional-gp-abi.md` for the final machine-code proof of the stock/core GP transitions.

## Independent offline staging validation

The candidate was assembled from the exact stock firmware, the loader artifact above, and the GP-safe XGOC artifact. The staging process independently repeated the guards implemented by `build_native_nes_asd.py` and `stage_native_nes_test.py`.

Before patching it verified:

- exact stock SHA-256;
- firmware injection cave `0x1500..0x217f` is entirely zero;
- stock bytes at ASD offset `0x00360e20` are exactly `8f 7d 0d 0c`, the little-endian `jal 0x8035f63c` to stock `run_nes`;
- loader length fits the 3,200-byte cave;
- XGOC magic/version/header size/load address/runtime bounds;
- XGOC header CRC-32 and payload CRC-32.

The ASD was then modified only by:

1. writing the 964-byte loader at offset `0x1500`;
2. changing the NES dispatch JAL at `0x00360e20` to `40 05 00 0c` (`jal 0x80001500`);
3. updating LCFG payload size;
4. recomputing the LCFG CRC-32/MPEG-2 over the firmware payload.

## Resulting staged fingerprints

Patched stock firmware:

```text
bios/bisrv.asd
SHA-256: fd9e68ca2d58da9103ecdaad90fe85e9c21fc46af1d471edfa25bf8c56eacb25
bytes:   12,768,452
LCFG payload size:         0x00c2d2c4
LCFG payload CRC-32/MPEG2: 0x84c36920
```

Core copied into the overlay unchanged:

```text
cores/fceumm/core.xgc
SHA-256: 32cc83f733954020361259badee0592af9c223d1dab1b7aa30a7d7c585d8625f
XGOC payload CRC-32: 0x4d5de935
XGOC header CRC-32:  0xc776dea7
```

The locally packaged overlay ZIP containing only:

```text
bios/bisrv.asd
cores/fceumm/core.xgc
XGO-NATIVE-NES-MANIFEST.txt
README-HARDWARE-TEST.txt
```

has:

```text
SHA-256: 5b81efb6303b89c46b9bfe23698ebddac6dbefeabd9b88d4d7172f9639c8508f
```

The ZIP itself is intentionally not committed to GitHub because it contains the preserved/modified stock firmware.

## Hardware-test procedure

Use only a disposable clone of the exact known-good XGO SD card and keep a second untouched bootable card available.

Copy the overlay paths to the disposable card. Do **not** create/install `Firmware.upk` and do not write SPI NOR.

Boot normally and launch one small, known-good `.nes` ROM through the ordinary NES browser. Do not use the earlier `fceumm;<rom>.gba` token mechanism.

Expected control flow:

```text
stock run_game preloads selected NES ROM
        ↓
patched JAL @ 0x80360e20
        ↓
native loader @ 0x80001500
        ↓
validate/load core.xgc @ 0x87000000
        ↓
external entry establishes core _gp
        ↓
FCEUmm/newlib
        ↕ bidirectional GP veneers
stock run_emulator + callbacks/services
```

Failures detected before external transfer retain the native loader's guarded stock fallback. A failure after successful transfer is now a hardware observation rather than a known unresolved static linker/ABI defect.

## Research boundary

At this point the highest-value remaining evidence is physical execution:

- does the live heap guard pass at ordinary NES dispatch;
- does the 1.6 MiB payload load correctly from SD into upper RAM;
- does cache/IRQ state survive the transition;
- does FCEUmm reach its first visible frame;
- are video/audio/input correct on the physical unit;
- does exiting return cleanly through the GP veneers and restored RAMSIZE.

Those observations should be recorded before adding further speculative platform code.
