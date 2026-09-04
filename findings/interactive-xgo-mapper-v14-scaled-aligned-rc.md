# Interactive XGO mapper v14 scaled/aligned release candidate

## Motivation

Hardware testing of v10 showed that the yellow selector markers were not vertically centered on the row labels. In particular, the MAP TO marker could visually sit between adjacent rows such as Y and A. v11-v13 also demonstrated that scaling only the static resource without transforming the dynamic marker coordinates causes increasing misalignment.

## Root cause

The v10 static label centers are approximately:

```text
150, 192, 234, 276, 318, 360
```

but the firmware marker routine used those values as the marker rectangle's **top edge**. The yellow marker is 14 pixels tall, so its center was about 7 pixels too low.

The marker routine also used a fixed 42-pixel row stride:

```text
32*i + 8*i + 2*i = 42*i
```

## v14 coordinated transform

v14 starts from hardware-proven v10 and scales the mapper canvas to 88% (12% smaller). The dynamic marker geometry is transformed at the same time.

Firmware changes:

```text
physical marker X: 270 -> 301
target marker X:   470 -> 478
marker Y base:     150 -> 154
row stride:         42 -> 37
```

The 37-pixel stride is implemented by changing the marker index arithmetic from:

```text
32 + 8 + 2 = 42
```

to:

```text
32 + 4 + 1 = 37
```

This keeps marker positions aligned with the 88%-scaled label rows.

The static legend is also corrected to match hardware-proven behavior:

```text
A = OPEN / SAVE+PLAY
ARROWS = CHANGE
```

The previous START+SELECT save wording is removed because hardware testing showed A/Confirm is the working save-and-resume action.

## Identity

```text
firmware SHA-256:
d826d26c7c1a416c4967b5424a757e7f0f1bff84f2949df4fd42577d70bb2b4b

LCFG CRC-32/MPEG-2:
0xb5e56398

gpapi.bvs SHA-256:
46ad48aa063dcb5ab58e4c1d4634944a079627d8359311b80161cb03af5f1314

card ZIP SHA-256:
daf2d41a7a7b3e275eb235169fb7020beb4b5933b5f4889b0336c665b48b6470
```

## Hardware acceptance test

1. Open Mapper and verify all borders have comfortable margins.
2. Move PHYSICAL selector through X/Y/L/A/B/R and confirm each yellow marker is vertically centered on its row.
3. Move MAP TO selector through B/Y/A/X/L/R and confirm each marker clearly identifies exactly one row.
4. Confirm A/Confirm saves and resumes gameplay.
5. Verify one remap still persists after restart.

If selector alignment is correct, this is the preferred release candidate over the display-only v11-v13 experiments.