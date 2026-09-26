# CPS1 1941 parent/clone archive dependency — BIN refinement

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Status: BIN/SRC narrowing. No hardware candidate authorized.

## New BIN evidence

The exact XGO bios/bisrv.asd contains two distinct 1941 driver identities:

- 1941
- 1941j

It also contains two distinct nearby ROM descriptor blocks.

The World/parent-style block begins with:
- 41e_30.rom
- 41e_35.rom
- 41e_31.rom
- 41e_36.rom
- 41_32.rom
- 41_gfx5.rom
- 41_gfx7.rom
- 41_gfx1.rom
- 41_gfx3.rom
- 41_09.rom
- 41_18.rom
- 41_19.rom

A second 1941-related block later in the binary begins with:
- 4136.bin
- 4142.bin
- 4137.bin
- 4143.bin
and then reuses the same shared 41_32 / gfx identities.

This is direct BIN evidence that XGO carries separate parent/clone ROM definitions rather than only a single undifferentiated 1941 record.

## Loader-family consequence

The preserved later-FBA loader asks the already-selected driver for archive names through BurnDrvGetZipName(). Clone drivers may therefore request their own archive plus parent archive(s).

For Test04, however, the wrapper archive basename is 1941.zip, which agrees with the XGO parent/World driver identity rather than 1941j.

Therefore a missing 1941 parent archive cannot explain launching 1941 itself: the selected archive is already named for the parent driver.

A clone-parent dependency remains relevant to 1941j, but there is currently no evidence Test04 selected 1941j.

## Narrowed question

The next decisive issue is no longer generic parent/clone support. It is exact driver-name selection:

Does stock retro_load_game derive the active driver from the content/archive basename 1941 and therefore choose the parent 1941 definition, as the preserved source family indicates?

If yes, Test04 should not require a separate clone archive merely to identify/load the World parent.

## Additional local observation

The 1941/1941j strings are embedded in the same dense CPS1 driver-name region that also contains dino/dinoj/dinou and neighboring CPS1 identities. This is consistent with normal compiled Burn driver metadata, not frontend-only strings.

## OPEN

- instruction-level XGO driver-name lookup;
- exact Test04 archive CRC contents;
- whether any support archive beyond the game archive is requested for the parent driver;
- generated-entry index/state effects before core entry;
- live-list/cache invalidation.

No Test05 authorized.
