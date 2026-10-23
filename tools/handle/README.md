# Native Handle P1/P2 + PAL Setup repair — GOLD (2026-10-22)

This directory contains the preserved text-only, hash-guarded rebuild stages for the hardware-proven XGO A10 native Setup P1/P2 selector, PAL Refresh/Handle submenu renderer and final TV-mode text placement. **Task closed / gold promoted**; see [`findings/2026-10-22-native-handle-pal-GOLD-closure.md`](../../findings/2026-10-22-native-handle-pal-GOLD-closure.md).

## Hardware-proven final artifact

- Complete owner's archive: `XGO_PAL_Fixed_TV_Text_Final12_Bold_Handle_TEST.zip` (now GOLD; original test filename deliberately retained for forensic provenance).
- ZIP SHA-256: `42c3f05ab3365f3fb58016d770f89106378b9ecedc4741599927058af9d7eb6c`.
- Firmware SHA-256: `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`.
- LCFG firmware CRC32/MPEG2: `0x80744DD0`.
- Hardware-passing previous PAL repair ZIP: SHA-256 `2451905dd48626524dc0303a50388170ac1ee71b7d3b29e70a45253de3e623b2`.

## Rebuild pipeline

1. Start from the previously HW-passing native toggle package and its six approved RGB565 Setup screens. The owner holds the exact legacy snapshots and GOLD ZIP in the private firmware vault.
2. `pal_setup_branch_repair.py` patches alternate PAL Setup exits to invoke the existing first-stage renderer. The first-stage renderer continues naturally into stage two.
3. `build_tv_mode_final12.py` performs the final -12 X, +12 Y TV-label adjustment **on the preceding hardware-passing PAL repair ZIP** and validates its SHA before changing six instruction words. The script also reseals CRC32/MPEG2.
4. Full original generation and verification scripts are embedded in the owner's GOLD ZIP under `SOURCE/` (`build_xgo_native_handle_toggle.py`, `verify_xgo_native_handle_toggle.py`, `build_xgo_pal_branch_restore_bundle.py`, `build_xgo_tv_final_12px.py`). The repository contains the small text-only stage builders to avoid publishing the proprietary full firmware.

Example (only if both verified input packages are in the working directory):

```bash
python tools/handle/build_tv_mode_final12.py \
  XGO_PAL_Submenu_Render_Branch_Repair_TV_Alignment_Combined_TEST.zip \
  XGO_PAL_Fixed_TV_Text_Final12_Bold_Handle_TEST.zip
sha256sum XGO_PAL_Fixed_TV_Text_Final12_Bold_Handle_TEST.zip
```

**Do not** treat a mere CRC match as hardware proof. This GOLD designation is based on the user's real NTSC/PAL and Handle tests. Do not supersede fixed-P1 recovery or cumulative stock/CLASSIC/Audio-OSD baselines. Keep failed interim PAL isolation artifacts and exact diffs in historical findings.

## Evidence

- [Root-cause and GOLD closure](../../findings/2026-10-22-native-handle-pal-GOLD-closure.md)
- [PAL branch repair](../../findings/2026-10-22-pal-branch-render-fix-candidate.md)
- [PAL hardware pass and final alignment diff](../../findings/2026-10-22-pal-submenus-hw-pass-tv-label-final-offset.md)
- [Historical fixed-P1 hardware pass](../../findings/handle-interface-p1-hardware-pass-20261021.md)
