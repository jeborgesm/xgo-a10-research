# Test106 stale-recovery logical-gate hardware closure

Status: HW PASS.

Precondition was established by passive filesystem capture:
- .xgo-cat-state = exact ASCII "CLEAN!"
- stale complete coherent 788 recovery triplet physically present
- LIVE catalog = coherent known-good 839/839/839
- no new ROMs introduced

Hardware action:
- card returned unchanged
- Refresh invoked once

Observed:
- UI: "No new games"
- device remained responsive

## Hardware conclusion

This is the decisive discriminator between Test105 and Test106.

Under Test105, the physically present complete 788 backup triplet remained sufficient to trigger recovery again.

Under Test106, with the same stale 788 triplet physically present but CLEAN! established, the next invocation took the normal no-change path and remained responsive.

Therefore HW proves that the Test106 logical transaction-state gate successfully prevents stale complete backup files from causing repeated rollback/rebuild cycles.

## Test106 closure achieved

HW-proven:
1. known firmware boots unchanged;
2. missing-marker compatibility path handles the pre-existing stale Test105 recovery state;
3. recovery/rebuild returns "Games Updated";
4. immediate MD frontend consumption, artwork, launch, and gameplay remain healthy;
5. success finalization persists exact CLEAN!;
6. LIVE ends at coherent known-good 839 generation;
7. stale coherent 788 recovery triplet may remain physically present;
8. CLEAN! causes the next Refresh to ignore that stale triplet;
9. with no new games, second invocation returns "No new games";
10. device remains responsive.

Still OPEN:
- actual power-loss/media durability/fsync semantics;
- hardware proof of an interrupted ACTIVE transaction;
- rollback after a deliberately induced partial LIVE write.

Those should not be tested by intentionally power-cutting the SD card. The stale-recovery defect itself is closed.

Test106 can now be treated as the hardened MD refresh baseline for subsequent work.
