# Test127 hardware result — GB Refresh Failed

Date: 2026-09-23
Status: **HW FAIL — do not promote**

Hardware fixture:
- user added Tetris as a new GB import;
- matching required folders/files for the enrichment workflow were present;
- Test127 installed;
- Refresh Games -> Game Boy invoked.

Observed:
- UI returned **Refresh Failed**.

This disproves Test127 as a usable GB candidate. No claim is made yet whether
failure originated in GB/refresh.xgc, GB/catalog.xgc, or the generic helper runner.

## Immediate diagnostic consequence

Test127 uses the Test97/Test75 generic helper runner at `0x80A382E0`. Preserved
repository evidence already documents a pre-helper guard:

```
if *(0x80C237B0) > 0x86FFFFFF:
    return -1
```

The runner can therefore emit the same Refresh Failed status **before the helper
is opened/executed**. This was previously observed as a lifecycle/heap concern in
the selective-helper lineage.

Accordingly, do not modify GB parsing, artwork, catalog strings, or wrapper code
until the failing stage is isolated.

## Next candidate requirement

Instrument the command-3 sequence so materializer and catalog failures have
separate observable status/result codes, or remove the generic-runner ambiguity
by reusing the already-proven invocation lifecycle from the closest successful
enrichment parent. The next hardware test must distinguish:

1. runner/materializer failure before wrapper creation;
2. materializer success + catalog runner/helper failure;
3. catalog success/status-path failure.

No blind GB helper changes are authorized from this result.
