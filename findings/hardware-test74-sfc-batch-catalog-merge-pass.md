# Hardware Test74 — SFC batch catalog merge PASS

Date: 2026-09-13
Branch: `research-stock-catalog-enrichment`
Status: **HARDWARE PASSED**

## Candidate

`xgo-stock-test74-sfc-batch-catalog-merge.zip`

ZIP SHA-256:
`219c61525bb8b8ba1cb0db8c3d59b70a44e068242d51e12f5f6942ea2ccbc8fc`

## Hardware result

The Test73 materializer had already generated:

`/SFC/Super Mario All-Stars + SMW.zsf`

but Test73 did not propagate that wrapper into the visible SFC catalog.

Test74 added an explicit SFC catalog merge stage after materialization rather than depending on the generalized scanner to notice a wrapper created during the same Refresh operation.

Hardware test result reported by the operator: **success; everything worked as expected.**

This confirms the complete single-entry proof path:

1. existing/generated top-level `.zsf` is detected by the explicit SFC merge;
2. the wrapper is appended to the stock SFC catalog;
3. friendly title is visible;
4. artwork is visible;
5. game launches;
6. second unchanged Refresh reports `No New Games`;
7. no duplicate entry is produced.

## Batch architecture now proven at single-entry scale

The intended ordering is:

`SFC materialization -> explicit SFC catalog merge -> existing six-console scanner -> unchanged Test72 CLASSIC path`

The explicit merge is intentionally batch-oriented: collect all missing top-level `.zsf` wrappers, then perform one synchronized SFC catalog update. The current candidate is sized for up to 256 missing SFC wrappers in one Refresh.

This hardware pass proves the architecture and idempotent single-entry behavior. It does **not yet prove a multi-game batch**. The next hardware gate should use a small 3–5 game batch before a 40+ game stress batch.

## Important negative finding

Filename length was not the Test73 failure. The generated Mario wrapper filename was only 31 bytes while the real stock SFC inventory contains filenames up to 66 bytes. Test73 failed at catalog propagation, not wrapper generation or filename handling.

## Protected baseline

Continue protecting the cumulative Test72-era behavior including Mapper v19, CPS1 pacing, Audio OSD v8, stock consoles, stock Arcade, generalized Refresh, CLASSIC importer, normalized MAME2000 core, CLASSIC Save/Load, and CLASSIC metadata/artwork behavior.

Do not propagate this implementation to FC/MD/GB/GBC/GBA until SFC batch behavior has been hardware-proven.