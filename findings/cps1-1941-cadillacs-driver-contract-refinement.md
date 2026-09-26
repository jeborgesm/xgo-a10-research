# CPS1 1941 versus Cadillacs driver-contract refinement

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Evidence: BIN / OPEN
Hardware candidate: NOT AUTHORIZED

## New BIN refinement

Exact XGO bios/bisrv.asd contains adjacent CPS1 driver-name strings for both comparison families.

Cadillacs family strings include:
dinohb, dino, dinoha, dinoh, dinopic2, dinopic, dinou, dinoj

1941 family strings include:
1941j, 1941

The known-good stock wrapper contract already maps:
Cadillacs and Dinosaurs.zfb -> dino.zip

The generated Test04 wrapper maps:
1941.zfb -> 1941.zip

Therefore the generated archive basename 1941.zip agrees with an actual stock-XGO internal driver identifier, just as dino.zip agrees with the working Cadillacs identifier.

This removes one candidate divergence: there is no BIN evidence that the generated wrapper chose the wrong driver/archive basename.

## Descriptor-table comparison

Both drivers use the same XGO stock-FBA descriptor architecture:
- fixed-size member-name field;
- size;
- checksum;
- type/region flags;
- FBA-era member aliases rather than modern external filenames.

Cadillacs World begins with cde_23a.rom / cde_22a.rom / cde_21a.rom and continues through cd_gfx*, cd_q and cd_q1..q4.

1941 World uses 41e_30.rom / 41e_35.rom / 41e_31.rom / 41e_36.rom / 41_32.rom, 41_gfx*, 41_09.rom and 41_18/19.rom.

The 1941 descriptor format is therefore normal for the same stock FBA runtime that successfully launches Cadillacs.

## Consequence

The first demonstrated divergence has NOT yet been found in:
- outer archive basename / driver identifier;
- descriptor-table architecture;
- basic CPS1 family/runtime identity.

The exact Test04 1941.zip payload remains the strongest unresolved offline discriminator because it can be compared directly to the now-closed XGO descriptor contract.

## Artifact search

A search of the companion xgo-a10-artifacts repository found older unrelated Game-List Test04 records, but no preserved CPS1 Test04 1941.zip or 1941.zfb by content search.

The local XGoAnalisis extraction likewise contains no 1941.zip or 1941.zfb.

Do not confuse historical test-number collisions with the current CPS1 Test04 checkpoint.

## OPEN

1. Exact Test04 1941.zip member names/sizes/checksums.
2. Whether the stock loader resolves members strictly by filename or has checksum/name normalization.
3. Any index-dependent CPS1 launch state after catalog selection.
4. Live-list/cache invalidation after mutation.
5. First runtime divergence after stock preprocessing.

## Next offline task

Trace the stock FBA archive-member lookup behavior in XGO BIN around the ROM descriptor consumption path. Determine whether member lookup is name-strict, checksum-assisted, or normalized. This tells us whether modern-named but checksum-identical 1941 content would fail before we ever need the exact Test04 archive.

No Test05 authorized.
