# Audio OSD v7 — 1-pixel gray border candidate

Date: 2026-09-05
Branch: `research-audio-osd`

Status: **READY FOR HARDWARE TEST**

## Base

Built from Audio OSD v6 boot-hidden frontend/menu-refresh candidate.

Base firmware SHA-256:

```text
4bda2556cc231ffc73b15e7b9822b0376cf6beae09a0029df7aa94e8542a65ed
```

## Change

The existing 64x8 volume OSD footprint now uses a one-pixel medium-gray outline.

```text
RGB565 border = 0x8410
```

The footprint remains exactly 64x8. The outer row/column pixels are gray, interior filled volume remains white, and interior unused volume remains black.

This is intentionally a rendering-only change.

## Invariants

- OSD payload remains exactly 1548 bytes.
- OSD cave remains `0x80002780..0x80002d8b`.
- v6 frontend helper begins at `0x80002d90` and is untouched.
- no larger framebuffer backup;
- no extra display write;
- no additional cave allocation;
- fine-volume policy unchanged;
- boot-hidden initialization unchanged;
- frontend-only repaint gate unchanged;
- CPS1 scheduler unchanged;
- Mapper and SNES paths unchanged.

## Candidate

```text
xgo-audio-osd-v7-gray-border-test.zip
ZIP SHA-256
9f081bdcd3a3701d5935e4c7216e21885c24654335e426cc526c024e7bc295af

firmware SHA-256
46b3a8e9a2c75546cdc02b586dc7f7ba529c833c0910a697344dc4d2a884178c

LCFG CRC-32/MPEG-2
0x49bbe49b
```

## Hardware expectation

The bar should remain hidden at power-on until the Volume button is pressed. When visible, the gray border should make the complete bar extent readable over black game/menu backgrounds without changing the successful v5/v6 game/menu behavior.
