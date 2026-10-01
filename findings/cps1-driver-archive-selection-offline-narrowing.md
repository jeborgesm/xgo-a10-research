# CPS1 driver/archive selection path — offline narrowing

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Status: SRC/UP with matching XGO BIN lineage; no hardware candidate authorized.

## Closed loader behavior

The historical libretro FBA loader family corresponding to XGO performs archive discovery from the already-selected Burn driver:

1. nBurnDrvActive is set to the selected driver.
2. open_archive() asks BurnDrvGetZipName() for up to 32 archive names associated with that driver.
3. each returned archive name is resolved relative to g_rom_dir;
4. all found archives are parsed;
5. required ROMs are mapped CRC-first, then by filename fallback;
6. unresolved non-optional ROMs abort initialization.

This means archive-member matching does not select the game driver. Driver selection occurs before open_archive().

XGO BIN preserves the same later-loader diagnostics and repository archaeology already ties the stock wrapper to FB Alpha v0.2.97.42 / 621e371 loader lineage.

## Implication for Test04

For 1941, the generated wrapper trailer is 1941.zip and XGO BIN contains internal driver identifier 1941.

For known-good Cadillacs, stock wrapper trailer is dino.zip and XGO BIN contains driver identifier dino.

Thus the two paths are structurally symmetric at the wrapper-basename/driver-name boundary.

The stock loader may additionally request parent/related archives via BurnDrvGetZipName(), but that list is a consequence of the selected driver, not a substitute driver-selection mechanism.

Because 1941 is itself the World parent identity in the compiled XGO driver family (with 1941j as a related clone identity), the generated 1941.zip basename is consistent with selecting the parent World driver.

## What is now weak

The following explanations are now weak or eliminated absent contrary BIN evidence:
- wrong outer archive basename;
- modern internal member names alone;
- anomalous 1941 descriptor format;
- 1941 driver absent from stock XGO.

## Remaining high-value OPEN boundaries

1. Exact frontend-to-core driver selection implementation in XGO: confirm instruction-level derivation from selected archive basename/path.
2. Exact Test04 1941.zip payload CRC/content.
3. Whether any parent/related archive is requested by XGO's 1941 driver and absent on card.
4. Whether generated catalog position/index changes frontend state before run_game preprocessing.
5. Live-list/cache invalidation after Refresh.
6. First runtime divergence after driver selection.

## Next offline task

Close item 1 from XGO BIN/reconstruction: locate the driver-name lookup path used by stock retro_load_game / FBA initialization and determine exactly which input string reaches it for the generated CPS1 launch.

Then determine the BurnDrvGetZipName archive dependency list for XGO 1941 if recoverable.

No Test05 authorized.
