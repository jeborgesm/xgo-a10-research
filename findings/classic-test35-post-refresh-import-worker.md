# Test35 — CLASSIC post-Refresh import worker

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

## Protected base

Exact hardware-good Test33A stretched-art package.

Hardware-confirmed before Test35:
- CLASSIC page stable with stretched artwork;
- Pac-Man works with MAME 0.37b5 ROM;
- Ms. Pac-Man works with MAME 0.37b5 ROM;
- Cadillacs and Dinosaurs works from CLASSIC;
- sound/controls/pause/OSD work;
- stock Arcade Cadillac works;
- Test33A does not exhibit Test34's transparent/stale page regression.

## Why Test34 failed

Test34 modified the Test08 six-pass console scanner loop itself. Hardware showed:
- CLASSIC composited with stale Neo Geo / Family Computer page content;
- Refresh became stuck and could not exit;
- no new CLASSIC games appeared.

The architecture is rejected.

The Test08 scanner discovers existing wrapper files and stable-merges them into catalogs. It does not manufacture CLASSIC wrappers from raw /CLASSIC/bin/*.zip archives.

## Test35 architecture

The original Test08 six-system FC/SFC/MD/GB/GBC/GBA scanner is preserved.

Only after that stock six-pass refresh finishes, firmware jumps through a 307-byte bootstrap at 0x807db9e0 in the verified zero tail of the existing scanner cave.

The bootstrap loads:

/mnt/sda1/cores/classic/refresh.bin

to runtime 0x86fe0000, flushes the loaded range, executes it, and maps its result back into the existing aggregate status path:
- 1 -> Games Updated
- 0 -> preserve stock result / No New Games
- -1 -> Refresh Failed

The CLASSIC worker uses the already-proven gp_buf_64m scratch arena, not stock malloc.

Worker behavior:
1. read clm.tax / clm.nec / clm.bvs;
2. validate synchronized counts;
3. scan /CLASSIC/*.zfb wrappers and read the embedded raw archive name at offset 59,908;
4. record existing ZIP references so human-named Pac-Man/Ms Pac-Man/Cadillac wrappers are not duplicated;
5. detect and repair orphan wrappers not present in the catalog;
6. scan /CLASSIC/bin/*.zip;
7. create a missing /CLASSIC/<rom>.zfb minimal wrapper for each previously unreferenced ZIP;
8. create a blank 59,904-byte 144x208 RGB565 thumbnail plus 4-byte spacer + archive filename;
9. stable-append filename/title/search entries;
10. fs_sync;
11. invalidate cached count for list ID 11 at 0x80d28978.

Existing catalog indices 1-3 remain unchanged.

Candidate cap is 128 new entries per pass.

## Candidate identities

xgo-classic-test35-classic-refresh-worker.zip

ZIP SHA-256:
b9eebc53b72bd92b3ef8ee28a79245d4e5042171b4a5d074305abf6e6833d187

Firmware SHA-256:
5eae7a39ac8696b35cb46b6d0ba40523f14233337b0b8b12cd09c484dbe78575

CLASSIC worker:
6554 bytes
SHA-256 9c2b3633b31ac7a2447258a591482f97c396390eb5b1ff8a131fa75a4675acc9

Bootstrap:
307 bytes
SHA-256 23782c01fa3a78d627adcae4bc2de110cf8cb299e6612b073dbc16a5de849fa7

## Hardware gate

With the existing ~41 MAME 0.37b5 ZIPs under /CLASSIC/bin:

1. boot and confirm CLASSIC page is visually identical to Test33A;
2. confirm initial CLASSIC count remains 3 before refresh;
3. run Refresh Games once;
4. expect Games Updated and a return to menu;
5. reopen CLASSIC and expect the additional ROM-derived entries;
6. verify Pac-Man, Ms Pac-Man and Cadillac remain the original first three entries and still launch;
7. launch at least one newly imported game;
8. run Refresh Games again and expect No New Games with no duplicates.

Do not merge until hardware passes.
