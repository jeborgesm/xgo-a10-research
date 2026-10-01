# CPS1 active-driver selection — source-family closure and XGO boundary

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Status: SRC/UP correspondence + BIN lineage. No hardware candidate authorized.

## Source-family behavior

The later FB Alpha libretro loader family identified in XGO uses the content path/basename to choose the Burn driver before archive loading.

Conceptually:
1. retro_load_game receives the game/content path;
2. the filename component is reduced to the archive/game short name;
3. the driver table is scanned for a matching short driver name;
4. nBurnDrvActive is set to that matching driver;
5. failure to find a match produces the preserved "Cannot find driver" diagnostic;
6. only after driver selection does open_archive()/BurnDrvGetZipName() construct and parse the driver's archive set.

This ordering is independently consistent with the XGO BIN diagnostic vocabulary and with the already-established XGO wrapper preprocessing contract.

## XGO-side input state

Existing BIN archaeology established that stock run_game preprocessing resolves/mutates the persistent archive-name state before FBA dispatch and that the selected archive filename component is also used in the stock /bin/%s path construction.

For the two comparator cases:
- stock Cadillacs wrapper carries dino.zip;
- Test04 generated wrapper carries 1941.zip.

XGO BIN contains both short driver identities:
- dino
- 1941

Thus, under the source-family driver-selection contract, both content names have direct compiled driver matches.

## Classification discipline

The exact instruction-level XGO driver-table scan has not yet been independently reconstructed here, so do not label the full algorithm BIN.

What is closed:
- XGO BIN contains the expected driver names and diagnostics;
- XGO preprocessing supplies the archive filename state;
- the identified 621e371 loader family selects active driver before archive loading;
- 1941 is a valid direct short-name match.

What remains OPEN:
- exact XGO instruction addresses/data flow from archive-name state into the driver-table scan;
- exact Test04 archive payload;
- post-selection runtime divergence.

## Consequence

A simple "generated entry selected no driver because 1941 is unknown" explanation is now inconsistent with the available evidence.

The likely failure boundary has moved beyond mere driver-name existence/matching unless an XGO-specific deviation from the identified loader family is demonstrated.

## Next offline task

Search the existing XGO disassembly/reconstruction for the stock FBA retro_load_game entry and the "Cannot find driver" xref neighborhood. Recover:
- exact input pointer used for short-name matching;
- matching comparison routine;
- nBurnDrvActive/global write;
- transition into open_archive.

If that can be closed at BIN level, compare it with the stock preprocessing globals already mapped for dino.zip/1941.zip.

No Test05 authorized.
