# GB Test128 root-cause review against MD Test76-106

Date: 2026-09-23
Status: **OFFLINE CAUSE NARROWED; no hardware candidate**

## Result

Test128 proves only that the command-3 materializer invocation returned through
the common failure path and created no `.zgb`.

A full review of the MD lineage changes the priority of the two hypotheses.

### The generic-runner guard is not sufficient as the primary explanation

The generic runner's `0x80C237B0 <= 0x86FFFFFF` precondition remains real.
However, Test128 invokes GB as the first/only helper for command 3. The MD record
associated guard exhaustion with repeated standalone helper invocations in one
session (FC/SFC followed by MD). There is currently no evidence that a fresh
single command-3 invocation starts above the guard.

Therefore hypothesis A (runner rejected before helper execution) remains OPEN,
but it is not justified as the leading cause solely from the guard's existence.

### The stronger MD analogue is Test96

MD chronology:

```
Test93 exact-ish materializer isolation -> No New Games
Test94/95 gate edits                -> No New Games
Test96 broad gate bypass            -> Refresh Failed
Test97 exact redundant-dot bypass   -> Games Updated
```

This proves that `Refresh Failed` from a materializer-only run can be a parser/
path-contract failure reached after passing earlier filters.

Test128's symptom therefore requires instruction-level validation of the GB
derivative before another runner/lifecycle patch.

## Re-audit target

The current GB helper was produced by changing Test97 MD at:
- wrapper suffix constant;
- source extension compare chars;
- path strings.

That derivation was mechanically bounded, but bounded does not mean semantically
correct. Reconstruct these exact operations from disassembly:
1. length computation and all L-N loads around offsets 0x024C..0x02D8;
2. branch delay slots and the preserved NOP at 0x027C;
3. source filename after any uppercase/classifier mutation;
4. wrapper suffix construction around 0x0114;
5. input/output/meta/art sprintf arguments;
6. every fatal-return branch reachable after extension acceptance and before
   wrapper creation.

Compare exact Test97 MD and GB values at each point. A new candidate is forbidden
until every changed byte has a demonstrated runtime meaning.

## Experimental-state discipline inherited from MD

Before the next hardware test, define the expected starting filesystem state.
Tetris source/art/meta and absence/presence of generated wrapper/catalog entry
must be explicit. Do not delete/regenerate wrappers or catalogs between tests
without recording it; Tests99-102 proved this can invalidate comparisons.

## Firmware discipline

Do not patch Test123/Test127 firmware to diagnose this unless external-helper
analysis cannot close the cause. Tests103/104 and later CRC work show firmware
changes are a separate risk axis.

The preferred next candidate, if helper analysis finds the cause, keeps the exact
known-booting Test128/Test123 invocation structure and changes only
`GB/refresh.xgc`.
