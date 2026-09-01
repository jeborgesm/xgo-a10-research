# XGO LCFG Header Integrity Fields

Status: **payload-size and CRC32/MPEG-2 fields confirmed exactly against the shipped XGO `bisrv.asd`; first metadata block appears to be stock-family format data rather than XGO-specific board identity.**

## Scope

This pass treats the 0x200-byte `LCFG` prefix as a real file-format structure instead of generic opaque metadata.

The preserved XGO image is:

```text
file size            12,768,452 bytes
LCFG header size          0x200 bytes
payload size          12,767,940 bytes
```

## Confirmed payload-length field

The XGO header contains:

```text
offset 0x184: c4 d2 c2 00
```

interpreted little-endian:

```text
0x00c2d2c4 = 12,767,940
```

This is exactly:

```text
file_size - 0x200
```

so offsets `0x184..0x187` are the application payload length.

This is independently corroborated by `bnister/sf2000_hcrtos/crc.c`, whose LCFG builder writes the payload size to exactly `0x184..0x187`.

## Confirmed CRC field

The XGO header contains:

```text
offset 0x18c: 11 1f e5 5e
```

or little-endian:

```text
stored CRC = 0x5ee51f11
```

Computing CRC-32/MPEG-2 over exactly the bytes from file offset `0x200` through EOF gives:

```text
computed CRC-32/MPEG-2 = 0x5ee51f11
```

The match is exact.

The public HCRTOS `crc.c` tool documents and implements the same contract:

```text
LCFG_HEADER_SIZE = 0x200
CRC input        = payload beginning at 0x200
CRC variant      = CRC-32/MPEG-2
stored at        = 0x18c..0x18f
```

This also matches FrogQEMU's reconstructed vendor boot chain, which explicitly verifies the stock ASD CRC32/MPEG-2 before transferring control to the application.

## Header layout now confirmed

Useful known fields are therefore:

```text
0x000..0x003  ASCII "LCFG"
0x004..       metadata / runtime-copied configuration block
0x17d..0x17f ASCII "End"
0x180..0x183 01 fe 01 01      # meaning not yet assigned
0x184..0x187 payload length   # CONFIRMED
0x188..0x18b 00 00 03 00      # meaning not yet assigned
0x18c..0x18f CRC32/MPEG-2     # CONFIRMED
0x200..EOF   executable/application payload
```

For the XGO specimen:

```text
payload length = 0x00c2d2c4
payload CRC    = 0x5ee51f11
```

## Important correction to the board-config interpretation

A public DataFrog SF2000 file-identification signature reproduces the same early LCFG metadata sequence seen in the XGO, including:

```text
LCFG
logo.m2v
2222Z
...
01 00 00 00 e0 01 10 01 1f 00 0a 00 2d 00 0a 00
03 00 10 00 00 00 00 00 00 00 01 00 ...
```

That includes the XGO byte at file offset `0x72` which the application later reads as LCD `cur_type`.

Therefore:

- the runtime copy from `0x80f00004` is real and active;
- `config[0x6e]` / file offset `0x72` really is consumed as `cur_type` by this application build;
- but the value `0` at that location is **not currently a useful XGO-specific fingerprint**, because the same metadata appears in the stock SF2000-family signature.

The stronger XGO-specific display evidence remains the executable board path that explicitly initializes `LCD_TYPE_ST7789V_MCU8080` plus the recovered 320x240 `ST7789V_80I` command table.

## Why this matters

We now have a deterministic validity test for any candidate or modified XGO `bisrv.asd`:

1. verify `LCFG` magic;
2. read little-endian payload size at `0x184`;
3. require `payload_size == file_size - 0x200`;
4. compute CRC32/MPEG-2 over bytes `0x200..EOF`;
5. compare with little-endian value at `0x18c`.

This is useful for future binary comparison, patching, or experimental firmware reconstruction because a modified payload can be repacked without guessing the integrity scheme.

It also separates two different concepts that had started to blur together:

```text
LCFG header structure / integrity
        !=
XGO-specific board adaptation
```

The XGO's actual hardware differences are increasingly visible in executable board-support code, GPIO choices, panel initialization, controller scanning, battery thresholds, and other runtime routines rather than in the generic early LCFG metadata block.

## Confidence

### CONFIRMED

- LCFG header is 0x200 bytes;
- XGO offset `0x184` stores payload size;
- XGO payload length is exactly `file_size - 0x200`;
- XGO offset `0x18c` stores CRC32/MPEG-2;
- recomputed CRC over the XGO payload matches `0x5ee51f11` exactly;
- public HCRTOS tooling writes those same fields at those same offsets;
- stock boot-chain reconstruction verifies this CRC before application handoff.

### STRONG EVIDENCE

- much of the early 0x8c runtime-copied metadata is generic SF2000-family configuration rather than an XGO-only descriptor;
- XGO-specific board archaeology should prioritize executable board-support deltas over those generic metadata bytes.

### OPEN

- exact semantics of header words at `0x180` and `0x188`;
- semantic names for most fields in the runtime-copied `0x8c` metadata block;
- whether sibling OEM builds vary those metadata fields meaningfully;
- whether the XGO bootloader performs any additional checks beyond payload size and CRC32/MPEG-2.