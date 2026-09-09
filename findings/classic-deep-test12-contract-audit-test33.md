# CLASSIC deep Test12 contract audit and Test33 exact-machine-loader candidate

Date: 2026-09-09
Branch: `research-game-list-arcade-expansion`

## Why this audit was necessary

Test32 restored all protected golden behavior on physical hardware:

- boot PASS;
- Contra PASS;
- normal pause Resume/Quit/Load/Save PASS;
- Mapper no longer leaked into the pause menu;
- stock Arcade Cadillacs PASS.

But every CLASSIC title still immediately returned to the CLASSIC list:

- Cadillacs and Dinosaurs / `dino.zip` FAIL;
- Pac-Man / `pacman.zip` FAIL;
- Ms Pac-Man / `mspacman.zip` FAIL.

Because `dino.zip` is already hardware-proven under the older XGO MAME2000 path, the ROM/core-compatibility hypothesis is insufficient. The launch contract itself had to be reconciled byte-by-byte with hardware-working Test12.

## Correction: what caused the Mapper regression in Tests28-31

Earlier analysis blamed the CLASSIC launcher at `0x80001900` for overwriting Mapper v19.

The exact Test08 binary disproves that statement.

A full zero-run scan of exact golden Test08 shows:

```text
0x800018fe..0x8000217f
2178 zero bytes
```

Therefore code beginning at `0x80001900` was inside a genuinely zero region.

The actual unsafe addition was the CLASSIC metadata/art filename string block beginning at:

```text
0x800018d0
```

which begins 46 bytes before the proven-zero boundary and therefore overlapped active pre-existing low-memory state/code.

Test32 moved all CLASSIC resource-name strings out of that region. Physical hardware then confirmed the Contra pause/Mapper regression disappeared.

This correction supersedes the earlier claim that all of `0x80001900..0x8000217f` was Mapper-owned.

## Browser call contract — direct machine-code proof

Both normal browser launch sites are unchanged in golden Test08:

```text
0x80357384 jal run_game @ 0x80360b88
0x80359064 jal run_game @ 0x80360b88
```

Immediately before each call:

```text
a0 = s7
a1 = selected load/index state
```

and `s7` has just been produced by stock `sprintf` using:

```text
format   "%s/%s"
0x809a3674 -> 0x810a0eb0  current system directory
0x809a3680 -> 0x8109fce8  current game name
```

Thus the browser already passes the complete selected wrapper path to `run_game()`.

## Critical Test12 dependency: stock run_game preload

Exact Test08 and hardware-working Test12 were compared across:

```text
0x80360940..0x80360b88 helper block
0x80360b88..0x80360df8 run_game pre-loader path
0x8036b500..0x8036b650 setup/callback path
```

Result:

```text
helpers              diff bytes = 0
pre-loader setup     diff bytes = 0
run_game pre-loader  diff bytes = 0
```

Hardware-working Test12 therefore relied on the completely stock `run_game()` preparation sequence.

Before the Test12 loader is called at `0x80360df8`, stock firmware has already:

1. classified the selected extension/system family;
2. opened/read the selected wrapper;
3. populated `gp_buf_64m @ 0x80c33ad8`;
4. populated `g_run_file_size @ 0x80c33a7c`;
5. executed the stock packaged-content/Arcade preprocessing;
6. resolved/mutated the selected archive-name state;
7. set the Arcade family bit `0x40`;
8. registered the ordinary pre-loader UI callback through `0x8036b558`;
9. only then called the external Test12 loader.

Test32 bypassed this entire block.

## Hidden dependency inside the exact Test12 core

The exact Test12 core is linked with:

`tools/multicore/xgo_preloaded_rom_sbrk.c`

Its private newlib heap is initialized from:

```text
gp_buf_64m + align64(g_run_file_size)
```

with an upper clamp below `0x87000000`.

Therefore the exact Test12 core was built around the assumption that stock `run_game()` has already populated the preload arena and run-file-size global.

Test32's direct CLASSIC launcher skipped the very memory contract the core's libc uses.

## Complete firmware differential: Test12 vs golden Test08

A full byte comparison was performed, not selected-window sampling.

Exact inputs:

```text
Test08 firmware
45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444

Test12 firmware
16233cbb0d7b7e5a90d72a0eed04b873a3754bcdbaaedcea64fc1b3b972e3f1f
```

Result:

```text
changed bytes  4114
changed runs   837
```

The differences classify into:

- CRC;
- low Test12 loader vs later golden OSD bytes;
- Test12 vs later golden `run_emulator()`;
- final Arcade MAME hook;
- later Refresh/scanner code;
- later Refresh-menu geometry/TV-mode changes;
- later Audio OSD screen-write/volume-event hooks.

The previously "unclassified" 85 bytes were mapped back to known post-Test12 Refresh/OSD UI patches such as:

