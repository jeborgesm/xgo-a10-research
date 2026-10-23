# Setup PAL failure — control-flow inspection (2026-10-22)

## Exact BIN observations
The native-toggle firmware has the following instructions:

```
0x80A38AAC lui t0,0x80A4
0x80A38AB0 lw t1,-0x7640(t0)       ; Refresh pending
0x80A38AB4 beq t1,zero,0x80A37FA4 ; custom P1/P2 status hook
0x80A38AB8 nop
0x80A38ABC lw s0,-0x1410(gp)       ; Refresh compositor path begins
...
```

The isolation candidate changes the branch at 0x80A38AB4 back to stock `beq t1,zero,0x80A38F70`, which **bypasses** the P1/P2 status hook but preserves the Refresh-pending nonzero path. That explains missing NTSC underline but does not prove why PAL submenus fail.

Native status routine at 0x80A37FA4 writes pixels to framebuffer pointer `lw a0,-5136(gp)`, using hardcoded offsets `(369*640+541)*2` and row stride 1280 bytes, then jumps to `0x80A38F70` restore epilogue. This is a **640-pixel stride assumption**. Whether PAL uses another stride, a different buffer or changed compositor state is **OPEN**. Do not assert PAL root cause without evidence.

Static Setup bitmap uses three icons on top row, while firmware TV mode label remains at legacy bottom-left. Runtime text must be relocated or TV icon moved to align. User supplied HW screenshots show NTSC/PAL text in bottom-left and both Refresh and Handle submenus invisible in PAL.

## Test constraints
- Keep P1/P2 routing unchanged (HW switching works).
- Restore status hook for NTSC, but do not blindly write fixed-stride framebuffer offsets in PAL without checking destination pointer and framebuffer stride.
- Inspect mode transition code and Refresh/Handle compositor visibility in PAL separately.
- Preserve exact hashes and recovered checkpoints in preceding findings files.
