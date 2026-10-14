# XGO HK slot0 first-sample instruction-window audit — 2026-10-14

## Scope
Read-only extraction of original supplied `XGoAnalisis.zip/bios/bisrv.asd` and `struct.unpack_from('<I', image, offset)` at 0x35D804–0x35D894. This refines prior audits by distinguishing the **two distinct stream deadlines** and documenting precise intervening instructions. No UF2.

## BIN: first stream (B15, register s1)
- 0x35D844: `sw t6,0(s1)`, clears bit15 output-enable: releases stream 1.
- 0x35D848: `jal 0x2e0778`, delay slot at 0x35D84C.
- 0x35D850: `jal 0x2e0750`, delay slot at 0x35D854.
- 0x35D858–0x35D864: second stream release work (`lw`, `addiu`, `and`, `sw`).
- 0x35D868: `jal 0x2e0778`, delay slot at 0x35D86C.
- 0x35D870: `lw t2,0(s4)` samples stream1 DATA.
- 0x35D874: `andi t1,t2,0x8000` extracts stream1 bit15.

**Consequence:** stream1 first-sample window includes **three helper invocations** and second-stream release. Exact duration cannot be inferred from instruction count because helper execution varies.

## BIN: second stream (L0, register s0)
- 0x35D864: `sw t3,0(s0)` clears bit0 output-enable: releases stream2.
- 0x35D868: `jal 0x2e0778`, delay slot at 0x35D86C.
- 0x35D870–0x35D88C: first-stream sample and conditional update, with branch-dependent path.
- 0x35D890: `lw t9,0(s1)` samples stream2 DATA.
- 0x35D894: `andi s3,t9,1` extracts stream2 bit0.

**Consequence:** stream2 first-sample window contains **one helper call and a branch-dependent first-stream decode**. The two windows differ in both start time and work, and their relative real-time length is not established.

## Important correction
The early LOAD transition cannot be assumed to be a clean, long logic-high pulse. An open-drain host/responder bus turnaround requires host output-enable release, line rise, RP2040 RX detection, and responder output-enable sink before the appropriate host sample. Test23 and Test24 do not establish that this deadline is met. The first stream is not automatically the external handle port; physical connection remains OPEN.

## What this audit DOES NOT prove
- Which of the two streams the GP2040 is wired to.
- The elapsed microseconds of either window.
- That missed HK is solely slot0 setup timing, or that initial MP is a particular shifted bit.
- Any failure of the physical HK input; user reports GP2040 OLED correctly shows RB.

## Next objective gate
Find external-handle wiring evidence (stream B15 versus L0) or acquire DATA/CLOCK capture. Compare against disassembled RP2040 firmware. No additional speculative Test25 from this result alone. Test16 preserved.
