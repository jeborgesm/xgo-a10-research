# Hardware test: PAL isolation reconstruction — FAILED (2026-10-22)

## User-reported hardware results (HW)
User installed the reconstructed PAL render isolation candidate and reports:
- In **NTSC**, P1/P2 underline is **no longer visible**.
- PAL and NTSC text labels remain **out of place**.
- P1/P2 controller **behavior changes correctly** when switched.
- Thus routing/toggle functionality survives, but display/UI is regressed. This is **not a successful PAL rendering fix**.

## Causal comparison (BIN + HW)
- Reconstructed candidate `XGO_PAL_Render_Isolation_Reconstructed_UNTESTED.zip` changed instruction at `0x80A38AB4` from `0x1120FD3B` (custom status hook) to original `0x1120012E` (bypass status renderer), and updated CRC.
- Builder `SOURCE/build_xgo_native_handle_toggle.py` shows status underline routine at `0x80A37FA4` and entry branch at `0x80A38AB4`.
- **HW observation is consistent with deliberately disabling the underline routine.** This change cannot fix the PAL/NTSC static text placement because text is pre-rendered into six 640x480 RGB565 Setup resources.
- Do not retest this failed reconstruction as a fix. Re-enable status hook for NTSC while separately diagnosing PAL framebuffer and static resource placement.

## Next engineering actions
1. Return to native toggle candidate for working NTSC underline, preserving functional controller routing.
2. Inspect static Setup resource bitmaps: PAL/NTSC labels are drawn in bitmap, not corrected by status hook. Locate exact source placement and icon bounding boxes; reposition labels in all six languages.
3. Diagnose PAL-specific Refresh/HANDLE invisibility in the compositor/renderer separately from status overlay, comparing NTSC/PAL frame buffer dimensions, strides and TV-mode transitions.
4. Produce new A/B candidate only after code/resource differences and CRC verified; collect NTSC and PAL screenshots and hardware observations.

## Provenance
HW: direct user report in conversation. BIN: local binary/package/source inspection. INF: cause of missing underline follows bypassed hook. No claim that PAL framebuffer cause is proven.
