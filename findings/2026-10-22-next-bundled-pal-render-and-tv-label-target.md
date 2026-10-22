# Hardware feedback / combined next-test requirement — 2026-10-22

## Accepted baseline (HW)
- Six bold-caption Resources for SETUP / REFRESH / HANDLE have a PASS from user.
- XGO_TV_Text_Left24_Bold_P1_P2_PAL_Pending_TEST.zip moved native TV-mode label X coordinates left by 24 pixels, preserving mode underline and working NTSC toggle.
- TV-mode text still needs a little farther LEFT, and possibly DOWN by approximately equal amount. The 24px patch is not final.
- Both Refresh and Handle submenus work in NTSC but fail to render in PAL (HW-confirmed).

## User-directed test discipline
DO NOT request another card flash for single cosmetic tweak. Bundle final TV-mode text X/Y placement correction WITH substantive PAL submenu rendering fix in the next candidate. Preserve working P1/P2 routing and underline, approved bold captions, Refresh, CLASSIC, Audio OSD, stock consoles.

## Remaining analysis
1. Investigate common PAL submenu drawing path including TV-mode transition and framebuffer stride/ownership; the 640 RGB565 underline stride is an assumption, not proven PAL cause.
2. Locate Y coordinate of label drawing at three call sites currently X=101,109,117 after -24 modification, stock Y=297. Stage slightly more left/down but DO NOT request isolated hardware test.
3. Only deliver combined hardware-test ZIP after offline validation and concrete PAL-specific correction. Track hashes, code and hardware evidence in GitHub.