```text
0x80359aa4 / 0x80359e60  Refresh menu option bounds
0x80359b..                  Refresh menu render geometry
0x8035ac98..                TV-mode menu geometry
0x8035c458                  Audio OSD screen-write hook
0x8035d6a8 / 0x8035d6c0    Audio OSD volume-event/repaint hooks
```

No additional hidden MAME-support patch was found elsewhere in firmware.

Test20 had already restored the Test12 `run_emulator()` body and still failed, so the later golden `run_emulator()` is not the missing pre-entry dependency.

## Major finding: the repository loader source was not the exact Test12 machine loader

The loader source at commit:

```text
3470f0e320f47fb7deef5f64f7c0346b21adb4e8
```

was recompiled at its original Test12 address `0x80002780`.

Result:

```text
rebuilt size       1373 bytes
different bytes     918
```

Therefore the source is semantically related historical source, but it is NOT a byte reproduction of the loader that actually ran in hardware Test12.

This invalidates earlier wording that Test26 used the "exact historical loader."

## Exact Test12 loader extraction

The actual Test12 loader machine image was extracted directly from the hardware-working firmware:

```text
source range
0x80002780..0x80002d03

size
1412 bytes

SHA-256
42f7638f9d0d9d89272eb06e880c777c65ce183900a8eee037cc561dccea4cb1
```

Direct disassembly confirms the actual binary contains the expected hardware-working contract:

- list gate;
- heap-break guard;
- exact historical core pathname;
- XGOC header and CRC validation;
- stock sound-task shutdown;
- `RAMSIZE = 0x87000000`;
- core copy to `0x87000000`;
- payload CRC/BSS;
- IRQ-GP repair;
- cache maintenance;
- external entry call;
- RAMSIZE restore;
- XGO1 continuity fallback.

## Test33 relocation

Rather than recompiling the source again, Test33 mechanically relocates the ACTUAL Test12 machine image.

Original:

```text
0x80002780..0x80002d03
```

Test33:

```text
0x80001900..0x80001e83
```

This lies wholly inside the exact-golden proven-zero range.

Relocation changes only:

1. eight internal direct J/JAL targets;
2. the two internal references to the embedded core pathname / `"rb"` strings;
3. the historical list gate immediate `7 -> 11`.

All other bytes remain the actual Test12 machine code.

Relocated-loader SHA-256:

```text
e38af97eabb454dbcc8dd8b1823b6f82b8878d7993c0eb7a120d26c6da767d4e
```

## Test33 architecture

This is the first candidate combining BOTH requirements that had previously been separated:

```text
first-class CLASSIC list 11
        +
complete stock run_game preload
        +
actual Test12 loader machine code
        +
exact Test12 MAME2000 core
```

Launch:

```text
CLASSIC browser
 -> untouched stock browser call
 -> untouched stock run_game()
 -> stock ZFB preload into gp_buf_64m
 -> g_run_file_size populated
 -> stock family/package preparation
 -> stock pre-loader callback registration
 -> 0x80360df8
 -> actual Test12 machine loader, relocated, gate=11
 -> exact Test12 MAME2000 core
 -> golden run_emulator()
```

Lists 7-10 enter the same relocated loader but fail the list-11 gate and immediately call untouched stock `run_fba()`, preserving stock Arcade behavior.

There are NO browser-run_game hooks in Test33.

## Golden protection assertions

CI confirms these remain byte-identical to golden Test08:

- Mapper v19 region before the proven-zero boundary;
- native SNES loader;
- Audio OSD low-memory region;
- active Refresh scanner code;
- golden `run_emulator()`;
- both stock browser `run_game()` calls.

CLASSIC resource-name strings are stored only in the verified unused tail of the Test08 scanner cave.

## Exact Test33 firmware payload

Private CI run:

```text
34312130930
artifact 10088750278
```

Firmware:

```text
SHA-256
80c851925990a04c35c9f7cc568f410f93c82d671f50b471ebd4f2c85f3c9a55
```

Exact Test12 core:

```text
abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

Final hardware package composed with existing CLASSIC catalogs/wrappers and a content-only squashed platform-art resource:

```text
xgo-classic-test33-exact-test12-preload.zip
size        7,528,733 bytes
SHA-256     092c7af7f31efe5c408cf16f674ac106c3483d55f3540cecdaa79dda1289061e
```

## Hardware gate

One baseline first:

```text
/CLASSIC/bin/dino.zip
```

Launch **Cadillacs and Dinosaurs from CLASSIC**.

Before doing that, verify Contra pause/Mapper remains normal and stock Arcade Cadillac remains normal.

If CLASSIC Cadillac reaches gameplay, the first-class CLASSIC -> Test12 contract is finally closed and Pac-Man/Ms Pac-Man become the next compatibility targets.

If CLASSIC Cadillac still fails, do not create a blind Test34. The next analysis must use the actual Test12 loader entry state and/or a RAM-only/non-boot-invasive entry marker while retaining this full stock preload path.
