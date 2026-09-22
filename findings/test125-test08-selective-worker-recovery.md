# Test125 design — recover Test08 HW-proven discovery worker

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Status: SOURCE RECOVERY / DESIGN; no firmware candidate authorized yet.

## Historical recovery

Repository-first review found the exact prior solution that must be reused:

- `findings/game-list-test08-hardware-pass.md`: HW PASS.
- `tools/game_lists/build_test08_all_console_scanner_candidate.py`: exact Test08 reproducer, scanner blob SHA `a3f965d0ccabc2238da240a4b05b5f8027c968e40ede1831b51c42cff374c01d`.
- `tools/game_lists/build_test07_general_sfc_scanner.py`: readable source-level ancestor of the Test08 worker.

HW Test08 specifically discovered forgotten raw `.gb` files in `/GB`, appended them to the normal GB catalog, and launched Super Mario Land successfully. This is the behavior Test124 failed to reproduce.

## Important source recovery detail

Test08's exact reproducer stores its 3601-byte HW-proven scanner as a compressed/hash-pinned blob. The readable Test07 source exposes the worker algorithm and stock ABI used to construct the generalized Test08 implementation.

Therefore source preservation for the new selective worker must be readable construction source, not another opaque binary transplant.

## Test08 worker contract to preserve

For one selected stock console:
1. resolve the synchronized stock filename/title/search triplet;
2. scan the real physical system directory through stock `DIR_OPEN/DIR_NEXT/DIR_CLOSE`;
3. copy the original filename before stock extension classification mutates extension text;
4. classify through stock `UPPER_EXT` + `EXT_CLASSIFY`;
5. accept the system wrapper extension and native-family extension range;
6. compare exact physical filename against slot-0 catalog entries;
7. collect missing filenames;
8. preserve existing indices/order;
9. append exact filename to slot 0 and basename fallback to slots 1/2;
10. construct all three complete outputs in RAM;
11. rewrite synchronized triplet;
12. call the same Test08 sync wrapper;
13. invalidate only the selected frontend count cache;
14. restore the classifier global system-mask side effect.

## GB/GBC/GBA descriptor mapping

The new worker will be descriptor-driven but invoked for exactly one command:

| command | system | Test08 one-based list/resource index | stock catalog triplet | directory | accepted classifier returns |
|---|---|---:|---|---|---|
| 3 | GB | 4 | vdsdc.tax / umboa.nec / qdvd6.bvs | /GB | ZGB=6 or GBC/GB/SGB=23..25 |
| 4 | GBC | 5 | pnpui.tax / wjere.nec / mgdel.bvs | /GBC | ZGB=6 or GBC/GB/SGB=23..25 |
| 5 | GBA | 6 | vfnet.tax / htuiw.nec / sppnp.bvs | /GBA | ZGB=6 or GBA/AGB/GBZ=20..22 |

Folder identity intentionally separates GB and GBC even though their native classifier family overlaps.

## Integration constraint

Do not overwrite the old Test08 firmware cave wholesale: current Test123 contains years-later cumulative behavior there. Test125 must package the recovered scanner as an external helper or another proven non-colliding execution surface, then call it from the current post-workspace selective dispatcher.

Preferred architecture is an external helper because the project already has HW-proven external-helper loading/execution in the SFC/FC/MD enrichment and CLASSIC lineages. The helper can receive selected command/system ID and return `-1/0/1`; current firmware maps that to native Refresh Failed / No New Games / Games Updated.

Before building, search for and reuse the existing generic external-helper runner contract rather than creating a loader.

## Test125 hardware target

Leave the current newly added Mario GBC and Mario GBA ROMs untouched as blind pending inputs.

Expected:
- GB row remains converged unless another unindexed GB file exists;
- GBC row alone discovers the pending GBC Mario ROM;
- GBA row alone discovers the pending GBA Mario ROM;
- second invocation of each changed row returns No New Games;
- new entries launch through their correct stock emulator pages;
- CLASSIC remains exact Test123 behavior;
- Arcade remains inert.
