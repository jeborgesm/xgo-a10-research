# Interactive XGO mapper v11 final border refinement

## Hardware status entering v11

Mapper v10 hardware testing confirmed:

- artificial blue pause-menu background is gone;
- artificial blue editor-side background is gone;
- mapper entry remains usable;
- remapping works;
- persistence remains intact.

The only remaining presentation defect is that the mapper canvas is clipped by approximately 1-2 pixels on the left, top, and bottom edges, hiding those border lines.

## v11 scope

Firmware is unchanged from hardware-proven v10.

Only `Resources/gpapi.bvs` changes. The mapper canvas is inset by two pixels on the left, top, and bottom so the corresponding borders remain visible on the physical display.

No input, renderer hook, mapping ABI, save path, or persistence logic changes.

## Identity

```text
firmware SHA-256 (unchanged from v10):
d6557ae72b4f3f2a60b82f35069b01a72b537977460154d642baf697be784782

gpapi.bvs SHA-256:
934da0444e009050d1392b2c37ddfc3cd8810c8f23ef0a54c3bd6099494f7325

card ZIP SHA-256:
ad0d5dac9131ca7e464f9bbf2cf98be1cece6605c1b9f633a65d7ad44e975c8b
```

## Final hardware check

1. Open Mapper and verify the left, top, and bottom borders are now visible.
2. Perform one quick remap and confirm behavior/persistence remain unchanged.

If this passes, the mapper branch is ready to merge/close.