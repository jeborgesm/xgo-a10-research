# Arcade Refresh Test05A — artwork repair hardware result

Date: 2026-09-27
Branch: `research-arcade-refresh-four-family`

## Candidate

Test05A was deliberately a narrow hardware probe derived from the exact physical Test04 CPS1 materializer.

Parent `refresh.xgc`:
- size: `0x101F08`
- SHA-256: `301df6494c89928cf615a918b76f81d4c0774d864cd45c77cacc2e145fed3f28`

Test05A `refresh.xgc`:
- SHA-256: `2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2`

Only patched fields:
- `/mnt/sda1/ARCADE/CPS1/art/.xgo.jpg` -> `/mnt/sda1/ARCADE/.xgo.jpg`
- `/mnt/sda1/ARCADE/CPS1/art/.xgo.rgb565` -> `/mnt/sda1/ARCADE/.xgo.rgb565`

No `bios/bisrv.asd` modification.

## Hardware sequence and observations

1. Installing Test05A over the existing Test04 state and running Refresh initially reported **No New Games**. The existing 1941 entry still had the old black artwork. This run did not exercise artwork generation because the previously published 1941 ZFB/catalog state already existed; therefore it is not evidence against the artwork repair.

2. The existing generated 1941 ZFB was removed and Refresh was run again.
   - UI result: **Refresh Failed**.
   - Afterward, 1941 was present in the CPS1 list with **real artwork**.
   - 1941 launched and played normally.

3. At that point the SD contained different 1941 archives:
   - `/ARCADE/CPS1/import/1941.zip`: older incompatible import archive.
   - `/ARCADE/bin/1941.zip`: known-compatible replacement previously proven to launch.

   This explains the mixed result consistently with the materializer's runtime-ZIP convergence protection: artwork/ZFB regeneration completed, then the differing existing runtime ZIP prevented clean convergence and the overall Refresh reported failure.

4. The import copy was then replaced with the same compatible 1941 ZIP used in `/ARCADE/bin/1941.zip`.

5. Refresh was run again.
   - UI result: **No New Games**.
   - 1941 retained the newly generated artwork.
   - 1941 remained playable.

## HW conclusions

### Artwork scratch repair: PASS

The Test05A scratch-path change is hardware-proven to allow the JPEG path to produce a real Arcade preview/ZFB. Preserve this change in the four-family implementation.

### Runtime ZIP collision protection: observed working

A differing existing runtime ZIP can cause the overall Refresh to fail after artwork generation rather than silently replacing that runtime ZIP. Once import and runtime ZIPs were synchronized, the no-change path completed as **No New Games**.

### Immediate Arcade re-entry freeze: NOT REPRODUCED in current testing

During the 2026-09-27 Test05A sequence, repeated Refresh/list-entry/launch operations did not reproduce the original Test04 immediate CPS1 hard freeze. Do not patch the BIN-closed list-7 count-cache slot merely to fix an unreproduced symptom. Keep the cache-invalidating mechanism available if a reproducible stale-list failure returns.

## Status / next boundary

Preserve:
- Test05A shared `/ARCADE/.xgo.jpg` and `/ARCADE/.xgo.rgb565` scratch repair.
- Known-compatible 1941 hardware evidence.
- Conservative runtime-ZIP convergence behavior.

Do not spend another archaeology cycle on artwork or the currently unreproduced freeze.

Next implementation target is the intended four-family Refresh with compatibility filtering, using the already recovered XACM/ZIP compatibility architecture. Hardware testing remains the arbiter; do not require closure of unrelated uncertainties before the next controlled candidate.
