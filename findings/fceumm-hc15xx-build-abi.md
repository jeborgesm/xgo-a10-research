# Existing HC15xx FCEUmm build ABI matches XGO

Status: **confirmed from the Data-Frog-Central Multicore core manifest and pinned FCEUmm Makefile**.

## Headline

The FCEUmm source used by the maintained SF2000/GB300 Multicore ecosystem already has a dedicated `platform=sf2000` static-build target whose machine ABI matches the XGO external-core ABI independently reconstructed in this repository.

Therefore the first XGO FCEUmm task is **not** an emulator CPU port. The emulator can already be built for this HC15xx/MIPS execution environment; the XGO-specific work belongs primarily in the frontend/linker/compatibility layer.

## Known Multicore core snapshot

`Data-Frog-Central/multicore_cores` currently pins:

```text
submodule: libretro-fceumm
repository: madcock/libretro-fceumm
commit: e6111e684e7a7761f3f1d6c80d0a825e2c8cdc7e
```

The maintained Multicore build scripts classify FCEUmm as a main/always-built emulator for both SF2000 and GB300 build variants.

## `platform=sf2000` build contract

The pinned FCEUmm Makefile contains a dedicated SF2000 block:

```text
TARGET = fceumm_libretro_sf2000.a
compiler prefix = /opt/mips32-mti-elf/2019.09-03-2/bin/mips-mti-elf-

-EL
-march=mips32
-mtune=mips32
-msoft-float
-G0
-mno-abicalls
-fno-pic
-ffast-math
-fomit-frame-pointer
-ffunction-sections
-fdata-sections
-DSF2000

STATIC_LINKING = 1
EXTERNAL_ZLIB  = 1
```

## Match to the XGO research toolchain

The XGO probe loader/core were independently built using LLVM with:

```text
--target=mipsel-none-elf
-march=mips32
-msoft-float
-G0
-mno-abicalls
-fno-pic
-ffreestanding
```

The important ABI properties therefore agree:

```text
architecture   MIPS32
endianness     little endian
floating ABI   software float
global small data disabled with -G0
ABI calls      disabled
PIC            disabled
static image   yes
```

The GCC-vs-LLVM difference is a toolchain choice, not a CPU ABI incompatibility.

## Architectural consequence

The external emulator should remain largely platform-agnostic libretro code:

```text
FCEUmm static MIPS archive
        |
XGO external-core/frontend wrapper
        |-- XGO environment compatibility shim
        |-- stock XGO video callback
        |-- stock XGO stereo audio callback
        |-- stock XGO P1/P2 callback
        |-- XGO stock function/global linker map
        |
stock XGO board firmware
```

This is preferable to modifying FCEUmm with XGO-specific GPIO/display code.

## What remains build-specific

A real XGO FCEUmm binary still needs:

1. the pinned/known-good FCEUmm source tree or a newer revision carrying equivalent SF2000 build support;
2. the matching external-zlib/static-link environment expected by the Multicore build;
3. linkage against the XGO wrapper and the XGO stock symbol map rather than the SF2000 linker map;
4. an unresolved-symbol audit of the final executable;
5. the XGO environment shim, including RGB565-only negotiation, 44.1-kHz target sample rate, and `fceumm_region` normalization;
6. temporary XGO system-family selection `0x01` while the core runs.

## Conclusion

The emulator port itself is already solved by the HC15xx community lineage. The remaining engineering problem is much narrower:

> take an existing MIPS32/soft-float static FCEUmm core and bind it safely to XGO's stock frontend services.

That is a substantially lower-risk task than porting or replacing the entire XGO firmware/emulator stack.
