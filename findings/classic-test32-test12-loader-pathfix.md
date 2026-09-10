# Test32 — Test12-derived CLASSIC loader with path discriminator fix

Date: 2026-09-08
Branch: research-game-list-arcade-expansion

## Hardware result leading here

Test31:
- device boots;
- CLASSIC page visible;
- Pac-Man, Ms Pac-Man, Cadillacs and Dinosaurs all visible;
- all three immediately return to game list after Loading;
- known-good dino.zip also fails from CLASSIC.

This proves the problem is CLASSIC -> MAME plumbing, not Pac-Man ROM compatibility.

## Concrete Test29/31 flaw

The CLASSIC launcher path discriminator required the browser-supplied filename to contain:

/CLASSIC/

That misses the valid stock-browser form:

CLASSIC/<game>.zfb

If that form is passed, the launcher falls directly to untouched stock run_game(), explaining Loading -> immediate return for every CLASSIC entry, including dino.zip.

## Test32 launcher

Test32 accepts both:

CLASSIC/<game>.zfb
/.../CLASSIC/<game>.zfb

For non-CLASSIC paths:
-> untouched stock run_game @ 0x80360b88.

For CLASSIC:
1. open selected wrapper directly;
2. seek to proven embedded ZIP-name offset 59908;
3. read ZIP basename;
4. set system directory global 0x810a0eb0 = /mnt/sda1/CLASSIC;
5. set game/archive-name global 0x8109fce8 = embedded ZIP basename;
6. execute the historical Test12 external-core sequence:
   - XGOC header validation;
   - payload/header CRC validation;
   - stock sound-task stop;
   - RAMSIZE ceiling;
   - upper-RAM payload copy;
   - BSS zero;
   - historical IRQ-GP repair;
   - full cache flush;
   - entry(filename, load_state).
7. exact archived Test12 MAME2000 frontend/core then owns callbacks and stock run_emulator().

The loader occupies only the already-used verified CLASSIC cave 0x80001900..0x8000217f. No new memory regions or trace helpers.

## Artwork

The full user-selected CLASSIC panel is intentionally stretched to 600x330 and centered at x=20, y=75 inside the native 640x480 RGB565 screen. This sacrifices aspect ratio so both title and bottom border remain visible between stock UI overlays.

## Exact candidate

xgo-classic-test32-test12-loader-pathfix-artfit.zip
size              7,535,429 bytes
ZIP SHA-256        3e8d7b1dfafd029120556ea5d65e06130bb3e0e7dd9b69759b712b533c42b08a
firmware SHA-256   235636d86ca86c915b2a78905392e9f2606a04392c51fc0114126154cbf65448
loader size        2,051 bytes
loader SHA-256     5aa159b1dc6bd05fcb18c8f3310818acd6c25d82d783bcd84cd0bc1b6cc15fc3
art SHA-256        f6ee3f75eafcdee6d5f61a64a7a8f709107eb8b1d93fefe694619e319937dd20
Test12 core SHA    abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461

## Hardware order

1. confirm boot;
2. confirm CLASSIC page/art fit;
3. launch Cadillacs and Dinosaurs first;
4. if Cadillac works, launch Pac-Man/Ms Pac-Man;
5. if Cadillac still immediately returns, path-discriminator failure is ruled out and the next seam is the browser call ABI / filename pointer itself.
