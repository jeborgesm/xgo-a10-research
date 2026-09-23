# Test127 GB execution-island audit against protected FC/SFC/MD bodies

Date: 2026-09-23
Status: **BIN — execution grammar matches; fault moves below dispatcher**

Exact Test127 firmware was disassembled at the three protected selective helper
bodies and at the new GB body.

## Protected body grammar

FC/SFC/MD each execute:

```
lui/addiu a0, refresh_path
li a1, 0x101F08
jal 0x80A382E0
nop
li t0,0
slt t1,v0,t0
bne t1,zero, common_fail
nop
or s0,s0,v0

lui/addiu a0, catalog_path
li a1,0x0A52
jal 0x80A382E0
nop
li t0,0
slt t1,v0,t0
bne t1,zero, common_fail
nop
or s0,s0,v0
j common_done
nop
```

The Test127 GB island at `0x80A39050` is instruction-for-instruction the same
grammar, with only its own path pointers and branch displacements changed.

Therefore the previously suspected stack/change-accumulation/return-grammar
difference is not present.

## Consequence

Test128's materializer-only failure is now below the GB dispatcher body:
- generic runner pre-open/precondition, OR
- GB helper execution.

Do not rebuild the same command-3 island again.

## Protected-path rule retained

FC/SFC/MD/CLASSIC remain protected and must not be replaced by diagnostic helpers.
Test129 remains rejected.

## Next offline discriminator

Use a GB-local helper that is exactly 0x101F08 bytes and returns a constant result
without filesystem work. It must be placed only at `/GB/refresh.xgc`, reached by
the existing Test128 command-3 path.

This does not modify any working subsystem and isolates the generic runner:
- normal return => runner/lifecycle can load and execute a GB-owned helper; defect
  is inside the GB materializer;
- Refresh Failed => failure occurs before/around helper execution and the
  materializer must not be changed.

Because the helper path and requested size are identical to Test128, this test
isolates code content while preserving loader geometry.
