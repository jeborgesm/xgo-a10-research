# GOLD closure — native Setup Handle P1/P2 toggle and PAL submenu repair

**Date:** 2026-10-22. **Status:** HW-PASS / GOLD. **Source branch:** `research-handle-interface-p1-experimental`.

## Hardware evidence and final approval

- HW: Native Setup Handle selector switches between external controller P1 and P2; behavior changes correctly. P2 remains default at cold boot.
- HW: P1/P2 mode underline is visible and changes with selected mode. Preserve the native status hook instead of the failed PAL-isolation bypass.
- HW: The Refresh and Handle submenus display and function in NTSC.
- HW: Both Refresh and Handle submenus, previously invisible after switching to PAL, now display and function in PAL after the combined stage-one rerouting correction. User: 'that worked'.
- HW: Bold SETUP, REFRESH and HANDLE resource captions passed.
- HW: Final native NTSC/PAL label alignment (-12 X, +12 Y from prior PAL-passing build) passed. User: 'ok that works. we can promote tpo gold'.

**Do not conflate:** Final user approval establishes the cumulative native Setup/PAL/Handle task. It is not a fresh per-core regression test of every stock FC/SFC/MD/GB/GBC/GBA/Arcade/CLASSIC title.

## Immutable GOLD artifact / recovery

- Gold ZIP name: `XGO_PAL_Fixed_TV_Text_Final12_Bold_Handle_TEST.zip` (promoted unchanged to GOLD; filename may retain TEST).
- ZIP SHA256: `42c3f05ab3365f3fb58016d770f89106378b9ecedc4741599927058af9d7eb6c`.
- `bios/bisrv.asd` SHA256: `75f858b6d9a1eb81235ae9e9c9b449a6a3052ad4365e5411b8ce041075e99d6b`.
- BIOS size: 12,768,452 bytes. LCFG CRC32/MPEG2 at file 0x18C: `0x80744DD0`.
- ZIP contains six RGB565 Setup bitmaps under `Resources/`, `RECOVERY/bios/bisrv.asd`, all patch manifests, README files and full-source `SOURCE/*.py` scripts. ZIP integrity was verified after final approval.
- Protected fixed-P1 recovery BIOS SHA256: `8a8cf7a84f7771b0fc116b80521e13d3dfbd5aace73e6053fb7494eaa7d44c4a`.
- Hardware-passing PAL branch-repair predecessor ZIP SHA256: `2451905dd48626524dc0303a50388170ac1ee71b7d3b29e70a45253de3e623b2`. Preserve as a known-good fallback.

## Root cause and final binary architecture

- The NTSC Setup drawing path already called the first-stage custom renderer `0x80A38A58` through jump at file `0x359BA8`.
- Two alternate video-mode paths jumped directly to second stage `0x807DB9D4`, omitting first-stage Refresh and Handle drawing. Redirected jumps at file `0x35ACB8` and `0x35ACF0` to `0x80A38A58`. First-stage still continues into second stage at `0x80A38EF0`.
- `0x80A38AB4` retains native P1/P2 mode underline hook (`0x1120FD3B`); prior attempt restoring the stock branch removed the underline and did not fix PAL menus.
- Dynamic NTSC/PAL label final X coordinates: 77, 85, 93 at file `0x359B88`, `0x35AC98`, `0x35ACD0` respectively. Final Y=321 at `0x359B8C`, `0x35AC9C`, `0x35ACD4`.
- PAL stage-one repair is also present in final BIOS. Approved Setup bitmaps all unchanged relative to the preceding PAL-passing ZIP.
- Existing external Handle routing hook and working Refresh dispatcher remain unmodified in final alignment step.

## Reproducibility / provenance

- Full assembly/bitmap and verification sources are embedded in the approved GOLD ZIP under `SOURCE/`.
- GitHub text builders `tools/handle/pal_setup_branch_repair.py` and `tools/handle/build_tv_mode_final12.py` reconstruct final changes from verified predecessor ZIPs, with exact SHA safeguards.
- See detailed hardware and instruction provenance in `findings/2026-10-22-pal-submenus-hw-pass-tv-label-final-offset.md` and `findings/2026-10-22-pal-branch-render-fix-candidate.md`.
- Historical negative tests are retained for archaeology rather than erased.

## Branch closure

All accepted Handle toggle/Setup/PAL changes are GOLD. This research branch can be merged into `main` without replacing unrelated concurrent work (particularly RP2040 live-controller work, workflows and cumulative stock console baseline). Preserve both parents in the merge commit. Update root README and active handoff to point to this closure, not the formerly open PAL issue.

Archive distribution note: the GOLD ZIP embeds a modified proprietary firmware image. Git records the reproducible code, exact digests and evidence; retain the binary package as a protected user-owned artifact rather than automatically publishing it in the public Git repository.