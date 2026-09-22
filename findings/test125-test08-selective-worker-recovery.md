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


## Loader/lifecycle closure — 2026-09-22

Repository recovery found a safer current-lineage execution architecture than inventing a new helper loader.

### Rejected as the primary design

Calling a newly relocated scanner directly through the generic runner is not the preferred final architecture. The runner at `0x80A382E0` has a documented heap-ceiling guard against `0x80C237B0 > 0x86FFFFFF`; earlier selective FC/SFC/MD work showed that repeated helper sequencing can make a later invocation report the same `Refresh Failed` as a helper-internal error. That makes repeated handheld Refresh behavior unnecessarily dependent on an unresolved allocator lifetime.

Likewise, the CLASSIC bootstrap at `0x80A38000` is not a generic callable loader. Test92 HW proved that treating it as a standalone function hard-locks. Its loader mechanics are reusable evidence, but its entry contract remains a continuation under the live native Refresh frame.

### Recovered HW-proven current-lineage pattern

Test105/Test106 already solved the analogous problem for MD without changing the boot-sensitive generic-runner size immediate:

```
existing generic runner
  -> fixed 2642-byte Stage1 /MD/catalog.xgc
  -> Stage1 loads 7000-byte /MD/catalog-safe.xgc at 0x87180000
  -> cache maintenance
  -> Stage2 executes
  -> result returns through Stage1 and existing runner
```

HW Test105 proved normal and recovery execution; Test106 proved the hardened steady-state protocol. The Test104 negative result also establishes why the 2642-byte firmware load immediate must not be enlarged.

### Test125 execution architecture

Reuse that exact fixed-size Stage1 grammar for handheld discovery:

```
command 3 -> /GB/catalog.xgc  (2642-byte Stage1)
              -> /GB/catalog-safe.xgc (7000-byte Stage2)

command 4 -> /GBC/catalog.xgc (2642-byte Stage1)
              -> /GBC/catalog-safe.xgc (7000-byte Stage2)

command 5 -> /GBA/catalog.xgc (2642-byte Stage1)
              -> /GBA/catalog-safe.xgc (7000-byte Stage2)
```

Stage1 is derived from the HW-proven Test106 MD Stage1 loader with only the equal-length system path changed. Stage2 is a **source-rebuilt relocation of the Test07/Test08 HW-proven stable-merge worker**, parameterized for one selected handheld family. It returns `-1/0/1` to the existing Refresh status path and contains no selector/UI renderer.

This avoids:
- overwriting the old Test08 firmware cave;
- changing the boot-sensitive 2642-byte generic-runner size contract;
- inventing a loader;
- calling CLASSIC's continuation out of context;
- using the failed Test124 native scanner.

### Stage2 fixed family contracts

Resource-table entries are 24 bytes apart from base `0x80A3C32C`:
- GB list 3: `0x80A3C374` -> `vdsdc.tax / umboa.nec / qdvd6.bvs`;
- GBC list 4: `0x80A3C38C` -> `pnpui.tax / wjere.nec / mgdel.bvs`;
- GBA list 5: `0x80A3C3A4` -> `vfnet.tax / htuiw.nec / sppnp.bvs`.

The count-cache address must be taken from the HW-proven Test08 worker/recovered table grammar, not from the contradictory later native-scanner note. Current records disagree between a 4-byte native-scanner interpretation and the 8-byte-per-list FC/SFC/MD helper lineage. This address is therefore **OPEN** until recovered from Test08 binary/source before emission.

### Candidate gate tightened

Do not emit Test125 until:
1. the exact Test106 2642-byte Stage1 is hash-pinned and equal-length path patching is verified;
2. the Test07 worker is rebuilt at the Stage2 execution address with UI/status code removed;
3. GB/GBC/GBA classifier predicates match the Test08 HW-proven generalized scanner;
4. the Test08 count-cache invalidation calculation is recovered exactly;
5. Stage2 is padded/asserted to the proven 7000-byte Stage1 read contract;
6. current Test123 firmware receives only command-3/4/5 dispatch additions plus path data;
7. LCFG is resealed and all protected Test123 regions are asserted unchanged.
