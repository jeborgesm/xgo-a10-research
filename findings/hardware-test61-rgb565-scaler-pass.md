# Hardware Test61 — on-device RGB565 scaler PASS

Status: **HARDWARE PASS**

Test61 validates the on-device artwork resize/letterbox stage in the external `/CLASSIC/refresh.xgc` helper.

Observed on XGO hardware:

- The supplied `shinobib.rgb565` sidecar was accepted and displayed correctly.
- The source payload was 143,360 bytes = 320 x 224 x 2 bytes.
- XGO resized it on-device to fit the 144 x 208 CLASSIC preview contract while preserving aspect ratio.
- The resulting Shinobi artwork appeared correctly in the CLASSIC list.
- Test60 Refresh/reconciliation behavior remained functional.

This proves the pipeline stage after decode:

`source RGB565 -> resize/letterbox on XGO -> 144 x 208 little-endian RGB565 -> wrapper preview`

The remaining artwork task is now isolated to the **source image decoder** for ordinary PNG/JPEG input.

## Protected baseline after Test61

Preserve:

- Test61 external Refresh helper architecture and scaler
- Test60 add/remove reconciliation and correct `Games Updated` / `No New Games` semantics
- Test57 CLASSIC logo atlas fix
- Test52 CLASSIC Save/Load
- Test53 metadata/friendly-title behavior
- Mapper v19
- Audio OSD v8
- protected MAME2000 core

## Next stage

Add ordinary image input under `/CLASSIC/art/`, preferably:

- `<shortname>.png`
- `<shortname>.jpg` / `.jpeg`

Desired flow:

1. locate source image beside matching ROM stem;
2. decode image to RGB/RGB565 using a proven callable stock decoder or a small external decoder;
3. feed decoded pixels into the already hardware-proven Test61 scaler;
4. generate 144 x 208 RGB565 preview;
5. rebuild/create wrapper;
6. only after successful conversion/import, delete the original PNG/JPEG if that cleanup behavior is enabled;
7. retain `.rgb565` support as a fast/manual fallback path.

Do not modify the protected MAME2000 core or regress any protected baseline behavior.