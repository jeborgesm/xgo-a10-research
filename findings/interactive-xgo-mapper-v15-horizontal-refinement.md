# Interactive XGO mapper v15 horizontal-only refinement

## Baseline

v14 is hardware-confirmed working with corrected vertical selector geometry, correct A/Confirm save+play behavior, and functional persistence.

## v15 scope

Do not change Y geometry again. v15 changes only the horizontal layout:

- mapper canvas width reduced by 8% relative to v14 while preserving its 422-pixel height;
- canvas shifted to create larger left/right margins and recover the clipped left border;
- physical marker X transformed from 301 to 319;
- target marker X transformed from 478 to 481;
- marker Y base remains 154;
- marker row stride remains 37;
- no input, mapping, persistence, or save behavior changes.

## Identity

```text
firmware SHA-256:
6c42f88b0e08e2252debb7cc9feceb945a95ea4add85fd4b77cfefe1c39210c9

LCFG CRC-32/MPEG-2:
0x907aef8f

gpapi.bvs SHA-256:
e0bd2e17bcd8ad325f6e4cd93fd1521cf68a9e9b47bcec87520a4517afdf8233

card ZIP SHA-256:
0d3cc5e2c8a6988d51d3e536711b078b60d743ef92bca4098ebcac06ed027da7
```

## Hardware check

1. Confirm left border is visible.
2. Confirm all six yellow markers remain vertically centered on their labels.
3. Confirm horizontal marker positions remain visually associated with each row.
4. Perform one remap and restart to verify no functional regression.