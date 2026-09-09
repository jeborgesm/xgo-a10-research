# Test28 — native first-class CLASSIC system

Date: 2026-09-08
Branch: research-game-list-arcade-expansion

## Architecture

Test28 abandons the list11->list7 compatibility design.

CLASSIC remains list ID 11 only because the frontend already has a menu slot for it. Everything else is independent:

- own visible category name: CLASSIC;
- own fixed metadata triplet: clm.tax / clm.nec / clm.bvs;
- own wrapper directory: /CLASSIC/;
- own ROM directory: /CLASSIC/bin/;
- own native launcher;
- exact archived Test12 MAME2000 core;
- no stock Arcade preprocessing;
- no list7 alias;
- no patch to the stock Arcade runtime call.

The generic browser launch calls are wrapped only to inspect ACTIVE_LIST_ID.

For list IDs other than 11:
  native launcher -> untouched stock run_game @ 0x80360b88.

For list ID 11:
  native launcher opens selected CLASSIC .zfb;
  seeks to proven embedded-name offset 59,908;
  reads ZIP basename;
  writes /mnt/sda1/CLASSIC to 0x810a0eb0;
  writes ZIP basename to 0x8109fce8;
  loads exact Test12 core.xgc to 0x87000000;
  performs proven sound-task stop, RAMSIZE ceiling, IRQ-GP repair and cache flush;
  enters exact Test12 core frontend;
  Test12 frontend installs callbacks/state and runs stock run_emulator();
  launcher restores previous frontend path globals on return.

## Menu handling

Test27 accidentally changed the control line and made the fifth page disappear.

Test28 preserves the last-known-visible menu geometry/control line exactly:

12 7 0
472 144 144 208
40 24

Only the fifth directory label changes from ARCADE to CLASSIC.

## Exact candidate

xgo-classic-test28-native-system.zip
size              7,401,889 bytes
ZIP SHA-256        c60f8b4760db48a33db14f90d9211051be2915bb39c8474cddfb4d3bb0fd82d3
firmware SHA-256   ca799f4fc727bb04368b2171075e799f2262d2475cd19df3ffa87cbe64337367

native CLASSIC launcher
size               1,991 bytes
SHA-256             1a2c98bbd0ab126efaae8e6cfc1280183b545ef2013b22b4864fe7ba77d2df61

exact Test12 MAME2000 core
SHA-256             abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461

Private CI run: 34299726436
Artifact ID: 10084477699

All offline checks passed after correcting the cave boundary to the verified 0x80001900..0x8000217f free region.

## Hardware gate

1. confirm CLASSIC page is visible;
2. confirm Pac-Man and Ms Pac-Man rows are visible;
3. confirm stock Cadillacs/CPS1 still behaves golden;
4. place pacman.zip in /CLASSIC/bin/;
5. launch Pac-Man from CLASSIC;
6. if gameplay starts, verify audio, controls, pause/quit, OSD and speed;
7. then test Ms Pac-Man.

If CLASSIC page is visible but launch still fails, the failure is now isolated to the native CLASSIC launcher/Test12 handoff; stock Arcade configuration is no longer in the path.
