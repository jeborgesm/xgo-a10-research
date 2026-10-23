# XGO Archeology — CURRENT Handle/PAL firmware handoff
Checkpoint date: 2026-10-22. Branch: research-handle-interface-p1-experimental.

## User priorities
Do not restart. Do not issue a cosmetic-only SD flash. Approved bold Setup / Refresh / Handle captions are golden. Mode underline and P1/P2 toggling work in NTSC. Both Refresh and Handle submenu graphics disappear after PAL selection, while their input actions continue. TV NTSC/PAL text needs slight extra left/down move. Bundle fixes in one test.

## Root-cause candidate established offline (BIN)
NTSC Setup ends its native TV-text drawing at 0x80359BA0 and jumps at 0x80359BA8 to first-stage custom renderer 0x80A38A58. Two other TV-mode paths finish at 0x8035ACB0 and 0x8035ACE8 but JUMP at 0x8035ACB8 and 0x8035ACF0 directly to second stage 0x807DB9D4, bypassing first-stage drawing. The first-stage EXIT already jumps to second stage at 0x80A38EF0. Thus all three paths can share the first-stage/second-stage chain.

## Combined candidate produced (hardware UNTESTED)
Filename XGO_PAL_Submenu_Render_Branch_Repair_TV_Alignment_Combined_TEST.zip
ZIP SHA256 2451905dd48626524dc0303a50388170ac1ee71b7d3b29e70a45253de3e623b2
Firmware SHA256 efaec378c7ce6ffee8e68e42228fc05dc6514c8a67ac1ba98eb9d34b54f73481; CRC MPEG2 7ba94869.
Changed jumps file 0x35ACB8 and 0x35ACF0: 0x081F6E75 -> 0x0828E296.
Also changed native TV label X at 0x359B88 / 0x35AC98 / 0x35ACD0 by another -12 pixels and Y at 0x359B8C / 0x35AC9C / 0x35ACD4 by +12 pixels.
All six approved bold resource bitmaps byte-for-byte preserved; fixed-P1 recovery unchanged; original NTSC hook at 0x359BA8 unchanged; first-to-second-stage jump unchanged; controller normalization and P1/P2 underline unchanged.
Firmware differs only at 8 instruction words and CRC; offline integrity/CRC and changed-byte tests PASS. The ZIP embeds source, patch manifest, README and recovery.

## GitHub checkpoints
- findings/2026-10-22-pal-branch-render-fix-candidate.md
- tools/handle/pal_setup_branch_repair.py
- findings/2026-10-22-next-bundled-pal-render-and-tv-label-target.md
- findings/2026-10-22-tv-label-offset-bold-caption-pal-menu-status.md

## Next action
User hardware-test combined candidate on SD clone: NTSC Setup/Refresh/Handle underline and routing; switch PAL and verify Refresh + Handle graphics visible, control routing, TV label alignment; switch back NTSC. Await actual results before HW-PASS claim. If PAL still fails, trace 0x807DB9D4 stage-two and video framebuffer/page handling. No assumptions of background execution and no repeated narration.
## NEWEST HW result + followup (2026-10-22)
- User reports the combined PAL submenu branch-repair firmware WORKED on physical device. Thus Refresh and Handle submenu visibility in PAL is now HW-PASS. This supersedes this document's older 'hardware UNTESTED' classification for the combined baseline; keep its ZIP/SHA intact as rollback baseline.
- User requests only a further TV-mode dynamic label X=-12 / Y=+12 versus that hardware-passed baseline.
- Built XGO_PAL_Fixed_TV_Text_Final12_Bold_Handle_TEST.zip; ZIP SHA256 42c3f05ab3365f3fb58016d770f89106378b9ecedc4741599927058af9d7eb6c; firmware SHA256 75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b; CRC32/MPEG2 0x80744dd0.
- Changed only 6 native TV string coordinates at offsets 0x359B88/8C, 0x35AC98/9C, 0x35ACD0/D4 and CRC at 0x18C-18F. Six approved bold resources, PAL rendering branch fixes, controller P1/P2/underline and fixed-P1 recovery are byte-identical to HW-pass baseline.
- Exact byte checks passed. The new text alignment coordinates remain UNTESTED on hardware; DO NOT call it HW-PASS until reported.
- Full evidence in findings/2026-10-22-pal-submenus-hw-pass-tv-label-final-offset.md. Reproducible builder tools/handle/build_tv_mode_final12.py, plus exact packaged build source at SOURCE/build_xgo_tv_final_12px.py in candidate ZIP.

### Next
Test label placement NTSC + PAL and confirm Refresh/Handle still visible. Retain hardware-proven combined PAL ZIP as recovery. Once approved, archive hashes and consider branch merge. No need for additional PAL root-cause archaeology unless regression observed.