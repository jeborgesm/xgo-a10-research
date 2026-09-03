# XGO keymap writer/loader filename mismatch

Status: **HARDWARE CONFIRMED PERSISTENCE; STATIC ROOT CAUSE IDENTIFIED**

## Hardware observation

The first functional hidden-page mapper probe successfully changed Player-1 physical A to logical B at runtime. The change persisted to disk as a 48-byte `.kmp` file, but relaunching the same game restored the stock mapping.

The hardware-created file was:

```text
Battletoads In Battlemaniacs.kmp
```

Its exact contents were:

```text
0A 00 00 00
0B 00 00 00
09 00 00 00
00 00 00 00
00 00 00 00
01 00 00 00
0A 00 00 00
0B 00 00 00
09 00 00 00
00 00 00 00
00 00 00 00
01 00 00 00
```

This proves:

- the page-4 hook changed the live keymap buffer;
- the stock writer saw the P1/P2 mismatch;
- the stock P2 synchronization ran;
- `set_keymap()` ran through the writer path;
- a 48-byte per-ROM `.kmp` was actually written.

The remaining failure is therefore exclusively in the next-launch lookup path.

## Writer path

At runtime `0x80354038..0x8035405c`, the stock writer constructs the path using:

```text
format: 0x809a3418 -> "%s/save/%s.kmp"
base:   0x810a0eb0
name:   0x8109fc20
```

Representative instructions:

```asm
80354038  lui   t7,0x810a
8035403c  addiu s1,t7,-2468
80354040  lui   t6,0x809a
80354044  lui   t0,0x810a
80354048  lui   a3,0x810a
8035404c  addiu a1,t6,13336      # 0x809a3418 = "%s/save/%s.kmp"
80354050  addiu a2,t0,3760       # 0x810a0eb0
80354054  addiu a3,a3,-992       # 0x8109fc20
80354058  jal   0x802946d8
8035405c  addu  a0,s1,zero
```

The hardware-created filename shows that `0x8109fc20` contains the display/base game name without the ROM extension for this title:

```text
Battletoads In Battlemaniacs
```

## Loader path

At runtime `0x8035ed48..0x8035ed9c`, `run_emulator()` constructs the `.kmp` lookup path with the same format string but a different name buffer:

```text
format: 0x809a3418 -> "%s/save/%s.kmp"
base:   0x810a0eb0
name:   0x8109fce8
```

Representative instructions:

```asm
8035ed48  addiu sp,sp,-304
8035ed4c  lui   v1,0x810a
8035ed50  lui   a0,0x810a
8035ed5c  addiu s5,v1,-792       # 0x8109fce8
8035ed60  addiu s4,a0,3760       # 0x810a0eb0
8035ed64  lui   v0,0x809a
8035ed68  addiu a1,v0,13336      # 0x809a3418 = "%s/save/%s.kmp"
8035ed6c  addiu a0,sp,16
8035ed70  addu  a2,s4,zero
8035ed74  addu  a3,s5,zero
8035ed88  jal   0x802946d8
```

It then opens the constructed path with `"rb"`, reads exactly 12 records of 4 bytes into `0x810a0f58`, closes the file, and calls `set_keymap()`:

```asm
8035ed90  lui   a1,0x809a
8035ed94  addiu a1,a1,32056      # "rb"
8035ed98  jal   0x802b3524       # fopen-like
8035eda0  addu  s0,v0,zero
8035edac  lui   a2,0x810a
8035edb0  addiu s2,a2,3928       # 0x810a0f58
8035edb4  addu  a0,s2,zero
8035edb8  li    a1,4
8035edbc  li    a2,12
8035edc0  jal   0x802b3698       # fread-like
...
8035edd8  jal   0x8035e83c       # set_keymap()
8035eddc  li    a1,8
```

## Why `0x8109fce8` is the full ROM filename

The same `0x8109fce8` buffer is used by the stock save-state path with:

```text
%s/save/%s.sa%d
```

The preserved test-card file listing contains:

```text
SFC/Battletoads In Battlemaniacs.zsf
SFC/save/Battletoads In Battlemaniacs.zsf.sa0
```

Therefore `0x8109fce8` is the ROM filename including its XGO extension:

```text
Battletoads In Battlemaniacs.zsf
```

while the writer uses the extensionless display/base name at `0x8109fc20`.

## Exact mismatch

For this game the stock writer creates:

```text
SFC/save/Battletoads In Battlemaniacs.kmp
```

but the stock loader looks for:

```text
SFC/save/Battletoads In Battlemaniacs.zsf.kmp
```

This explains the hardware result exactly:

```text
page-4 mapper mutation
  -> writer succeeds
  -> extensionless .kmp created
  -> game closes
  -> next launch constructs extension-bearing .kmp path
  -> file not found
  -> embedded/default keymap remains active
```

## Immediate no-firmware-change test

Copy the hardware-generated file:

```text
Battletoads In Battlemaniacs.kmp
```

to:

```text
Battletoads In Battlemaniacs.zsf.kmp
```

in the same `SFC/save/` directory, preserving the original file as well.

If relaunch then restores physical A -> logical B, the filename mismatch is hardware-confirmed end to end.

## Architectural consequence

The mapper write architecture is now closed. A complete on-device editor does not need a new persistence format or filesystem implementation. It only needs either:

1. a tiny writer fix so the stock writer uses the same full ROM-name buffer as the loader, or
2. a loader fix so it uses the writer's extensionless display-name buffer.

The second option is potentially the smaller compatibility patch because existing hardware-created `.kmp` files already use the writer convention.
