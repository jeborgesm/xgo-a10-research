# Test35 — dedicated CLASSIC raw-ROM Refresh candidate

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

## Motivation

Test34 is rejected. Hardware showed:
- CLASSIC page composited transparently with stale Neo Geo / Family Computer art;
- Refresh could hang and trap the menu;
- no new CLASSIC entries appeared.

The rejected architecture extended the stock Test08 six-pass console scanner loop to a synthetic seventh iteration. That disturbed frontend/UI state and was conceptually wrong for CLASSIC raw MAME ZIPs.

## Correct architecture

Test35 returns to hardware-good Test33A.

The stock Test08 six-system Refresh loop remains byte-for-byte unchanged.

Only after the six stock workers finish does Test35 invoke a separate CLASSIC worker loaded from:

/cores/classic/refresh.bin

The worker scans:

/CLASSIC/bin/*.zip

It does not run the stock per-console worker with list 11.

## CLASSIC wrapper generation

The worker reads every existing CLASSIC catalog entry, opens its .zfb wrapper, and reads the embedded target archive from offset 59,908.

Therefore existing pretty wrappers are preserved and raw archives already referenced by them are not duplicated, including:

- Pac-Man.zfb -> pacman.zip
- Ms Pac-Man.zfb -> mspacman.zip
- Cadillacs and Dinosaurs.zfb -> dino.zip

For each newly discovered ZIP, the worker creates a minimal CLASSIC .zfb wrapper using the already hardware-proven Test33 contract:

- 59,908 zero bytes;
- raw ZIP filename;
- two terminating zero bytes.

New wrapper name defaults to ZIP basename + .zfb.

## Catalog mutation

The worker loads current clm.tax and performs a stable append:

- old count becomes old + discovered-new;
- every old offset value remains unchanged;
- complete old string blob is copied byte-for-byte;
- only new offsets and new wrapper-name strings are appended.

The same output is written to:

- clm.tax
- clm.nec
- clm.bvs

This preserves aligned list-11 metadata for all current language/search paths.

After successful writes:

- filesystem sync is called;
- only cached count for list 11 is invalidated.

No delete and no reorder are performed.

## ROM-set result now authoritative

Hardware confirmed that replacing pacman.zip and mspacman.zip with MAME 0.37b5 versions makes both run correctly from CLASSIC with sound and expected runtime features.

For MAME2000 use the MAME 0.37b5 set. Prefer non-merged archives for isolated compatibility testing.

## Exact candidate

xgo-classic-test35-dedicated-refresh.zip

size:
7,543,524 bytes

ZIP SHA-256:
77268a6e6f10b1cbbf68086c05b94bc6746841da4b65991b6322e22d897df1ea

firmware SHA-256:
6a2b3938142543f0ed25f1d6f52ee6f5d76c4bee06c8747180e569a158ca91f1

CLASSIC refresh worker:
6,020 bytes
SHA-256 c02be8bf9d89324e982b89bf05ed82bed4cc75060abd15fdbaf8834cea4d02cc

exact Test12 MAME2000 core:
SHA-256 abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461

CI audit explicitly confirms stock six-pass Refresh loop preserved.

## Hardware gate

1. Boot and confirm CLASSIC page uses the Test33A stretched artwork (not Test34 transparent rendering).
2. Confirm existing Pac-Man / Ms Pac-Man / Cadillac remain visible.
3. Launch at least Pac-Man and Cadillac before Refresh.
4. Invoke Refresh Games once.
5. Confirm menu exits normally and stock timed result message behaves.
6. Return to CLASSIC.
7. Expected count should increase from 3 to roughly the number of unique MAME ZIPs under /CLASSIC/bin that were not already referenced.
8. Launch several newly-generated entries.
9. Reboot and confirm catalog additions persist.
10. Re-run Refresh; with no additional ZIPs, it should report no new games and create no duplicates.

Do not promote until hardware passes.
