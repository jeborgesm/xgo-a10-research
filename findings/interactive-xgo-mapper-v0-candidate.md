# Interactive XGO mapper v0 candidate

Status: **STATICALLY CLOSED; HARDWARE TEST PENDING**

This candidate replaces the fixed A->B proof mutation with a real two-selector mapper while preserving the already hardware-proven XGO persistence path.

## Controls

On hidden pause page 4:

```text
UP / DOWN     physical SOURCE selector
LEFT / RIGHT  logical TARGET selector
A / CONFIRM   apply selected mapping, persist .kmp, resume game
```

Both selectors start at zero whenever the pause menu is entered.

Physical source order is the confirmed XGO P1 record order:

```text
0 X
1 Y
2 L
3 A
4 B
5 R
```

Logical target order is:

```text
0 B   libretro 0
1 Y   libretro 1
2 A   libretro 8
3 X   libretro 9
4 L   libretro 10
5 R   libretro 11
```

Turbo is deliberately excluded from v0. The goal is to prove arbitrary six-button remapping before adding the GB300 edit/turbo submode.

## Hook architecture

The stock input dispatcher begins after `0x80354e84`. Candidate v0 replaces only the first dispatch branch at ASD offset `0x00354e88` with a jump to an injected handler at runtime `0x800014a0`.

The original delay-slot instruction at `0x80354e8c` remains intact, so the input event is still stored to the same stock global before the injected handler runs.

The handler first reads page state `gp-3524`. For any page other than 4 it recreates the displaced stock `v0 == 0x20` test and returns to the untouched stock dispatcher. Thus ordinary pause pages retain stock behavior.

For page 4 it consumes only the five mapper events:

```text
0x20   source +1 with wrap 0..5
0x80   source -1 with wrap 0..5
0x40   target +1 with wrap 0..5
0x10   target -1 with wrap 0..5
0x2000 or 0x0008   commit
```

The candidate reuses pause globals that stock initializes to zero and does not use for page 4:

```text
gp-3396  source selector
gp-3576  target selector
```

## Commit path

Commit computes:

```c
record = 0x810a0f58 + source * 4;
logical_id = {0,1,8,9,10,11}[target];
*record = logical_id;
```

Only the P1 record is changed. Control then jumps to the already hardware-proven stock continuation at `0x80355804`.

That path performs:

```text
P1/P2 mismatch detection
 -> P1-to-P2 synchronization
 -> set_keymap()
 -> corrected full-ROM-name .kmp writer
 -> normal resume
```

The writer filename repair remains the proven one-instruction change:

```text
0x00354054  0x24e7fc20 -> 0x24e7fce8
```

Page 4 exposure remains:

```text
0x00354ec0  0x28700003 -> 0x28700004
```

## Injected code region

The handler occupies 326 bytes including the six-byte target table:

```text
runtime 0x800014a0 .. 0x800015e5
ASD     0x000014a0 .. 0x000015e5
```

The exact stock image contains zeros across that range. Candidate generation refuses to inject unless those bytes are still zero and the exact stock SHA-256 matches.

The previously rejected `0x80004268` zero run is not used; that region has known live references.

## Labeled mapper resource

`Resources/gpapi.bvs` is a raw 640x480 RGB565 screen (`614400 = 640*480*2`). Candidate v0 uses a modified copy containing the selector orders and control legend. The firmware logic itself does not depend on the modified pixels, but the labeled screen makes the initially non-dynamic selector UI usable for hardware testing.

## Exact candidate identity

From stock SHA-256:

```text
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

the v0 firmware is:

```text
SHA-256: 092ba23cc4390c03dfd8d3fcd64a152a654c25bc5d59dde6903488a0068261d5
LCFG CRC-32/MPEG-2: 0xaf07a137
```

The labeled `gpapi.bvs` is:

```text
SHA-256: ef45f5beeb9b82d117911fdd8f4a8a76d1a32e7f4a69a84b878c79c65bc45010
size: 614400
```

## First hardware tests

Use SFC/SNES first.

Reproduce the previous proof through the real selector:

```text
source A = DOWN x3
 target B = initial target 0
confirm
```

Expected: physical A behaves as logical B and survives game restart.

Then test a non-hard-coded mapping:

```text
source B = DOWN x4
 target A = RIGHT x2
confirm
```

Expected: physical B behaves as logical A and survives game restart.

A successful second test proves the code cave, input dispatcher, both selectors, encode table, arbitrary record addressing, and stock persistence continuation. The next increment can then add dynamic visual selection and GB300-style turbo/edit mode.