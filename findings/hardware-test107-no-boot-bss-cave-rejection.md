# Test107 NO BOOT — root cause: misclassified BSS, not executable cave

Date: 2026-09-21
Hardware result: **NO BOOT**

## Immediate conclusion

Do not use Test107. Restore the protected Test106 baseline.

The failure exposes a critical classification error in the prior cave audit.

## Root cause

The range beginning at 0x80A389B8 is zero in the firmware file, but exact Test106 references prove that at least:
- 0x80A389C0 = selector_active
- 0x80A389C4 = selected command

are live writable runtime state.

That means the zero run is not evidence of spare executable ROM/code capacity. It is a **BSS/runtime-state region**.

Test107 placed executable instructions beginning at 0x80A389C8. The frontend hooks then jumped into that region. If startup/runtime initialization clears or owns this BSS range—as the live C0/C4 state already strongly indicates—the injected instructions are not a valid persistent executable target. A jump into zeroed/non-code memory explains the immediate NO BOOT without requiring any catalog or SD activity.

This interpretation also fits the historical pattern: Test85/Test97 code/data ends before the zero-state area; previous attempts that expanded inferred code/resource ownership beyond proven regions produced NO BOOT or frontend corruption.

## Evidence correction

Previous findings that called 0x80A389B8..0x80A391F8 a "safe executable cave" are superseded.

Correct classification:
- static file bytes: zero;
- runtime ownership: at least partially BSS/state;
- executable suitability: **REJECTED by Test107 HW NO BOOT**.

A zero-run hash across firmware versions proves byte stability only. It does **not** prove executable allocation safety.

## Next architecture

Do not search for another zero run.

Reuse only regions already proven executable in hardware:
1. Test85/Test106 obsolete diagnostic selector code around 0x80A385F0..0x80A388xx;
2. inherited diagnostic overlay code at 0x807DB9D4..0x807DBBxx.

These are ideal replacement surfaces because the final selector is deliberately deleting the functionality they currently implement.

Split the replacement:
- selector/navigation/confirm trampolines -> reclaim obsolete 0x80A385F0.. dispatcher code;
- eight-row renderer -> replace obsolete 0x807DB9D4 diagnostic renderer in place;
- retain 0x80A389C0/C4 as writable state if useful;
- do not expand executable code into the BSS zero run.

## Test107 evidence boundary

- Test107 NO BOOT: **HW**
- C0/C4 runtime state ownership: **BIN**
- zero run is not safe executable cave: **HW + BIN**
- startup zeroing exact extent: **INF**, not yet directly traced
- reclaiming already-executable diagnostic regions: **DESIGN grounded in prior HW executable provenance**

No Test108 should be emitted until the replacement fits entirely inside already-proven executable regions and a byte-diff audit confirms no expansion into BSS.
