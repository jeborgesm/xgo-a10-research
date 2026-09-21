# Test106 logical transaction marker — offline construction

Status: OFFLINE CONSTRUCTED / NOT YET HW-PROMOTED.

## Why Test105 cleanup failed

Test105 does execute the three intended remove calls after successful LIVE verification. Static disassembly confirms exact paths and three calls to 0x807D40A8. Hardware/filesystem capture nevertheless shows all three 788 recovery files survive unchanged.

Therefore deletion cannot be used as the sole transaction-state signal on this path.

The repair does not weaken the proven restore/commit machinery. Instead it makes recovery state explicit and write-based.

## Test106 protocol

New persistent state file:

    /mnt/sda1/MD/art/.xgo-cat-state

Exact 6-byte states:

    ACTIVE
    CLEAN!

Rules:

1. Marker absent / invalid / ACTIVE:
   run existing Test105 recovery preflight.
   This preserves compatibility with the current card, which has the stale 788 triplet and no marker.

2. CLEAN!:
   stale backup files are ignored by recovery preflight.

3. Before destructive LIVE commit:
   existing backup_old must first succeed and byte-verify;
   then write ACTIVE with fopen wb / fwrite exact 6 / fclose;
   if that write fails or is short, abort before LIVE writes.

4. After Stage2 returns nonnegative success/no-change:
   write CLEAN! with fopen wb / fwrite exact 6 / fclose.

The old three remove calls remain in Stage2 as best-effort housekeeping, but correctness no longer depends on them.

## Power/interruption ordering

CLEAN + old backups + no transaction:
    backups ignored.

Backup verified, before ACTIVE:
    LIVE untouched; interruption is safe.

ACTIVE written, then LIVE commit begins:
    interruption leaves marker non-CLEAN/ACTIVE; next invocation executes recovery.

LIVE verified, CLEAN write interrupted:
    marker is conservatively non-CLEAN in the normal torn/truncated case; recovery may repeat, but safety is preserved.

Physical-media fsync/durability remains OPEN, as before.

## Implementation placement

The 2642-byte Stage1 had over 2 KB inert padding. Test106 uses that already-loaded executable space for the marker helpers without increasing the file size.

Stage1 remains exactly 2642 bytes.

Stage2 remains exactly 7000 bytes.

Stage2 changes only two call targets:
- entry recovery call -> Stage1 recovery_gate
- backup hook backup_old call -> Stage1 backup_and_activate

The original hardened recovery, rollback, commit, verify, and cleanup bodies otherwise remain byte-identical.

Stage1 main finalization writes CLEAN! for any nonnegative Stage2 return and preserves the original Stage2 return value.

## Hashes

Test106 Stage1 MD/catalog.xgc:
    size 2642
    SHA-256 3849d126badd649b89be606bec00a3ff1d4525221a1a5b955a6c9d99c559243e

Test106 Stage2 MD/catalog-safe.xgc:
    size 7000
    SHA-256 45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

Firmware remains exact known-booting Test97:
    SHA-256 b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e

Offline ZIP:
    SHA-256 6030dcfdb56efac06f819a0c919bd1028a5aaf307f406a35dad6eda45f0015e2

Complete package comparison vs Test105:
- changed MD/catalog.xgc
- changed MD/catalog-safe.xgc
- added none
- removed none
- all other files byte-identical.

## Current-card advantage

Do not delete the current stale 788 backup triplet. It is the ideal compatibility proof:
- marker absent => Test106 must recover once;
- successful completion => CLEAN! created;
- stale backup triplet may remain physically present but becomes logically inactive;
- next Refresh should take the CLEAN path and avoid another 788 rollback/rebuild.

Final mechanical branch/stack audit is still required before hardware promotion.
