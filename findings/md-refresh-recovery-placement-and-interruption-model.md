# MD Refresh hardening: recovery placement and interruption model closure

Status: BIN + DESIGN + MODEL. No hardware candidate.

## /MD/art recovery placement audit

Test97 MD/refresh.xgc contains only these artwork/temp path contracts:

    /mnt/sda1/MD/art/.xgo.jpg
    /mnt/sda1/MD/art/.xgo.rgb565
    /mnt/sda1/MD/art/%s.jpg
    /mnt/sda1/MD/art/%s.jpeg

The cleanup calls previously traced through 0x807D40A8 use the two exact temporary path literals:

    /mnt/sda1/MD/art/.xgo.jpg
    /mnt/sda1/MD/art/.xgo.rgb565

There is no wildcard path string and no generic /MD/art directory cleanup contract in the Test97 materializer.

BIN conclusion: persistent recovery files with distinct names and non-image extensions in /MD/art will not collide with the known exact-name temporary cleanup or the per-game .jpg/.jpeg artwork lookup.

This is sufficient for an implementation candidate, while HW behavior remains unproven.

Proposed names:

    /mnt/sda1/MD/art/.xgo-cat-tax.bak
    /mnt/sda1/MD/art/.xgo-cat-nec.bak
    /mnt/sda1/MD/art/.xgo-cat-bvs.bak

Do not place recovery triplets in /Resources.

## Important validation refinement

Count equality alone is sufficient to reject the observed 839/839/788 incident, but it is not a cryptographic/generation identity check.

For backup creation during a healthy run, stronger verification is available without hashes:

    source OLD member already in RAM
          |
          v
    write recovery member
          |
          v
    reopen recovery member
          |
          v
    compare exact byte length
          |
          v
    compare every byte against OLD source

A backup set is eligible for commit only after all three members pass byte-for-byte verification.

For later-run recovery, no original RAM copy exists. The persistent recovery set can still be structurally validated as a coherent TAX/NEC/BVS triplet before restoration.

## Logical interruption simulation

The protocol was modeled at every file-write boundary.

Legend:
O = old coherent generation
N = new generation
P = previous stale recovery generation

    interruption point      LIVE       RECOVERY     restart decision

    before backup           O/O/O      P/P/P        keep LIVE
    after backup TAX        O/O/O      O/P/P        keep LIVE
    after backup NEC        O/O/O      O/O/P        keep LIVE
    after backup BVS        O/O/O      O/O/O        keep LIVE

    after live TAX          N/O/O      O/O/O        restore RECOVERY
    after live NEC          N/N/O      O/O/O        restore RECOVERY
    after live BVS          N/N/N      O/O/O        keep LIVE

At every modeled logical interruption boundary the restart rule converges to a coherent generation.

Restart rule:

    validate LIVE
         |
      +--+--+
      |     |
    valid invalid
      |     |
      v     v
    use   validate RECOVERY
    LIVE      |
           +--+--+
           |     |
         valid invalid
           |     |
           v     v
       restore  FAIL
       recovery safely

## Why interrupted backup creation is safe

Backup files are created BEFORE any live member is touched.

If power fails while replacing the backup set, LIVE remains O/O/O and therefore wins on the next invocation. A mixed backup set is ignored.

Only after all three backup files have been written and verified does the helper enter the destructive live-commit phase.

Thus the logical ordering creates a useful invariant:

    incoherent LIVE
        implies
    commit phase had begun
        implies
    complete verified RECOVERY existed beforehand

This is a program-order invariant, not yet a physical-media durability guarantee.

## Remaining durability caveat

fclose reaches the filesystem backend, but no fsync/flush primitive has been proven.

Therefore physical FAT/SD write reordering remains OPEN.

The model proves logical crash recovery, not guaranteed persistence under arbitrary controller/media behavior.

Do not claim power-fail atomicity.

## Same-run rollback

During the same helper invocation, OLD remains resident:

    OLD TAX  0x87200000
    OLD NEC  0x87210000
    OLD BVS  0x87220000

If any live fwrite/fclose/count check fails, restore all three live files from OLD RAM immediately, then re-open and validate.

Persistent recovery files handle the separate reboot/interruption case.

## Scratch-buffer strategy

The helper already owns six 64-KiB-spaced catalog regions:

    OLD  0x87200000 / 0x87210000 / 0x87220000
    NEW  0x87240000 / 0x87260000 / 0x87280000

The gap at 0x87230000 is a natural candidate scratch region, but ownership has NOT been proven.

Do not use 0x87230000 merely because it appears geometrically free.

Safer implementation options, in order:
1. locate a proven helper-owned scratch/workspace region;
2. verify backups one member at a time before NEW buffers are populated, temporarily using a NEW buffer;
3. restructure sequence so recovery backup + verification happens immediately after OLD validation, before NEW construction.

Option 2/3 avoids inventing a seventh memory region and is currently preferred.

Recommended sequence:

    read OLD
       |
    validate OLD
       |
    write backup TAX -> reread into NEW TAX -> byte compare
    write backup NEC -> reread into NEW NEC -> byte compare
    write backup BVS -> reread into NEW BVS -> byte compare
       |
    backup verified
       |
    rebuild NEW buffers normally
       |
    commit NEW -> LIVE
       |
    reopen/validate LIVE
       |
    success

This reuses memory already owned by the helper and does not increase RAM footprint.

## Next closure before Test104

The remaining implementation-level work is now:
- reconstruct enough of catalog.xgc control flow to insert backup/verify/recovery without disturbing the proven rebuild logic;
- determine the enlarged helper size and corresponding dispatcher size constant;
- add startup detection of incoherent LIVE + coherent recovery;
- ensure successful live validation occurs before cache invalidation;
- build an offline test harness for valid, mixed, truncated, and malformed triplets.

No SD-card test is justified yet.
