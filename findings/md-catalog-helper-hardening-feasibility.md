# MD catalog helper hardening feasibility audit

Status: BIN / DESIGN. No hardware candidate.

Target analyzed:
MD/catalog.xgc from Test97
size 2642 bytes
SHA-256 2604672d00ec25f49a96e05214b1a3421b35717d04098800309bd08b26077645

## Existing helper already has strong pre-write validation

The helper reads the complete live triplet before it modifies anything:

    /mnt/sda1/Resources/scksp.tax -> 0x87200000
    /mnt/sda1/Resources/setxa.nec -> 0x87210000
    /mnt/sda1/Resources/wmiui.bvs -> 0x87220000

Each fread is bounded to 0x10000 bytes.

It then validates, before scanning /MD or opening any live catalog with "wb":

1. each read succeeded with a plausible size;
2. each catalog count <= 4096;
3. each catalog's offset-table geometry fits inside the bytes actually read;
4. TAX count == NEC count;
5. TAX count == BVS count.

Therefore the current helper ALREADY refuses to proceed from the observed 839/839/788 mixed generation.

This is important: corrupt-start protection is not absent. The missing safeguard is preservation/recovery around the destructive output phase.

## Existing output phase

After rebuilding candidate buffers, helper writes:

    0x87240000 -> scksp.tax
    0x87260000 -> setxa.nec
    0x87280000 -> wmiui.bvs

using fopen("wb"), fwrite, fclose and exact write-count checks.

Only after all three writes succeed does it clear MD count cache 0x80D2895C.

Failure at any write returns -1, but earlier live members may already have been replaced. That is the transaction hole.

## Useful consequence

Because the old coherent triplet is already fully resident in RAM at:

    OLD TAX  0x87200000
    OLD NEC  0x87210000
    OLD BVS  0x87220000

and the rebuilt generation is separate at:

    NEW TAX  0x87240000
    NEW NEC  0x87260000
    NEW BVS  0x87280000

a backup phase does NOT require another large RAM allocation.

The helper can write the already-validated OLD buffers to recovery files before touching the live files.

Conceptually:

    read LIVE -> OLD buffers
             |
             v
       validate OLD
             |
             v
       build NEW separately
             |
             v
    OLD buffers -> RECOVERY
             |
             v
       verify recovery
             |
             v
    NEW buffers -> LIVE

This fits the existing memory architecture unusually well.

## Size ceiling

Each input member is currently read with fread(..., 1, 0x10000, ...).

Thus the helper's present hard ceiling is 65,536 bytes per individual catalog member.

Current MD 839 sizes:
- TAX 23,458
- NEC 17,082
- BVS 9,258

There is substantial room before the existing helper's per-member ceiling.

Do not enlarge the catalog limits as part of hardening. Keep scope surgical.

## Recovery filename placement

Do NOT put speculative backup triplets directly into /Resources until native resource discovery behavior is proven safe. Test91 demonstrated that guessed Resources assets can have unintended frontend effects.

Safer design direction: keep recovery artifacts outside /Resources, under an already-existing MD-owned directory that native catalog discovery does not consume.

Candidate DESIGN namespace:

    /mnt/sda1/MD/art/.xgo-cat-tax
    /mnt/sda1/MD/art/.xgo-cat-nec
    /mnt/sda1/MD/art/.xgo-cat-bvs

Why this is preferable:
- /MD/art already exists in the proven Test97 enrichment layout;
- stock Resources discovery cannot mistake these for catalog members;
- /MD root wrapper enumeration is avoided;
- names do not collide with the known .xgo.jpg/.xgo.rgb565 temporary artwork files.

This placement is NOT yet HW-proven. Before implementation, verify statically that artwork cleanup targets only its exact temp filenames and does not purge arbitrary .xgo-* files.

## Backup verification options

Writing the backup is insufficient; it must be re-opened and checked.

Minimum verification without new hashing code:

    write OLD TAX backup
    write OLD NEC backup
    write OLD BVS backup

    reopen each backup
    read into available scratch/new buffer after NEW can be regenerated,
    or compare file byte count plus structural triplet validation.

Preferred: backup before NEW construction if code organization permits, then use NEW buffers as temporary verification buffers and subsequently rebuild NEW.

Alternative: build NEW first, write backup from OLD, then verify backup one file at a time using an otherwise-safe scratch region. Do not overwrite OLD until commit is complete because OLD is the rollback source.

The exact scratch choice remains OPEN.

## Restore path

A restore after a failed live write can use the OLD buffers still resident in RAM during the same invocation:

    failed commit
         |
         v
    OLD TAX -> live TAX
    OLD NEC -> live NEC
    OLD BVS -> live BVS
         |
         v
    reopen/validate live

For recovery on a later invocation/reboot, the recovery files must be loaded and validated before restoration.

This implies two distinct safeguards:

A. same-run rollback: easy, because OLD is already resident.
B. next-run recovery: requires persistent recovery-file detection/loading.

Implement A before B only if doing so does not create false confidence; the historical failure involved forced shutdown, so B is required before declaring interruption hardening complete.

## Helper-size constraint

Test97 firmware invokes MD/catalog.xgc through the generic helper runner with an explicit helper size of 2642 bytes.

The current helper ends its code near 0x9E4 and immediately stores path strings through the 0xA4x region. There is effectively no comfortable unused code cavity for a complete backup/recovery state machine.

Therefore robust hardening will probably require:
- a larger catalog.xgc payload; and
- changing the selective dispatcher size constant for MD/catalog.xgc.

That is a materially larger change than patching a few existing instructions and must be audited offline before hardware.

Do not attempt to squeeze recovery logic into arbitrary padding or overwrite strings.

## Next offline closure

Before Test104:
1. prove /MD/art cleanup is exact-name only and safe for persistent recovery files;
2. map a safe scratch-buffer strategy for re-reading backups;
3. design helper expansion and update the explicit 2642-byte runner size;
4. simulate power-loss boundaries after each backup/live member write;
5. require every simulated restart to converge either to old coherent generation or new coherent generation.

Only then build a hardware candidate.
