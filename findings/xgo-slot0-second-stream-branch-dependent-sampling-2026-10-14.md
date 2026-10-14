# XGO slot0 second-stream sampling is branch-dependent — 2026-10-14

## Direct BIN verification
Original supplied `XGoAnalisis.zip`, `bios/bisrv.asd` extracted read-only; little-endian MIPS32 instruction words at file offsets 0x35D870–0x35D894.

```
0x35D870  0x8e8a0000  lw    t2,0(s4)         ; first DATA stream input
0x35D874  0x31498000  andi  t1,t2,0x8000    ; first stream bit15
0x35D878  0x15200005  bne   t1,zero,+5      ; target 0x35D890
0x35D87C  0x36710050  ori   s1,s3,0x0050   ; branch delay slot, always executes
0x35D880  0x8f91f2d4  lw    s1,-3372(gp)   ; only on not-taken path
0x35D884  0x36301000  ori   s0,s1,0x1000   ; only on not-taken path
0x35D888  0xaf90f2d4  sw    s0,-3372(gp)   ; only on not-taken path
0x35D88C  0x36710050  ori   s1,s3,0x0050   ; only on not-taken path
0x35D890  0x8e390000  lw    t9,0(s1)       ; second DATA stream input
0x35D894  0x33330001  andi  s3,t9,1        ; second stream bit0
```

## BIN conclusion
First stream bit15 decides whether four instructions execute before second stream slot0 read. The second stream's release at 0x35D864 occurs before the branch. Thus second stream's LOAD-release-to-sample instruction path depends on the first stream's sampled bit. This is **not** a claim that the four instructions add a known number of microseconds: cache, memory and pipeline timing remain open.

## Interpretation
If the RP2040 is wired to second stream, the other stream's input state changes its first-bit setup window. If wired to first stream, this branch occurs *after* its sample and cannot directly change that sample deadline. This conditional dependency may help identify physical stream with targeted observation, but it is not by itself proof of HK failure.

## Outstanding
Physical DATA stream identity; timing capture; RP2040 compiled latency; initial MP substitution; held-repeat cause.

## Safety
Test16 remains protected. No new firmware or hardware request from this finding.
