# Interactive XGO mapper v9 clean-background release candidate

## Root cause correction

Hardware testing of v7/v8 showed that changing `gpapi.bvs` did not remove the blue blocks behind the pause-menu Mapper row or the left side of the mapper screen. The remaining blue areas were therefore not resource pixels.

Binary comparison identified the actual source: mapper v5 introduced an explicit framebuffer-clear rectangle before drawing the added Mapper row. That workaround was carried forward unchanged into v6, v7, and v8. It is the source of the persistent blue blocks.

## v9 strategy

v9 returns to the hardware-proven v4 firmware baseline, which predates the framebuffer-clear workaround, and applies only the desired label-case change:

```text
MAPPER -> Mapper
```

The v9 resource uses the cleaned mapper artwork with no baked-in duplicate MAPPER label. Therefore:

- no v5+ framebuffer-clear rectangle remains;
- no baked-in duplicate Mapper/MAPPER label remains;
- the mapper behavior and persistence path are the already hardware-proven v4 implementation;
- the native pause entry reads `Mapper`.

## Identity

```text
firmware SHA-256:
b6f978eff6198274e664ae6cf86258fbaf6b8141b970910d58981bebf101a933

LCFG CRC-32/MPEG-2:
0x156e88ec

gpapi.bvs SHA-256:
1582400e3fad2ba195d43492599ceb421456081f02cfa754d9477e6a4416499e

card ZIP SHA-256:
a1d1e505832f6f87d1e65292384859e4eed3d0b3cb6c88d1ee95187ff1195552
```

## Hardware check

1. Open pause menu and verify `Mapper` has no artificial blue rectangle behind it.
2. Highlight Mapper and verify the left side is not replaced by a firmware-drawn blue block.
3. Enter mapper and verify the cleaned resource appears without duplicate label.
4. Confirm one arbitrary remap and persistence still work.

If this passes, presentation cleanup is complete.