# GB / GBC / GBA Refresh wiring branch

Date: 2026-09-21
Parent: merged `main` at CLASSIC resurface PR #52 / Test123 HW PASS.

## Scope

Wire the existing REFRESH GAMES commands independently:
- 3 Game Boy
- 4 Game Boy Color
- 5 Game Boy Advance

Preserve command 6 Arcade as inert/non-mutating in this branch. Preserve command 7 CLASSIC exactly as HW-proven Test123.

## Protected parent behavior

Do not regress:
- Mapper v19 and per-game mapping persistence;
- repaired CPS1 pacing;
- Audio OSD v8;
- stock consoles and stock Arcade;
- CLASSIC MAME2000 runtime + Save/Load;
- Test74 SFC enrichment;
- Test75 FC enrichment;
- Test106 hardened MD transaction path;
- Test118 B-cancel behavior;
- Test119 Refresh re-entry normalization;
- Test122 producer-side stock selector suppression;
- Test123 independent CLASSIC Refresh route and canonical Test72 helper.

## Reuse-first starting evidence

The generalized native stock scanner is already BIN/SRC closed:
- entry `0x807DAE4C`;
- input `a0 = stock list ID`;
- return `v0 = -1 failure, 0 no additions, 1 additions`;
- requires native Refresh workspace initialized before post-workspace dispatch.

Known stock list IDs:
- 3 GB
- 4 GBC
- 5 GBA

Do not immediately patch these calls merely because IDs are known. First recover existing Test75/cumulative six-console loop and any preserved materializer/helper paths, compare with Test123, and choose the smallest architecture that preserves catalog/workspace/cache semantics.

Historical Test103 direct native-scanner substitution was NO BOOT and had an LCFG-reseal confound. Treat it as a boundary requiring explanation, not as proof that the scanner ABI is wrong.

## Branch exit gate

Each of GB/GBC/GBA must be independently hardware-proven from its own selector row and must not mutate another system.

The branch must preserve deterministic source/build logic, exact hashes/diff manifests and HW records in GitHub before merge.

## Follow-on

After this branch merges, create a dedicated Arcade branch. The single Arcade UI command must classify/orchestrate stock CPS1/CPS2/NeoGeo/IGS catalogs rather than pretending Arcade is one generic stock list.

Explicit ninth `Refresh All` remains later work after all eight individual operations are stable.
