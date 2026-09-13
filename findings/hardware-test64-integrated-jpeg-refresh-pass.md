# Hardware Test64 — integrated JPEG Refresh PASS

Status: **HARDWARE PASS**

Test64 validates the corrected single-transaction architecture for ordinary JPEG artwork conversion inside `/CLASSIC/refresh.xgc`.

Observed on physical XGO hardware:

- `/CLASSIC/bin/shinobi.zip` paired with `/CLASSIC/art/shinobi.jpg` was reconciled using the ROM shortname automatically.
- Refresh generated `/CLASSIC/art/shinobi.rgb565` on-device.
- The generated preview is the proven 144 x 208 little-endian RGB565 contract (59,904 bytes; Windows displays it as about 59 KB).
- The artwork displayed correctly in the CLASSIC game list.
- The conversion occurred inside the same Refresh flow rather than a separate pre-pass.

Architecture now protected from Test64 forward:

`Refresh -> per-ROM reconciliation -> existing RGB565? -> JPEG decode if needed -> normalize preview -> rebuild wrapper -> mark changed`

No hardcoded game names and no second SD-side worker process are required.

Test62/Test63 pre-pass experiments are superseded and should not be used as baselines.

The next candidate extends this exact Test64 flow with PNG support while preserving JPEG as fallback, the Test61 scaler/wrapper logic, Test60 reconciliation/no-change behavior, Test57 logo atlas fix, Test52 Save/Load, Mapper v19, Audio OSD v8, and the protected MAME2000 core.