# Arcade catalog front-end — construction gate

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: READY FOR SOURCE-BUILT FRONT END; NO HARDWARE CANDIDATE

## Frozen inputs

Catalog semantic ancestor:
final HW-proven GBA catalog.xgc
SHA db7c1173f5b98adb3506b2676a035ba6e54b35a4391709cbbcd7ad92b983cbc6
size 2642.

Preservation boundary:
- replace discovery only;
- preserve stable slot0 compare/append semantics from the proven helper;
- preserve synchronized three-slot writes;
- remove/disable only the GBA-specific cache invalidation for Arcade first proof.

Four family descriptors are now source-pinned in
tools/arcade_refresh/catalog_family_descriptors.py.

## Manifest-reader ABI

Input:
- compile-time family descriptor;
- ASCII LF-terminated .refresh-list;
- exact outer .zfb basename per line.

Output to inherited merge logic:
- one validated filename at a time;
- empty manifest = no candidates;
- malformed/truncated manifest = failure;
- missing physical /ARCADE/<filename>.zfb = failure.

The front end must not:
- infer family from ZFB;
- inspect the ROM ZIP to choose family;
- enumerate all /ARCADE/*.zfb;
- mutate catalogs itself;
- write any guessed count-cache address.

## Construction audit before packaging

For each family binary:
1. exact triplet literals match the XGO list 7/8/9/10 table;
2. only that family's manifest path is reachable;
3. suffix accepted is .zfb only;
4. inherited catalog body is unchanged except relocations/code references required by the new front end;
5. no GBA path/catalog/cache literal survives;
6. return contract remains -1/0/1;
7. empty manifest returns 0;
8. malformed manifest returns negative;
9. existing slot0 identity is idempotent;
10. new identities append without reorder.

Only after all four pass offline do we wire command 6.
