# Test57 — CLASSIC logo atlas completion — Hardware PASS

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Hardware result

Test57 passed on the physical XGO. The persistent narrow scrambled strip on the CLASSIC game-list screen is gone.

Root cause: CLASSIC was added as a functional frontend/list state, but the stock UI atlas used by the bottom system/category logo area had not been extended for the new CLASSIC slot. The stock `Resources/ihdsf.bke` resource is a vertically stacked RGBA atlas. Test57 preserves the original atlas byte-for-byte and appends one new CLASSIC slot.

Therefore the correct architectural model is: a complete new XGO list/page requires all relevant stock-style UI resource slots, not only list metadata and launch plumbing.

## Protected baseline update

Test57 is now part of the cumulative protected baseline together with:

- Mapper v19;
- Audio OSD v8;
- Test47 generalized CLASSIC importer;
- normalized `/cores/classic-mame2000/core.xgc`;
- Test52 CLASSIC Save/Load;
- Test53 metadata + raw RGB565 artwork enrichment;
- stable Refresh / no-change behavior;
- CLASSIC landing artwork as locally preserved by the user;
- Test57 completed CLASSIC game-list logo atlas.

Future candidates must preserve Test57 behavior and must not overwrite the CLASSIC landing artwork resource.

## Next work

Resume metadata/importer work:

1. add safe CLASSIC removal/reconciliation when `/CLASSIC/bin/<shortname>.zip` is deleted;
2. continue mapping an on-device PNG/JPEG decode path so ordinary artwork files can be converted to the proven 144x208 little-endian RGB565 wrapper preview format;
3. only after CLASSIC hardware passes, generalize to the other systems.
