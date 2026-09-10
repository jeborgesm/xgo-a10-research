# CLASSIC deep Test12 contract recovery and Test33 exact-loader candidate

Date: 2026-09-09
Branch: research-game-list-arcade-expansion

## Why Tests 28-32 failed to launch CLASSIC games

The deep binary/source comparison closed multiple hidden differences between the hardware-working MAME2000 Test12 path and the later CLASSIC path.

### 1. Test32 intercepted too early

Exact browser disassembly shows both normal launch sites call:

```text
0x80357384  jal run_game
              a0 = s7  # full selected wrapper path
0x80359064  jal run_game
              a0 = s7
```

Test32 intercepted these browser-level calls and therefore bypassed the complete stock `run_game()` preparation path.

### 2. Test12 depended on stock preload state

Exact `run_game()` machine code confirms the common preload sequence:

```text
open(selected wrapper)
seek/tell selected file size
store g_run_file_size
rewind
read into gp_buf_64m
close
dispatch by system family
```

The hardware-working Test12 MAME core links `xgo_preloaded_rom_sbrk.c`.

That allocator explicitly requires:

```text
gp_buf_64m      = 0x80c33ad8
g_run_file_size = 0x80c33a7c
```

and creates external newlib heap space only after the stock-preloaded prefix.

Therefore bypassing `run_game()` removes a real runtime dependency of the exact Test12 core.

### 3. Test12 entered at the final FBA seam

Exact Test12 machine code:

```text
0x80360df4  move a0,s2
0x80360df8  jal 0x80002780   # hardware-working Test12 loader
0x80360dfc  move a1,zero
```

So the proven loader receives:

- original wrapper filename/path in `a0`;
- `load_state = 0`;
- only after stock wrapper preload/state preparation.

### 4. Historical source is not the exact Test12 loader binary

A rebuild of historical loader source at the original address produced:

```text
rebuilt size      1373
different bytes   918
```

against the actual hardware-working Test12 firmware slice.

Therefore the machine bytes in the hardware-tested Test12 firmware are authoritative.

### 5. Corrected low-memory collision diagnosis

Exact Test12-vs-golden binary comparison proves:

```text
Mapper active      0x800014a0..0x800018fd
golden zero/free   0x800018fe..0x8000217f
SNES loader        0x80002230..0x8000277f
Audio OSD          0x80002780..
```

The CLASSIC launcher at `0x80001900` did NOT overlap Mapper.

The Mapper/pause regression came from CLASSIC metadata/art strings and a launch flag that earlier builds placed at `0x800018d0..0x800018f0`, which does overlap Mapper v19.

Test32 restored Mapper because those writes were removed.

## Actual Test12 loader relocation

The exact hardware-working Test12 machine loader was extracted as:

```text
source    0x80002780..0x80002d03
size      1412 bytes
SHA-256   42f7638f9d0d9d89272eb06e880c777c65ce183900a8eee037cc561dccea4cb1
```

It was relocated to:

```text
0x80001900..0x80001e83
```

Only required transformations were made:

1. list gate immediate `7 -> 11`;
2. eight direct internal J/JAL targets relocated by the address delta;
3. two internal data-pointer low halves relocated for the core pathname and `rb` string.

Relocated loader:

```text
SHA-256 e38af97eabb454dbcc8dd8b1823b6f82b8878d7993c0eb7a120d26c6da767d4e
```

No direct J/JAL remains pointed at the historical Audio-OSD-owned loader region.

## Test33 architecture

Test33 restores the exact successful ownership sequence:

```text
CLASSIC browser
 -> untouched stock run_game()
 -> stock wrapper parse/preload
 -> gp_buf_64m + g_run_file_size established
 -> stock system-family state
 -> final FBA dispatch @ 0x80360df8
 -> relocated actual Test12 machine loader
 -> exact Test12 MAME2000 core
 -> golden run_emulator()
```

Real Arcade lists still hit the same hook, but the relocated loader's gate is list 11, so non-CLASSIC Arcade families fall through to stock FBA.

CLASSIC remains first-class at the UI/content layer:

```text
/CLASSIC/Pac-Man.zfb
/CLASSIC/Ms Pac-Man.zfb
/CLASSIC/Cadillacs and Dinosaurs.zfb

/CLASSIC/bin/pacman.zip
/CLASSIC/bin/mspacman.zip
/CLASSIC/bin/dino.zip
```

Metadata/art names live only in the verified unused tail of the Test08 scanner cave.

Protected byte ranges are preserved:

- Mapper v19;
- native SNES loader;
- Audio OSD;
- active Test08 scanner;
- golden `run_emulator()`;
- both browser `run_game()` call sites.

## Exact full Test33 package

```text
xgo-classic-test33-exact-test12-loader-full.zip
size              7,549,340 bytes
ZIP SHA-256        94d269201d59e42554dd80f547faa89262103b84c9fe80332666d258733867c4
firmware SHA-256   80c851925990a04c35c9f7cc568f410f93c82d671f50b471ebd4f2c85f3c9a55
core SHA-256       abf8e4ec6eb7c6d4c2162076e8faa868954a3663b8210c820e1267857b345461
```

The CLASSIC artwork/content layer is inherited from the hardware-safe Test32 package.

## Remaining uncertainty

Golden Test08's `run_emulator()` differs from historical Test12 by 150 bytes because of later Audio OSD and scheduler work.

This is not yet proven incompatible with MAME2000. Previous attempts to test the old runner were confounded by broken CLASSIC/list11 plumbing.

Test33 deliberately fixes the loader/preload contract first while retaining golden `run_emulator()` to avoid regressing proven OSD/scheduler behavior.

Hardware order:

1. Boot.
2. Contra pause/Mapper.
3. stock Arcade Cadillac.
4. CLASSIC Cadillac (`dino.zip`) — decisive MAME baseline.
5. only after CLASSIC Cadillac reaches gameplay, Pac-Man / Ms Pac-Man.
