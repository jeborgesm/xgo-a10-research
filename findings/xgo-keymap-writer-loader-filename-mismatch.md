# XGO keymap writer/loader filename mismatch

Status: **HARDWARE CONFIRMED END TO END; ONE-INSTRUCTION WRITER FIX IDENTIFIED**

## Hardware result

The first functional hidden-page mapper probe changed Player-1 physical A to logical B at runtime and the stock writer produced a 48-byte `.kmp` file:

```text
Battletoads In Battlemaniacs.kmp
```

The captured file contained the modified map in both player halves:

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

Therefore hardware proves the page-4 hook, active-buffer mutation, P1/P2 synchronization, `set_keymap()` writer path, and 48-byte filesystem write all work.

On the first relaunch the mapping reverted. The generated file was then copied/renamed manually to:

```text
Battletoads In Battlemaniacs.zsf.kmp
```

With no other change, relaunching the same game loaded the A->B mapping successfully. This hardware-confirms that the loader itself is correct and that the failure is solely the stock writer filename source.

## Writer path

At runtime `0x80354038..0x8035405c`, the stock writer constructs:

```text
format: 0x809a3418 -> "%s/save/%s.kmp"
base:   0x810a0eb0
name:   0x8109fc20
```

```asm
80354038  lui   t7,0x810a
8035403c  addiu s1,t7,-2468
80354040  lui   t6,0x809a
80354044  lui   t0,0x810a
80354048  lui   a3,0x810a
8035404c  addiu a1,t6,13336      # "%s/save/%s.kmp"
80354050  addiu a2,t0,3760       # 0x810a0eb0
80354054  addiu a3,a3,-992       # 0x8109fc20 display/base name
80354058  jal   0x802946d8
8035405c  addu  a0,s1,zero
```

For the tested game, `0x8109fc20` contains:

```text
Battletoads In Battlemaniacs
```

so stock writes:

```text
SFC/save/Battletoads In Battlemaniacs.kmp
```

## Loader path

`run_emulator()` uses the same path format but name buffer `0x8109fce8`:

```asm
8035ed5c  addiu s5,v1,-792       # 0x8109fce8
8035ed60  addiu s4,a0,3760       # 0x810a0eb0
8035ed68  addiu a1,v0,13336      # "%s/save/%s.kmp"
8035ed6c  addiu a0,sp,16
8035ed70  addu  a2,s4,zero
8035ed74  addu  a3,s5,zero
8035ed88  jal   0x802946d8
```

It opens the result with `"rb"`, reads 12 records x 4 bytes into `0x810a0f58`, and calls `set_keymap()` at `0x8035e83c`.

The same `0x8109fce8` buffer is used by the save-state path, which produces names such as:

```text
Battletoads In Battlemaniacs.zsf.sa0
```

Therefore it is the full ROM filename including extension:

```text
Battletoads In Battlemaniacs.zsf
```

and the loader correctly seeks:

```text
SFC/save/Battletoads In Battlemaniacs.zsf.kmp
```

The manual rename hardware test proves this lookup path works exactly as reconstructed.

## Exact fix

Do not modify the loader. Make the writer use the already-canonical full-ROM-filename buffer:

```text
runtime / ASD offset: 0x80354054 / 0x00354054
```

Stock:

```asm
addiu a3,a3,-992       # 0x8109fc20
```

Raw word:

```text
0x24e7fc20
```

Patched:

```asm
addiu a3,a3,-792       # 0x8109fce8
```

Raw word:

```text
0x24e7fce8
```

This is a one-instruction integration repair: after it, the writer should create the exact filename the existing loader already consumes.

## Persistent probe candidate

Combined with the already hardware-proven mapper probe, the stock-derived candidate contains four instruction edits:

```text
0x00354054  0x24e7fc20 -> 0x24e7fce8  writer uses full ROM filename
0x00354ec0  0x28700003 -> 0x28700004  expose hidden page 4
0x0035519c  0x146fff15 -> 0x546f019a  page-4 branch-likely
0x003551a0  0x97848964 -> 0xae401908  P1 physical A -> logical B
```

For the exact stock image:

```text
stock SHA-256: 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

the candidate is:

```text
LCFG CRC-32/MPEG-2: 0x3f08b86e
SHA-256: 834be40b32027bc6cf2426d9f030c51d1a9a8a0b85ce1b06293564bfa42dee25
```

Reproducibility tool:

```text
tools/patch_mapper_probe_persistent.py
```

## Architectural conclusion

The complete XGO per-ROM remapping pipeline is now hardware proven:

```text
hidden gpapi.bvs page
  -> page-4 input hook
  -> active 48-byte keymap mutation
  -> stock P1/P2 synchronization
  -> stock set_keymap()
  -> stock .kmp writer
  -> per-ROM file on SD
  -> next-launch .kmp loader
  -> stock set_keymap()
  -> restored gameplay mapping
```

The persistence subsystem does not need replacement. The only stock integration defect encountered in this path is the writer selecting the extensionless display-name buffer instead of the full ROM filename.
