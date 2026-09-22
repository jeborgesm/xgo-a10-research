# Test120 hardware failure and Test119 backdrop-loop audit

Date: 2026-09-21
Protected baseline: Test119
Status: Test120 REJECTED; no replacement candidate emitted yet

## HW Test120 result

Observed:
- selecting Refresh produced no visible selector and the device stopped responding to buttons;
- pressing Volume still produced the Volume OSD;
- that presentation event then exposed the black Refresh screen;
- selector input remained unresponsive.

Therefore Test120 is rejected. Test119 remains the protected checkpoint.

Test120 introduced two unneeded execution changes: a stock `memset` call from inside the selector renderer and an additional text-renderer/footer helper. The failure does not falsify Test119's renderer or selector lifecycle.

## Exact Test119 backdrop loop (BIN)

The existing HW-proven renderer is not an opaque rectangle primitive. At `0x80A38ABC` it executes:

```text
80A38ABC  lw    s0,-5136(gp)       # framebuffer
80A38AC0  lui   t0,0x0001
80A38AC4  addu  t0,s0,t0
80A38AC8  lhu   t1,-1516(t0)       # sample existing RGB565 pixel
80A38ACC  lui   t0,0x0001
80A38AD0  addu  t0,s0,t0
80A38AD4  addiu t0,t0,-1456        # initial write pointer = fb+0xFA50
80A38AD8  li    t2,360              # outer count
80A38ADC  move  t3,t0
80A38AE0  li    t4,560              # inner halfword count
80A38AE4  sh    t1,0(t3)
80A38AE8  addiu t3,t3,2
80A38AEC  addiu t4,t4,-1
80A38AF0  bne   t4,zero,80A38AE4
80A38AF4  nop
80A38AF8  addiu t0,t0,0x500
80A38AFC  addiu t2,t2,-1
80A38B00  bne   t2,zero,80A38ADC
80A38B04  nop
```

This is the mechanism that Test113/Test118/Test119 actually exercised on hardware.

## Important correction

It is NOT yet evidence-safe to describe the four immediates (start offset, 360, 560, 0x500) as ordinary x/y/width/height on a conventional tightly packed 640x480 surface.

The inner loop advances 1120 bytes, while the outer update advances the base by 1280 bytes independently. The exact storage/presentation geometry represented by those values must be reconciled before changing them. Blindly changing 560->640 and 360->480 would be another guessed hardware candidate and violates the continuity protocol.

## Next gate

Use the exact Test119 binary and existing framebuffer/presentation findings to determine:
1. why the renderer samples `fb+0xFA14`;
2. why writes begin at `fb+0xFA50`;
3. the meaning of outer count 360;
4. the meaning of inner count 560;
5. why the base advances `0x500` per outer iteration;
6. whether this is a 640x480 surface, doubled/interlaced surface, or another stock frontend layout.

Only after that closure should a candidate be emitted. The candidate must change only the minimum loop immediates required; no new calls, helpers, hooks, stack changes, or footer text in the same hardware test.
