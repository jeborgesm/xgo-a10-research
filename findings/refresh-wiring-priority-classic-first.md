# Refresh wiring priority — CLASSIC first, stock handhelds second, Arcade separately

Date: 2026-09-21

## User priority

1. Rescue CLASSIC Refresh first.
2. Then wire GB/GBC/GBA.
3. Treat Arcade as a separate classification problem because the XGO frontend exposes four stock Arcade families/pages: CPS1, CPS2, NeoGeo and IGS.

Do not collapse Arcade into one generic stock-list operation.

## CLASSIC — existing HW-proven subsystem to restore

The target is not a new scanner. The repository already preserves a mature HW-proven CLASSIC content-management subsystem:

- generalized CLASSIC importer: Test47 HW PASS;
- external `/CLASSIC/refresh.xgc`: Test60+ HW PASS;
- JPEG decode/resize/wrapper generation: Test64 HW PASS;
- 50-game batch: Test72 HW PASS;
- unchanged second Refresh -> `No New Games`: Test72 HW PASS;
- protected final Test72 `CLASSIC/refresh.xgc` SHA-256:
  `6d416c71af871445023de96522d78bfa62b6277cfb7e5e37945bc12ea76dc98d`;
- protected normalized MAME2000 core SHA-256:
  `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`.

The firmware bootstrap/continuation at `0x80A38000` is not callable standalone. It must run under the native Refresh frame/workspace created by `0x807DB5CC`.

### Required Test123 architecture

Keep Test122 UI/input/presentation byte-identical.

At the post-workspace command dispatcher:
- commands 0/1/2 retain current FC/SFC/MD behavior;
- command 7 branches into the preserved CLASSIC continuation contract:
  `s5=0; j 0x80A38000`;
- commands 3/4/5/6 must NOT silently fall through to MD. Until implemented, they need a safe non-mutating result/return path.

The CLASSIC test must use the protected Test72 `/CLASSIC/refresh.xgc`; firmware alone cannot prove the mature importer.

## GB/GBC/GBA — second stage

The native stock scanner ABI already maps list IDs 3/4/5 to GB/GBC/GBA. However, the current FC/SFC/MD selective paths include enrichment/materializer stages, so do not assume merely calling the native scanner gives equivalent native-ROM/artwork enrichment. Reuse the existing generalized six-console scanner/materializer lineage before implementing these three commands.

## Arcade — separate design

Confirmed stock page identities:

```
list 7  CPS1
list 8  CPS2
list 9  NeoGeo
list 10 IGS
```

The physical card shares `/ARCADE`; classification is required before stable merge. A single UI row `Arcade` therefore represents an orchestrator over four family-specific stock pages, not one list ID.

CLASSIC/list 11 remains separate from those stock Arcade pages and uses the MAME2000/CLASSIC subsystem.

## Immediate implementation gate

Before Test123:
1. recover exact Test72 bootstrap words at `0x80A38000` and its loader ABI;
2. verify Test106/Test122 still preserves that bootstrap or determine what displaced it;
3. verify the SD candidate contains the exact protected Test72 `CLASSIC/refresh.xgc`;
4. extend only the post-workspace command decode for command 7;
5. prevent 3..6 from aliasing MD;
6. preserve Test122 renderer/B/suppression/status behavior;
7. deterministic builder + diff manifest + LCFG reseal before hardware.
