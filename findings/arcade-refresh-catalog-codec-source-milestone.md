# Arcade Refresh — catalog codec and stable-append source milestone

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **SOURCE CLOSED / HOST INVARIANTS CLOSED; CURRENT-CATALOG HARNESS READY**

## Source added

`tools/arcade_refresh/catalog_codec.py`

The codec is intentionally stricter than a generic serializer. It validates:
- 32-bit LE count;
- complete offset table;
- first offset exactly zero;
- strictly increasing offsets;
- each string NUL-terminated;
- adjacent strings exactly contiguous;
- final string ends exactly at EOF;
- synchronized triplet counts.

Stable append:
- preserves every original offset word exactly;
- preserves the entire original string blob exactly;
- appends one new relative offset equal to old blob length;
- appends slot0 exact ZFB identity;
- appends friendly title to slots1/2;
- uses exact slot0 bytes as idempotence key;
- never sorts/reorders/deletes/normalizes existing OEM records.

## Host invariant tests

`tools/arcade_refresh/test_catalog_codec.py` covers:
- synchronized one-record append;
- old-offset preservation;
- old-string/blob preservation;
- exact second-run no-op;
- fail closed on triplet count mismatch;
- fail closed on unknown trailing bytes/footer.

## Current-card validation harness

`tools/arcade_refresh/verify_current_arcade_catalogs.py` is non-mutating and expects the current physical Resources directory. It validates exact current counts:
- CPS1 27 (includes known Test11 Pac-Man diagnostic residue);
- CPS2 28;
- IGS 6;
- NeoGeo 117.

For each family it simulates one synthetic append in memory, checks stable-prefix preservation, then repeats the same append and requires a byte-identical no-op.

This harness is ready for the current physical baseline catalog files. If those bytes are not locally available in the execution environment, no claim of direct execution against them is made.

## Architectural consequence

Catalog mutation logic is no longer an algorithmic unknown. The remaining on-device problem is implementation of this exact transform under the XGO VFS plus durable three-file commit/recovery.

Next:
1. collision/idempotence planner across /ARCADE/bin, outer ZFBs and all four slot0 catalogs;
2. transaction/recovery protocol;
3. JPEG -> RGB565 worker reuse;
4. runtime helper construction.
