# XGO serial scanner CLOCK/DATA phase — binary audit 2026-10-12

**BIN source:** supplied XGoAnalisis.zip, bios/bisrv.asd; little-endian MIPS32 scanner at file offset 0x35D770. No firmware candidate or hardware test.

## Confirmed repeated-slot instruction order

- 0x35D8B0: lw GPIO register at s2 = 0xb8800354.
- 0x35D8B8–0x35D8BC: clear bit 7 (CLOCK low), sw.
- 0x35D8C8: jal 0x30fed0, delay-slot a0=2 (time delay helper).
- 0x35D8D0: jal 0x2e0750 (separate helper).
- 0x35D8D8–0x35D8E4: read GPIO register, set bit 7 (CLOCK high), sw.
- 0x35D8F0–0x35D8F4: read first DATA register at s4=0xb8800350; test bit 15.
- 0x35D908–0x35D90C: read second DATA register at s1=0xb8800050; test bit 0.
- Next slot at 0x35D928–0x35D960 repeats clear CLOCK, delay 2, set CLOCK high, then read.

**Finding:** XGO reads DATA **after** driving CLOCK high for the repeated slots. RP2040 updating DATA upon observing CLOCK low is phase-consistent; whether the actual update completes before XGO reads is OPEN.

## Helper identification
- 0x30fed0 saves registers, calls 0x49fc8 to read a time counter, computes elapsed time and loops until requested duration. Delay helper is confirmed structurally; effective duration unit and overhead still OPEN.
- 0x2e0750 calls 0x49da4 then increments a gp-relative counter. This is **not** the 2-unit delay routine.
- 0x2e0778 decrements the same gp-relative counter and conditionally calls 0x49df4 when count reaches zero. Their exact purpose is OPEN (likely resource/critical-section nesting; do not claim).
- Slot0 has different startup sequence including delay argument 4 at 0x35D824, followed by GPIO transitions and reads at 0x35D870 and 0x35D890; requires separate deadline analysis.

## Consequence
Prior speculation that XGO samples *early during CLOCK low* is contradicted by these instructions for repeated slots. The unresolved hazard is RP2040 detection/response latency relative to the host low-duration + subsequent high/read sequence, or incorrect LOAD/slot alignment and/or mapping.

Next: determine counter units in 0x30fed0/0x49fc8 and verify pin register semantics, inspect slot0 initialization, compiled RP2040 critical-path cycles, then one-hot mapping test. Protected Test14 unchanged.
