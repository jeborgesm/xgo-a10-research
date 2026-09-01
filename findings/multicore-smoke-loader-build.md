# XGO minimal loader smoke test — build and patch audit

Status: **minimal loader built successfully; patched ASD generated and audited locally but not executed on hardware**.

## Purpose

Before attempting a complete Multicore port, the safest useful proof is to validate only three assumptions:

1. the XGO boot chain accepts a correctly resealed modified `bisrv.asd`;
2. code injected in the confirmed zero-filled loader window at `0x80001500` executes;
3. injected code can call resolved stock XGO firmware APIs.

The smoke loader deliberately avoids display drivers, emulator cores, SPI NOR, updater paths, and other board-sensitive code.

## Behavior

The injected entry has the same two-argument signature as the stock GBA launcher:

```c
void xgo_loader_entry(const char *filename, int load_state);
```

For all filenames except:

```text
/mnt/sda1/ROMS/XGO_PROBE.gba
```

it immediately forwards to the original XGO function:

```text
run_gba = 0x80360110
```

For the explicit probe filename it creates:

```text
/mnt/sda1/XGO_PROBE.OK
```

containing:

```text
XGO injected loader executed successfully.
```

and then returns. This makes execution observable using only an SD-card file write.

## Stock functions used

The smoke loader uses only already-resolved stock functions:

```text
fopen   = 0x802b3524
fwrite  = 0x802b42ac
fclose  = 0x802b2f40
run_gba = 0x80360110
```

No direct GPIO, LCD, VPO, OSD-driver, ADC, SPI-NOR, or updater functions are used.

## Host build proof

The loader was successfully compiled in the research environment using Clang 17's MIPS target rather than requiring the historical MIPS MTI GCC toolchain:

```text
clang --target=mipsel-none-elf
-march=mips32
-msoft-float
-G0
-mno-abicalls
-fno-pic
-ffreestanding
-fno-stack-protector
-fno-builtin
```

The linker places the entry at exactly:

```text
0x80001500
```

Observed build properties:

```text
loader .text binary size : 339 bytes
available injection space: 3200 bytes
ELF entry                : 0x80001500
relocations               : none
```

Thus the proof loader consumes only about 10.6% of the confirmed XGO loader hole.

## Exact XGO patch site

The unmodified XGO firmware contains:

```text
0x80360cf0  move $a0,$s2
0x80360cf4  jal  0x80360110   # run_gba
0x80360cf8  move $a1,$zero
```

Raw bytes at file offset `0x360cf4` are:

```text
44 80 0d 0c
```

For an injected entry at `0x80001500`, the replacement `jal` is:

```text
40 05 00 0c
```

The argument setup remains untouched.

## Local patched-image audit

A patched copy of the preserved XGO image was generated locally for byte-level analysis only. It has not been run on hardware.

The modifications are limited conceptually to:

```text
0x018c..0x018f  recomputed LCFG CRC32/MPEG-2
0x1500..0x1652  339-byte loader placed inside confirmed zero-filled space
0x360cf4..      run_gba JAL redirected to 0x80001500
```

The payload-size field at `0x184` does not change because the ASD file length is unchanged.

The resealed patched image produced:

```text
CRC32/MPEG-2 = 0x3c71eb9c
SHA-256      = bb2369ec8f51d6d3cf766ea122772ae8a8bbfb6885a5868ce675c20818a20feb
```

These values identify only this specific unexecuted research build and are not a general XGO firmware signature.

## Why this is a useful milestone

A successful hardware smoke test would prove the complete SD-only modification chain without yet introducing emulator-core complexity:

```text
internal stock bootloader
    -> modified + resealed SD bisrv.asd
    -> stock frontend
    -> patched GBA call site
    -> injected 0x80001500 loader
    -> stock fopen/fwrite/fclose
    -> marker file on SD
```

Normal GBA launches remain pass-through in the smoke loader, reducing the test surface.

## Safety boundary

This experiment is intentionally separate from:

```text
/mnt/sda1/UpdateFirmware/Firmware.upk
```

It does not invoke the XGO SPI-NOR updater or intentionally modify internal flash.

The generated ASD should still be regarded as experimental. The first physical test, if/when performed, should use a separate SD card containing a complete backup-derived filesystem and **must not include `UpdateFirmware/Firmware.upk`**.

## Source files

- `tools/multicore/xgo_smoke_loader.c`
- `tools/multicore/xgo_smoke_loader.ld`
- `tools/multicore/xgo_stockfw_symbols.ld`

Stock image fingerprint used for all offsets:

```text
SHA-256 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```
