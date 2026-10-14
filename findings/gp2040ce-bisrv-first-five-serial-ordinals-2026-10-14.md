# Original scanner per-slot evidence, first five samples (2026-10-14)

Direct extraction from user-supplied `XGoAnalisis.zip` -> `bios/bisrv.asd`, little-endian MIPS32 instructions, file offset = virtual address - 0x80000000 for this code range. No firmware modifications.

## First B15 and L0 sample groups

| Serial sample ordinal (starting 0) | B15 read and mask | L0 read and mask | output bit set when pressed |
|---|---|---|---|
| 0 | 8035d870 `lw t2,0(s4)`, 8035d874 `andi t1,t2,0x8000` | 8035d890 `lw t9,0(s1)`, 8035d894 `andi s3,t9,1` | 0x1000 (8035d888/8035d8a4) |
| 1 | 8035d8f0 `lw v0,0(s4)`, 8035d8f4 `andi a1,v0,0x8000` | 8035d908 `lw t5,0(s1)`, 8035d90c `andi t4,t5,1` | 0x2000 (8035d904/8035d91c) |
| 2 | 8035d968 `lw s3,0(s4)`, 8035d96c `andi t8,s3,0x8000` | 8035d980 `lw t0,0(s1)`, 8035d984 `andi a3,t0,1` | 0x4000 (8035d97c/8035d994) |
| 3 | 8035d9e0 `lw t4,0(s4)`, 8035d9e4 `andi t3,t4,0x8000` | 8035d9f8 `lw a1,0(s1)`, 8035d9fc `andi s0,a1,1` | 0x0800 (8035d9f4/8035da0c) |
| 4 | 8035da58 `lw a3,0(s4)`, 8035da5c `andi a0,a3,0x8000` | 8035da70 `lw t8,0(s1)`, 8035da74 `andi t7,t8,1` | 0x0080 (8035da6c/8035da84, latter beyond original focused printout; verify) |

This demonstrates B15 and L0 sampled as **parallel ordinal positions** and each accumulates bits into separate GP-relative words (`gp-0x0d2c` and `gp-0x0d28` via `0xf2d4` and `0xf2d8`). The *destination output bit masks are not monotonic serial position indexes*; they are a firmware mapping of physical scan ordinal to internal button state. Thus comparing SFII HP and MK by attack labels alone is invalid.

## CLOCK transition and timing

Between sample 0 and 1 the code changes GPIO using s2: `8035d8b0 lw t1,0(s2)`, `8035d8b4 addiu s0,zero,-129`, `8035d8bc sw t0,0(s2)`; then calls `0x802e0778`, `0x8030fed0` with argument 2, `0x802e0750`, followed by `8035d8d8 lw a3,0(s2)`, `8035d8e4 sw a2,0(s2)`, and `0x802e0778` before the next sample at 8035d8f0. Repeats at ~0x78-byte spacing. Exact edge polarity depends on s2 address and surrounding register values; helper 0x8030fed0 requires classification. Delay slots must be accounted for; don't claim a measured sample window from static code.

## Engineering implication

The XGO maps each physical serial ordinal to internal flags; serial timing and game-facing attack mapping are distinct. Need to trace those flags through emulator mapping before attributing HP→MK to an adjacent slot. Test28 remains protected; Test29 slowed repeats but did not fix mixing. No Test30 candidate yet.
