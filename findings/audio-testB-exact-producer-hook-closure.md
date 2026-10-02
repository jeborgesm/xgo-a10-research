# XGO gameplay audio — Test B exact producer hook closure

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN implementation surface closed; builder committed**

## Exact `retro_run()` sequence [BIN]

Direct disassembly of the exact cumulative firmware closes the relevant stock-FBA path.

```asm
8036C2F4  lw    ra,-24072(gp)       ; existing per-retro_run counter
...
8036C304  addiu t9,zero,-1
8036C308  addiu t8,zero,22050
8036C30C  sb    t9,-30211(gp)
8036C310  sw    t8,-24100(gp)       ; nBurnSoundRate = 22050
8036C314  sw    s3,-24072(gp)       ; counter = old + 1
8036C318  jal   0x80370074
8036C31C  sw    s0,-24108(gp)       ; pBurnSoundOut
8036C320  jal   0x8036FFF4           ; FBA frame engine / BurnDrvFrame path
8036C324  nop
...
8036C370  addu  a0,s0,zero
8036C374  lw    s0,-24180(gp)       ; audio_batch_cb
8036C378  jalr  ra,s0
8036C37C  lw    a1,-24104(gp)       ; callback count = current nBurnSoundLen
```

The rendered-video path reaches the same audio submission:

```asm
8036C3D0  lw    t1,-24176(gp)
8036C3D4  jalr  ra,t1               ; video callback
...
8036C3E0  lw    s0,-24180(gp)
8036C3E4  jalr  ra,s0               ; audio callback
8036C3E8  lw    a1,-24104(gp)       ; same nBurnSoundLen
```

This closes the key ordering question: the producer-length global can be selected immediately before the frame engine and the exact same global is later passed to the audio callback on both render and render-skipped paths.

## No new persistent state required [BIN/INF]

The wrapper already increments an existing per-`retro_run()` counter at GP-24072 before the frame-engine call.

Test B can use that counter's parity:

```text
len = 367 + (frame_counter & 1)
```

Therefore no new RAM state, initialization hook, or unload/reset hook is required.

The starting phase may be either 367-first or 368-first depending on the existing counter phase. Either phase has the same exact two-frame average of 735 samples and therefore the same 22050 samples/s at 60 executed frames/s.

Because the stock scheduler still executes `retro_run()` on render-skipped catch-up frames, the correction follows emulated-frame production rather than visible-frame presentation.

## Minimal hook shape [BIN]

Patch only the existing frame-engine call:

```text
0x8036C320
old 0x0C0DBFFD = jal 0x8036FFF4
new             jal Test-B shim
```

The shim performs:

```asm
lw    t0,-24072(gp)
andi  t0,t0,1
addiu t0,t0,367
sw    t0,-24104(gp)
j     0x8036FFF4
nop
```

The shim **tail-jumps** to the original frame-engine target. The `jal` at `0x8036C320` has already placed `0x8036C328` in `ra`; the tail jump leaves that return address untouched, so the original frame engine returns directly to the unmodified continuation.

The shim uses only caller-saved `t0`, does not alter `gp`, does not allocate a stack frame, and introduces no nested return-address dependency.

## Executable padding surface [BIN]

Exact HW-PASS Test-A firmware contains an injected executable region around `0x807DBAxx`. Existing code ends with a jump at `0x807DBB00`; `0x807DBB04` is its delay-slot NOP. The bytes `0x807DBB08..0x807DBB3F` are zero padding before the existing data block beginning at `0x807DBB40`.

Test B uses only:

```text
0x807DBB08..0x807DBB1F   24 bytes
```

and deliberately leaves the preceding jump delay slot and following padding/data untouched.

The fail-closed builder verifies this padding is still zero in the exact Test-A SHA before writing.

## Producer buffer headroom [BIN + bounded INF]

The stock load path sets `pBurnSoundOut` to:

```text
0x80D3CB30
```

A later static object begins at:

```text
0x80D3D0F8
```

The address delta is:

```text
0x5C8 = 1480 bytes
```

Stereo signed-16 PCM requires 4 bytes/frame:

```text
367 frames = 1468 bytes
368 frames = 1472 bytes
369 frames = 1476 bytes
370 frames = 1480 bytes
```

Thus the proposed 368-frame production remains below the next observed static-object address, with 8 bytes remaining before that boundary.

Classification is deliberately bounded: BIN proves the addresses and physical gap; INF identifies the gap as sufficient backing storage for one additional stereo frame. This does not promote an upstream C array declaration into XGO BIN evidence.

## Why this is preferable to a resampler

The exact target is 367.5 producer frames per emulated frame. Alternating 367/368:

- creates no synthetic/interpolated sample;
- uses FBA itself to generate every submitted sample;
- needs no fractional PCM state;
- changes no frontend quantum;
- changes no lower SND queue threshold;
- changes no scheduler timing;
- preserves Test A native-22050 transport;
- changes no mono/stereo policy.

## Builder

`tools/audio/build_testB_fba_367_368.py`

The builder requires exact Test-A input SHA:

`060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7`

It refuses any other lineage, verifies the original call word, verifies the selected executable padding, installs the one call-site patch plus 24-byte shim, reseals LCFG CRC32/MPEG-2, and audits that no bytes outside the call site, shim, and CRC field changed.

## Test question

Test B changes exactly one remaining semantic variable relative to HW-PASS Test A:

> Does correcting FBA's 22020-source-frame/s production to exactly 22050 source frames/s remove any remaining periodic roughness while preserving Test A's good synchronization and slowdown recovery?

No mono, scheduler, buffer-threshold, frontend-quantum, Mapper, Refresh, CLASSIC, or Audio OSD changes are part of Test B.
