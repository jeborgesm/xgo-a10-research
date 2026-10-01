# Arcade artwork repair — golden-length shared scratch namespace

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **OFFLINE REPAIR DESIGN CLOSED; source corrected; no hardware candidate yet**

## Root-cause constraint

The exact Test04 CPS1 materializer proved that the inherited JPEG preparation code uses fixed-count copies into decoder-private pathname slots. The safe repair should therefore preserve the ancestral copy geometry rather than enlarge or relocate opaque decoder-private state.

## Exact length equivalence

Golden Test75 FC scratch paths:

```
/mnt/sda1/FC/art/.xgo.jpg
/mnt/sda1/FC/art/.xgo.rgb565
```

Lengths including terminating NUL:
- JPEG scratch: 26 bytes
- RGB565 scratch: 29 bytes

Proposed Arcade scratch paths:

```
/mnt/sda1/ARCADE/.xgo.jpg
/mnt/sda1/ARCADE/.xgo.rgb565
```

Lengths including terminating NUL:
- JPEG scratch: 26 bytes
- RGB565 scratch: 29 bytes

They are **exactly length-isomorphic** to the HW-proven FC ancestor.

Therefore the existing fixed-copy loops and decoder-private slots can remain unchanged.

## Separation of source artwork and scratch

Family source artwork remains structured and family-specific:

```
/ARCADE/CPS1/art/<stem>.jpg|jpeg
/ARCADE/CPS2/art/<stem>.jpg|jpeg
/ARCADE/IGS/art/<stem>.jpg|jpeg
/ARCADE/NEOGEO/art/<stem>.jpg|jpeg
```

Only the disposable decoder scratch pair is shared:

```
/ARCADE/.xgo.jpg
/ARCADE/.xgo.rgb565
```

This does not change catalog identity, source retention, ZFB naming, runtime ZIP naming, or family selection.

## Why one shared pair is safe for the current architecture

Command 6's locked design processes the four family materializers sequentially in list order 7,8,9,10. The inherited materializer removes stale scratch paths before decode and cleans successful scratch output. There is no concurrent family materialization in the current design.

Thus one shared scratch pair avoids four long family paths while preserving the proven worker ABI.

If future work introduces concurrency, this assumption must be revisited.

## Source correction

`tools/arcade_refresh/build_materializer_literal_blocks.py` now emits the shared golden-length scratch paths for `art_jpg` and `art_rgb`, while preserving family-specific `art_stem_jpg` and `art_stem_jpeg`.

This is a source correction only. It does not authorize Test05 by itself.

## Mandatory offline audit before candidate

Before packaging:
1. rebuild all four retargeted materializers deterministically;
2. verify each decoder tail remains byte-identical to golden SHA `9ca2599d...`;
3. verify every scratch-path live reference resolves to the shared short literals;
4. verify family source-art references remain family-specific;
5. verify fixed-copy bounds and destination geometry are unchanged from Test75;
6. verify Arcade finalizer splice at `+0x09B4` is unchanged;
7. verify no unexpected binary deltas outside literal block/immediate retargets;
8. separately preserve the still-open live-list/cache issue and compatibility-gate work.

No hardware candidate until those audits pass.
