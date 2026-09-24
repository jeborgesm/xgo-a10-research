# Test128 hardware result and MD-derived stop gate

Date: 2026-09-23
Status: **HW FAIL; pause GB hardware tests**

## Test128 observation

Fixture: Tetris GB import/art/meta retained from Test127.

Test128 executes only the GB materializer through the selective generic helper
runner; GB catalog execution is bypassed.

HW:
- Refresh Games -> Game Boy: **Refresh Failed**
- no top-level `.zgb` generated.

Therefore Test127's failure is already present at the materializer/runner boundary.
The GB catalog helper is not implicated by this hardware result.

## Mandatory MD lessons applied before any Test129

The MD Test76-106 record shows that this exact symptom class must not be debugged
by producing a sequence of speculative hardware variants.

1. Test81 returned clean Refresh Failed and explicitly required
   materializer-only isolation. Test128 has now completed that isolation for GB.
2. Test93-97 demonstrated that extension geometry must be solved from exact helper
   control flow. Test97's success came from one specific redundant-dot gate bypass,
   not from broad parser rewriting.
3. Test99-102 demonstrated that persistent state can confound later results and
   that byte-identical/reduced-delta candidates can fail for reasons unrelated to
   the proposed helper edit.
4. The generic runner has a pre-open heap guard. Refresh Failed does not prove the
   helper executed.
5. Test82 proved status instrumentation can itself create a total freeze; do not
   instrument UI/status paths.
6. Test103/104 proved apparently Refresh-only firmware changes can create NO BOOT.
   Prefer external-helper changes and preserve known-booting firmware.
7. Test105/106 proved the winning hardening pattern: keep the proven fixed-size
   external contract/firmware unchanged and move new logic behind a helper stage.
8. Storage/catalog state is first-class evidence. Do not infer helper behavior
   from status alone.

## Stop gate

No Test129 hardware candidate until offline analysis proves which of these two
conditions caused Test128:

A. generic runner rejected execution before `GB/refresh.xgc`; or
B. exact GB helper executed and returned -1.

If B, reconstruct the exact Test97 materializer extension/path parser for `.md`
and mechanically validate the proposed `.gb` substitution against instruction
semantics. Do not assume same filename-length geometry merely because both suffixes
contain two letters.

If A, reuse a HW-proven helper invocation lifecycle rather than patching the GB
materializer.

The next SD-card cycle must validate a closed cause, not narrow another guess.
