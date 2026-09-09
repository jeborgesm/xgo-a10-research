# Test34 — CLASSIC bottom label + Refresh integration

Date: 2026-09-09
Branch: `research-game-list-arcade-expansion`

## Hardware baseline

Test33/33A established the first hardware-working CLASSIC launch path:

- CLASSIC Cadillacs and Dinosaurs -> `dino.zip`: runs on hardware, with known MAME2000 lag;
- CLASSIC Pac-Man -> `pacman.zip`: freezes;
- CLASSIC Ms. Pac-Man -> `mspacman.zip`: freezes;
- stock Arcade Cadillac remains functional;
- golden Mapper/pause behavior restored;
- Test33A stretched CLASSIC artwork accepted by hardware/user.

Therefore MAME launch plumbing is now proven. Pac-Man/Ms. Pac-Man are a separate compatibility investigation.

## Bottom label

The CLASSIC game-list screenshot showed the stock bottom label area as corrupt/garbled.

The relevant stock draw call is:

```text
0x80359838  jal 0x803528a4
delay:      sw s7,24(sp)
```

It draws the stock bottom item at x=96, y=234 with the stock size/color arguments and the source pointer at stack +24.

Test34 redirects only this call through a 32-byte list-aware wrapper in the unused tail of the Test08 scanner cave.

Behavior:

- list != 11 -> tail-jump to stock draw with every argument unchanged;
- list == 11 -> replace only stack +24 with `CLASSIC`, then tail-jump to stock draw.

Thus CLASSIC uses the same stock position/style while every existing list remains byte-equivalent at the renderer interface.

## Refresh integration

Golden Test08 Refresh currently scans six inputs:

```text
scanner index 0..5
 -> list ID index+1
 -> FC, SFC, MD, GB, GBC, GBA
```

The scanner loop at `0x807db684..0x807db6b4` was extended to the sequence:

```text
0,1,2,3,4,5,10
```

Scanner index 10 maps naturally to list ID 11.

A tiny helper changes the default scanner folder:

- index 5 -> existing `%s/GBA`;
- index 10 -> new `%s/CLASSIC`.

A relocated 11-row extension-rule table preserves the six existing rules and defines:

```text
index 10 -> [7, 255, 0, 0]
```

Classifier ID 7 is `.zfb`. The inverted native range rejects all non-ZFB files.

Therefore Refresh now:

- scans `/CLASSIC`;
- ignores `/CLASSIC/bin` through the existing directory-skip behavior;
- imports new `.zfb` wrappers only;
- uses the existing stable merge;
- rewrites synchronized `clm.tax / clm.nec / clm.bvs`;
- invalidates list 11's cached count;
- uses the existing `Games Updated / No New Games / Refresh Failed` status path.

Stock Arcade lists 7-10 are still not scanned or rewritten.

## Memory safety

New Test34 data/code lives only in the previously unused tail of the Test08 scanner cave:

```text
0x807db9e0  11-row scanner rule table (44 bytes)
0x807dba0c  "%s/CLASSIC"
0x807dba18  "CLASSIC"
0x807dba20  folder helper
0x807dba48  loop helper
0x807dba64  label wrapper
```

Helper blob size: 104 bytes.

Protected byte ranges remain unchanged from hardware-working Test33A:

- actual relocated Test12 loader `0x80001900..0x80001e83`;
- Mapper v19 `0x800014a0..0x800018fd`;
- native SNES loader `0x80002230..0x8000277f`;
- Audio OSD `0x80002780..`;
- golden `run_emulator()`;
- exact Test12 MAME2000 core;
- accepted stretched CLASSIC artwork.

## Candidate

```text
xgo-classic-test34-label-refresh.zip
size        7,537,711 bytes
SHA-256     cbacb517f5dfbb092963750b88d4caf7da499a0ee508e394709013990ee3b352
firmware    4e8faa2531b958988bac4497bf2e7e04f95349b3ba8debef77b95c5a943dca0f
loader      e38af97eabb454dbcc8dd8b1823b6f82b8878d7993c0eb7a120d26c6da767d4e
core        abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
art         4ff7b3e0bd88acb96e3a915264fdbaee14209175a5331e8a422764664e07a843
```

## Hardware closeout gate

1. Boot.
2. Verify Contra pause/Mapper remains normal.
3. Verify stock Arcade Cadillac remains normal.
4. Verify CLASSIC Cadillac still launches.
5. Verify bottom list label now reads CLASSIC and no garbled strip remains.
6. Run Refresh with no content changes; expect normal status and no list corruption.
7. Reboot and verify CLASSIC still contains the three current entries.

After hardware PASS, merge `research-game-list-arcade-expansion` to `main`, promote Test34 as the branch checkpoint, and open a new Pac-Man compatibility branch.
