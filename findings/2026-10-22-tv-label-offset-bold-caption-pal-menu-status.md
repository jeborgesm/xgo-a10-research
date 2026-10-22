# Hardware results and resource-caption diagnostic — 2026-10-22

## HW — user photograph and direct report
- Latest lower-left TV alignment ZIP boots and its Setup screen shows TV CRT icon on lower-left.
- Runtime **NTSC** text overlaps CRT icon at its right side; user requests moving the runtime text **left by approximately the width of two uppercase characters**. This remains **OPEN**; do not claim that an icon move or resource-only edit corrected it.
- Underline beneath P1 is visible in latest image, restoring NTSC indication.
- **Refresh and Handle submenus work in NTSC and do not render in PAL.** Reconfirmed explicitly, not speculative. PAL bug remains a HIGH-PRIORITY blocker.
- Captions **SETUP, REFRESH, HANDLE** need heavier weight (at least bold).

## Resource-only diagnostic generated
- Package: `XGO_Bold_Setup_Refresh_Handle_Typography_Resource_Test.zip`
- SHA-256: `10925f556f871fc2468d200c8e84b54255eb06ce8e0bf31e6822fb99187139fb`
- Base: `XGO_TV_BottomLeft_NTSC_Underline_Restored_PAL_Diagnostic.zip`; SHA-256 `b1d185686ebe2585113944e7fa2fc11e808fd04d1e04a9e1c86447d0bd9bd00e`.
- Firmware **byte-identical** to base (SHA-256 `853031610cec4103c89d9d8c66e68dfa89f9e5c49ef7f7ca4a607f339ea746bb`).
- Changes only six RGB565 Setup bitmaps by one-pixel horizontal dilation of near-white title glyph pixels in tight caption rectangles. 696 additional near-white pixels per language. Manifest included. ZIP integrity verified.
- Source script is local artifact `build_xgo_bold_caption_test.py`; source needs to be committed for reproducibility.
- **Not a fix for the remaining PAL failure or misplaced NTSC/PAL runtime label.** Not hardware-tested.

## Required engineering before final integration
1. Locate and adjust dynamic TV mode string drawing X coordinate, approximately two uppercase glyph widths to left. Do not patch unrelated graphic resources in lieu of the actual overlay coordinate.
2. Investigate PAL-specific submenu compositor / buffer state; BOTH Refresh and Handle lose menu visibility, though they respond to inputs. Analyze common rendering hook; leave P1/P2 routing unchanged.
3. Integrate verified bold resources after correcting the above; hardware A/B NTSC/PAL.

Evidence HW: user-provided image and report. BIN: package byte comparison; SRC: narrow resource pixel dilation. OPEN: exact dynamic text drawing site and PAL compositor cause.
