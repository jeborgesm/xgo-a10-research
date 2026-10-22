# PAL submenu compositor — BIN audit (2026-10-22)

HW: Both Refresh and Handle menus fail to display in PAL; work in NTSC. P1/P2 switching works. User approved bold caption graphics. Do not request another SD flash for a cosmetic-only adjustment.

BIN: Native toggle candidate XGO_TV_Text_Left24_Bold_P1_P2_PAL_Pending_TEST.zip.
At 0x80A38A58 custom render routine saves registers and loads pending Refresh flag 0x80A389C0.
At 0x80A38AB4 branch 0x1120FD3B routes when pending=0 to underline routine 0x80A37FA4, while pending nonzero continues into Refresh compositor at 0x80A38ABC.
At 0x80A38ABC load s0 from gp-0x1410 (framebuffer). Source pixel at framebuffer+0x1FA14 and destination starts at framebuffer+0x1FA50.
At 0x80A38AD8 rows=360; 0x80A38AE0 columns=560; 0x80A38AF8 stride increment=0x500 (1280 bytes). An initial halfword is loaded once before loops and repeated to clear rectangular region. This is a fixed 640-RGB565-row-stride assumption.
Text overlays then call 0x80354A29 using framebuffer from gp-0x1410 and hard-coded x/y coordinates, before restoring registers at 0x80A38E90.
OPEN: PAL-specific framebuffer stride, framebuffer page and display commit behavior not proven. Do NOT call the fixed stride itself the verified root cause. The failed underline-bypass experiment does not fix PAL menus.

BIN: TV-mode text coordinates in latest native offset candidate:
- file 0x359B88 X=101 (0x24050065), file 0x359B8C Y=297 (0x24060129).
- file 0x35AC98 X=109 (0x2405006D), file 0x35AC9C Y=297 (0x24060129).
- file 0x35ACD0 X=117 (0x24050075), file 0x35ACD4 Y=297 (0x24060129).
User requests TV-mode text a little farther LEFT and perhaps DOWN similarly. Bundle with actual PAL menu rendering fix, keeping all six approved bold-caption resources and native underline hook 0xA38AB4=0x1120FD3B.

Next: trace PAL mode framebuffer origin, row stride, scanout state and compositor call path. Determine actual observed difference before patching. Avoid premature test ZIP.