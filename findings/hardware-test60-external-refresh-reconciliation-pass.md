# Hardware Test60 — external Refresh reconciliation PASS

Status: **HARDWARE PASS**

Test60 validates the external `/CLASSIC/refresh.xgc` architecture plus corrected final-catalog change detection.

Observed on XGO hardware:

- Refresh can add a new CLASSIC game.
- Refresh can remove a CLASSIC game after its ZIP is deleted from `/CLASSIC/bin`.
- Added/restored games launch and play normally.
- First Refresh after a real catalog change reports `Games Updated`.
- A subsequent Refresh with no filesystem/catalog change reports `No New Games`.
- Repeated no-change behavior no longer inherits Test59's sticky false-positive `Games Updated` result.

This makes Test60 the current protected Refresh/metadata baseline for the next artwork phase.

## Artwork boundary still in force

The currently proven sidecar contract remains:

`/CLASSIC/art/<shortname>.rgb565`

with an exact 144 x 208 little-endian RGB565 payload (59,904 bytes).

A supplied `shinobib.rgb565` was 143,360 bytes, corresponding to 320 x 224 x 2, so it was correctly rejected by the importer. This motivates the next stage: on-device decode/resize/conversion from ordinary PNG/JPEG source images.

## Next stage

Keep Test60 reconciliation and no-change semantics unchanged while extending the external helper architecture for image processing. The intended pipeline is:

1. find `/CLASSIC/art/<shortname>.png` or `.jpg`;
2. decode using a proven stock firmware decoder if a safe callable entry point can be established;
3. aspect-preserving resize/letterbox to 144 x 208;
4. convert/store little-endian RGB565;
5. use the resulting 59,904-byte preview in the generated `.zfb` wrapper;
6. delete the source PNG/JPG only after successful conversion/import;
7. retain existing `.rgb565` support and fallback art.

Do not modify the protected MAME2000 core, Test57 logo atlas, Test52 Save/Load path, Mapper v19, or Audio OSD v8.