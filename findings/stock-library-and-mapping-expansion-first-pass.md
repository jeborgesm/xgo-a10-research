# Stock library and mapping expansion — first pass

Status: **active archaeology**

## Goal

Investigate two high-value usability capabilities for the XGO external-core runtime:

1. intentional button remapping through the stock `.kmp` mechanism;
2. adding/replacing games while preserving the stock XGO system/game-list frontend.

These are now first-class runtime goals alongside Core #2 (SNES), because they determine whether the external-core work becomes a practical expansion of the stock handheld rather than only an execution proof.

## SD-card inventory evidence

Analysis of the preserved card file listing shows that the stock library is overwhelmingly represented as ordinary files directly inside per-system top-level directories:

```text
FC      -> .zfc
SFC     -> .zsf
GB/GBC  -> .zgb
GBA     -> .zgb
MD      -> .zmd
ARCADE  -> .zfb / archives
```

Representative inventory counts from the recovered card listing:

- `FC`: 774 filesystem entries; `.zfc` dominates the NES library.
- `SFC`: 1081 entries; `.zsf` dominates the SNES library.
- `GB`: 977 entries.
- `GBC`: 975 entries.
- `GBA`: 1150 entries, including many `.sav` files.
- `MD`: 835 entries.
- `ARCADE`: 574 entries.

Across the card the dominant wrapped-ROM extensions are approximately:

```text
.zgb  2596
.zsf  1066
.zmd   833
.zfc   757
.zfb   184
```

The preserved card also contains a separate `/ROMS` directory with ordinary user ROM formats (`.nes`, `.smc`, `.sfc`, `.gb`, `.gba`). This is important evidence that the stock per-system lists and the generic/raw-ROM collection are distinct mechanisms.

## Firmware string evidence

The stock firmware contains the following path-format strings near the already-reversed `run_emulator` state machinery:

```text
%s/save/%s.kmp
%s/save/%s.sa%d
%s/%s/save/%s.sa%d
```

It also contains:

```text
%s/Resources/Test.zsf
```

The first three reinforce that keymap/state paths are constructed dynamically from system/game path components rather than being hard-coded per title.

## Initial game-list hypothesis

The SD-card inventory strongly suggests the stock system libraries may be **directory-driven** rather than backed by one obvious external database file. No obvious top-level game-list database or small per-system index file appears in the recovered file listing.

This is not yet proof. The next static target is the firmware directory enumeration path: locate callers of stock `fs_opendir` / `fs_readdir`, then identify the code that filters `.zfc`, `.zsf`, `.zgb`, `.zmd`, etc. and constructs the visible game list.

If confirmed, adding a game to the stock list may reduce to producing a valid wrapped ROM with the correct extension and placing it in the appropriate system directory. That would be a major usability win.

## Mapping evidence already established

The stock input callback and keymap compiler already expose a generic libretro-compatible mapping layer:

- two independent controller ports;
- 16 libretro joypad target IDs per port;
- six remappable action/shoulder physical controls per player;
- fixed D-pad / Select / Start semantics;
- hidden valid L2/R2/L3/R3 targets;
- turbo encoded in bit 16 of the mapping record.

Therefore the remaining mapping archaeology is primarily **persistence and UI**, not low-level controller decoding.

Next targets:

1. determine the exact `.kmp` on-disk record layout and byte order;
2. find the stock `.kmp` read/write functions and identify the known Player-2 mirroring behavior;
3. determine whether a `.kmp` can be generated externally and consumed by stock `run_emulator` without visiting the mapping UI;
4. build a deterministic `.kmp` generator once the format is proven.

## Integration target

The desired architecture is:

```text
stock XGO system/game list
        |
        +-- ordinary stock/wrapped title discovery
        |
        +-- per-title .kmp mapping
        |
        +-- generic external-core dispatch
                |
                +-- NES  -> FCEUmm
                +-- SNES -> Core #2
                +-- later systems
```

The stock frontend should remain visually and behaviorally stock wherever practical. The external runtime should expand what it can launch rather than replace the frontend.
