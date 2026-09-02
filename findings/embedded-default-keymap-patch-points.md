# XGO embedded default keymap patch points

Status: **exact fallback-map addresses and contents confirmed from executable copy paths**.

## Headline

The XGO firmware contains six 48-byte default keymaps embedded directly in `bisrv.asd`. They are copied into the working keymap buffer only when a game-specific `%s/save/%s.kmp` file is not successfully loaded.

This means XGO has two mapping layers:

```text
per-game .kmp exists
    -> load 48-byte per-game map

per-game .kmp absent
    -> copy one of six embedded firmware defaults
```

Therefore a future configuration utility can support both:

1. per-game remapping without firmware modification; and
2. system-wide default remapping by patching these six 48-byte firmware tables and resealing the ASD CRC.

## Working keymap

The active 48-byte map is copied to runtime buffer:

```text
0x810a0f58
```

The mapping compiler then consumes that buffer.

The physical record order is already confirmed as:

```text
X, Y, L, A, B, R    // Player 1
X, Y, L, A, B, R    // Player 2
```

Each record is a 32-bit little-endian value. The low selector chooses the emulator logical button and bit `0x00010000` is the turbo/autofire flag.

## Exact embedded tables

Because the ASD is mapped at runtime base `0x80000000`, the runtime address minus `0x80000000` is also the file offset.

| System | mask | runtime address | ASD file offset |
| --- | ---: | ---: | ---: |
| Arcade / FBA | `0x40` | `0x808ddc44` | `0x008ddc44` |
| GBA | `0x10` | `0x808ddc74` | `0x008ddc74` |
| GB / GBC | `0x20` | `0x808ddca4` | `0x008ddca4` |
| SNES | `0x08` | `0x808ddcd4` | `0x008ddcd4` |
| Mega Drive / Sega | `0x04` | `0x808ddd04` | `0x008ddd04` |
| NES | `0x01` | `0x808ddd34` | `0x008ddd34` |

The tables are packed consecutively in the firmware in a 6 x 48-byte region.

## Exact shipped values

### Arcade / FBA

```text
0000000a 0000000b 00000009 00000008 00000000 00000001
0000000a 0000000b 00000009 00000008 00000000 00000001
```

### GBA

```text
00000009 00000001 0000000a 00000008 00000000 0000000b
00000009 00000001 0000000a 00000008 00000000 0000000b
```

### GB / GBC

```text
00010008 00010000 00010000 00000008 00000000 00010008
00010008 00010000 00010000 00000008 00000000 00010008
```

### SNES

```text
0000000a 0000000b 00000009 00000008 00000000 00000001
0000000a 0000000b 00000009 00000008 00000000 00000001
```

### Mega Drive / Sega

```text
0000000a 0000000b 00000009 00000008 00000000 00000001
0000000a 0000000b 00000009 00000008 00000000 00000001
```

### NES

```text
00010008 00010000 00010000 00000008 00000000 00010008
00010008 00010000 00010000 00000008 00000000 00010008
```

These values match the previously reconstructed logical defaults and independently confirm the table interpretation.

## Executable selection path

The fallback selection in `run_emulator` uses the active system mask and copies exactly 0x30 bytes from one of the six tables into `0x810a0f58`.

Confirmed selector branches include:

```text
0x01 -> NES     source 0x808ddd34
0x04 -> Sega    source 0x808ddd04
0x08 -> SNES    source 0x808ddcd4
0x10 -> GBA     source 0x808ddc74
0x20 -> GB/GBC  source 0x808ddca4
0x40 -> Arcade  source 0x808ddc44
```

After the copy, execution rejoins the same keymap compiler path used for a loaded `.kmp` file.

## Practical implication

A safe future PC workflow can be:

```text
read exact known XGO bisrv.asd
verify SHA / patch signatures
edit selected 48-byte default table(s)
recompute LCFG payload CRC32/MPEG-2
write modified copy to a separate SD card
```

No `Firmware.upk` or internal SPI-NOR update is needed for this kind of default-map experiment.

Per-game `.kmp` files would continue to override the firmware defaults for games that already have them.

## Player 2 implication

Every embedded default contains a full second six-record block, and the shipped maps mirror P1 into P2. This is additional evidence that Player 2 mapping is intentional rather than accidental baggage: the firmware provisions both players at the default-map level as well as carrying P2 through the libretro input callback.
