# Test105 cleanup defect root-cause direction

Status: BIN/HW reconciliation. Do not run another Refresh on the current card while the stale 788 recovery triplet remains.

## Observation to explain

Hardware/filesystem state after deterministic recovery:
- LIVE catalog = coherent healthy 839 generation.
- complete recovery triplet = still the original coherent 788 fixture.
- frontend/artwork/gameplay = healthy.

Therefore recovery/rebuild succeeded but successful cleanup did not remove the sentinel.

## Most important discriminator

The backup files are not merely present; they are byte-identical to the originally injected 788 fixture.

That rules out a large class of theories:
- they were not overwritten with the newly current 839 generation;
- backup_old did not successfully replace the sentinel with a new backup generation before the final state;
- cleanup did not successfully remove them.

The next patch must not alter recovery/commit behavior that already produced a healthy 839 live triplet.

## Narrow repair strategy

Preserve:
- Test97 bisrv.asd byte-identical;
- Test105 Stage1 byte-identical;
- Stage2 base 0x87180000;
- Stage2 size 7000 if possible;
- recovery restore/validation;
- catalog rebuild/verification;
- stock status return behavior.

Change only the successful finalization path so that, after the final live triplet has been verified, the three recovery paths are removed explicitly and unconditionally before returning success.

The remove operation must use the already BIN-established remove-like service 0x807D40A8 and exact paths:
- /mnt/sda1/MD/art/.xgo-cat-tax.bak
- /mnt/sda1/MD/art/.xgo-cat-nec.bak
- /mnt/sda1/MD/art/.xgo-cat-bvs.bak

Do not use guessed rename/link semantics.

## Safety ordering

The cleanup must remain AFTER successful live verification.

Never delete recovery before:
1. all three LIVE members are written;
2. all three LIVE members are reopened/read;
3. byte comparison against expected NEW succeeds.

Then:
    remove tax backup
    remove nec backup
    remove bvs backup
    invalidate MD count cache
    return success

If cleanup itself fails, retaining a stale complete backup is safer than deleting only part before live verification, but repeated rollback/rebuild is undesirable. The repair should therefore make the three explicit calls on the proven success path and preserve live data regardless of remove return value.

## Test106 scope

If a corrected artifact is needed, Test106 should be Stage2-only relative to Test105:
- MD/catalog-safe.xgc changed
- MD/catalog.xgc unchanged SHA 135dae8bf00962db365afe1cffd6c2f36b0780033d11e89f4694925f05276a80
- bios/bisrv.asd unchanged SHA b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e

The current stale recovery files should be left in place for the eventual Test106 proof. That gives the corrected Stage2 an immediate deterministic cleanup case without manufacturing another fixture.

No hardware action yet.
