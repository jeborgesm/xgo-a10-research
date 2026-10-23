# XGO native Setup — PAL submenu hardware PASS and TV-label final offset

Date: 2026-10-22 (user hardware feedback). Branch: research-handle-interface-p1-experimental.

## HW result: PAL submenu repair PASSED
The user tested XGO_PAL_Submenu_Render_Branch_Repair_TV_Alignment_Combined_TEST.zip and reported: 'that worked but we need to move the ntsc/PAL text more to the left and a bit down. IO think 12 and 12 is ok'. This establishes a hardware PASS for the PAL submenu repair in context of prior Refresh/Handle submenu invisibility. Do not retroactively claim unrelated subsystems were individually retested.
Preserve SHA256 of HW-pass source ZIP: 2451905dd48626524dc0303a50388170ac1ee71b7d3b29e70a45253de3e623b2.
HW-pass source firmware SHA256: efaec378c7ce6ffee8e68e42228fc05dc6514c8a67ac1ba98eb9d34b54f73481.
Previous accepted features: six bold RGB565 Setup resources, P1/P2 switching + underline, NTSC Refresh/Handle. PAL repair routes two alternate TV paths at 0x35ACB8 and 0x35ACF0 to first-stage 0x80A38A58, then to second-stage 0x807DB9D4.

## New label-only candidate, OFFLINE verified / hardware untested
Filename: XGO_PAL_Fixed_TV_Text_Final12_Bold_Handle_TEST.zip
ZIP SHA256: 42c3f05ab3365f3fb58016d770f89106378b9ecedc4741599927058af9d7eb6c
Result firmware SHA256: 75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b
CRC32/MPEG2 payload: 0x80744dd0.
BIN: +12 further down and -12 further left relative to hardware-passed combined candidate, at all three native string placements:
- 0x359B88 X 89 ->77 (0x24050059 -> 0x2405004D); 0x359B8C Y309 ->321 (0x24060135 ->0x24060141)
- 0x35AC98 X 97 ->85 (0x24050061 -> 0x24050055); 0x35AC9C Y309 ->321 (0x24060135 ->0x24060141)
- 0x35ACD0 X105 ->93 (0x24050069 -> 0x2405005D); 0x35ACD4 Y309 ->321 (0x24060135 ->0x24060141).
Only changed firmware byte offsets: 0x18C, 0x18D, 0x18E, 0x18F, 0x359B88, 0x359B8C, 0x35AC98, 0x35AC9C, 0x35ACD0, 0x35ACD4.
All original ZIP members, including all six bold resources and RECOVERY fixed-P1 image, are bit-for-bit preserved except bios/bisrv.asd; new manifest, README, and full local rebuild source added. ZIP passes CRC and member identity verification.
Critical protected words verified: 0x359BA8=0x0828E296, 0x35ACB8=0x0828E296, 0x35ACF0=0x0828E296, 0xA38EF0=0x081F6E75, 0xA38AB4=0x1120FD3B, 0x35D53C=0x0828E199.

## Next
Hardware check the new text position in NTSC and PAL; confirm no regression of Refresh/Handle menu rendering. Don't discard HW-pass PAL baseline until new candidate passes. Once approved, document and merge according to protected feature policy.