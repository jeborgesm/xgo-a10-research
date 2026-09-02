# Exact offline XGO FCEUmm SD-staging rehearsal

Status: **completed successfully against the preserved XGO firmware; not yet executed on hardware**.

## Purpose

Before placing anything on a physical SD card, the current production artifacts were combined offline with the exact preserved XGO `bisrv.asd` and audited as a complete staging rehearsal.

This used three independently produced inputs:

```text
preserved stock XGO bisrv.asd
CI-built production XGOC loader
CI-built production FCEUmm core.xgc
```

No physical SD card, SPI-NOR update path, `Firmware.upk`, or game ROM was involved.

## Inputs

Stock firmware:

```text
size       12,768,452 bytes
SHA-256    869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

Injected loader from loader-preflight CI:

```text
size       820 bytes
SHA-256    9ca075712c1c101a7de41cffea6a03435d50b1c3ed6d7285462cfe4efaded99f
```

FCEUmm XGOC from link-lab CI:

```text
SHA-256    46d5678ecbaddff5e1f5d1f696aea0bad6a397ca4c7797f3f452a3b03742c4ac
```

## Guards revalidated before patching

The offline rehearsal independently rechecked the same critical signatures used by the repository patcher:

```text
stock SHA-256 exact match
0x1500..0x217f all zero before injection
loader <= 3200 bytes
0x360cf4 original GBA jal bytes = 44 80 0d 0c
0x1270 startup GP pair          = c3 80 1c 3c 74 47 9c 27
0x49744 original IRQ bytes      = 3a 41 0c 0c 00 00 00 00
```

The rehearsal then:

1. inserted the 820-byte loader at file/runtime offset `0x1500`;
2. patched `0x360cf4` from stock `jal run_gba` to `jal 0x80001500`;
3. copied the validated startup GP-init pair to `0x49744..0x4974b`;
4. preserved the ASD payload size;
5. recomputed and wrote CRC32/MPEG-2 at `0x18c`.

## Patched ASD result

```text
payload size field     unchanged / 0x00c2d2c4
new payload CRC        0xa0bf7d8b
patched ASD SHA-256    86610a29334223951cedb1564ec0ee4d53a762ad0c8f5b50b09ec46155eded29
```

The recalculated CRC over `0x200..EOF` exactly matches the value written into the LCFG header.

## Binary-diff audit

The only semantic regions modified are:

```text
0x0000018c..0x0000018f   LCFG payload CRC
0x00001500..0x00001833   current injected loader runtime/file-backed area
0x00049744..0x0004974b   IRQ-path GP repair instruction pair
0x00360cf4..0x00360cf7   GBA dispatcher JAL word
```

Because the original injection cave is zero-filled and the loader itself contains zero bytes, only **644 individual bytes** differ when comparing the full images byte-for-byte. The changed-byte count is therefore smaller than the 820-byte loader file size without implying any omitted loader data.

The patched GBA JAL changes only three physical bytes because the high opcode byte remains `0x0c`:

```text
stock    44 80 0d 0c
patched  40 05 00 0c
```

No LCD tables, board configuration, emulator payloads, updater code, resources, or SPI-NOR routines are modified.

## XGOC revalidation

The staged core independently passed XGOC v1 checks:

```text
magic          XGOC
version        1
header size    32
load           0x87000000
entry          0x87000098
payload        1,567,784 bytes
runtime        3,841,632 bytes
payload CRC    0x7fcbef5b
header CRC     0x7c8f0683
```

The runtime image remains entirely below the stock heap ceiling `0x87cdae00`.

## Launch-token rehearsal

A zero-byte browser token was staged as:

```text
/ROMS/fceumm;ScienceFrog.nes.gba
size = 0
```

with the real-ROM path contract:

```text
/ROMS/fceumm/ScienceFrog.nes
```

No NES ROM was copied or fabricated during the rehearsal.

## Classification

**Confirmed offline:** the exact current loader + core artifacts can be combined with the preserved stock XGO firmware into a resealed ASD whose only binary changes are the intended loader/hook/IRQ/CRC regions; the XGOC core and zero-byte launch-token layout also revalidate independently.

**Not yet confirmed:** device boot/execution. The remaining validation boundary is physical hardware behavior, not an unaccounted-for offline image-construction step.
