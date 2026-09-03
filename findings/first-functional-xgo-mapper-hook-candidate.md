# First functional XGO mapper hook candidate

## Status

**STATICALLY CLOSED; HARDWARE TEST PENDING.**

This is the first deliberately minimal functional bridge between XGO's hardware-proven hidden `gpapi.bvs` pause page and the stock per-game keymap compiler/writer.

It is not a full editor. The candidate performs one fixed, unmistakable mapping mutation on hidden page 4 and reuses XGO's existing persistence path end to end.

## Why no injected code cave is needed

The pause confirm/action dispatcher is entered on input event `0x2000` and tests the active menu state at runtime `0x80355180`:

```asm
80355180  lw    v1,-3524(gp)
80355184  beq   v1,zero,0x80355804   # state 0
8035518c  beq   v1,t0,0x8035588c    # state 1
80355194  beq   v1,t1,0x803558c8    # state 2
80355198  li    t7,3
8035519c  bne   v1,t7,0x80354df4    # all non-3 states fall back
803551a0  lhu   a0,-30364(gp)       # delay slot
# state 3 handler follows
```

The already-hardware-proven navigation patch allows state `4`, but stock state 4 currently takes the final `bne` fallback.

Instead of introducing a trampoline, change the final branch to a **branch-likely** that redirects non-3 states to the existing state-0 writer/resume path:

```asm
# stock
8035519c  bne   v1,t7,0x80354df4
803551a0  lhu   a0,-30364(gp)

# probe
8035519c  bnel  v1,t7,0x80355808
803551a0  sw    zero,0x1908(s2)
```

Raw words:

```text
0x0035519c: 146f ff15 -> 546f 019a
0x003551a0: 9784 8964 -> ae40 1908
```

The stock firmware already uses MIPS branch-likely instructions elsewhere, so this is not introducing an ISA form absent from the image.

## Why state 3 remains untouched

For `v1 == 3`, `bnel` is **not taken** and MIPS branch-likely semantics annul the delay-slot instruction.

Therefore:

```text
state 3 -> patched store does not execute -> stock state-3 body continues
```

For hidden state 4:

```text
state 4 -> branch is taken -> delay-slot store executes -> jump to stock writer path
```

This conditional-delay-slot property is what makes the probe possible without a code cave.

## Exact fixed mutation

At pause-function entry, register `s2` is established as:

```text
s2 = 0x8109f65c
```

The active 48-byte per-game keymap buffer is:

```text
0x810a0f58
```

For ordinary systems the physical record order is:

```text
0 X
1 Y
2 L
3 A
4 B
5 R
```

Thus Player-1 physical A is record 3:

```text
0x810a0f58 + 3*4 = 0x810a0f64
```

and:

```text
0x810a0f64 - 0x8109f65c = 0x1908
```

So the taken branch delay slot:

```asm
sw zero,0x1908(s2)
```

writes record value `0x00000000` to Player-1 physical A.

Under XGO's confirmed keymap ABI:

```text
low 16 bits = libretro logical target ID
bit 16      = turbo
```

logical ID `0` is libretro `B`.

Therefore the probe deliberately changes:

```text
physical A -> logical B
```

For the first hardware test, use an SFC/SNES game so both the physical-record interpretation and visible A/B behavior are maximally unambiguous.

## Why only Player 1 is changed before calling the writer

This is intentional.

XGO's stock writer at `0x80353fac` writes a `.kmp` only after detecting a mismatch between corresponding P1/P2 records. When it finds one, it:

1. copies the P1 record into the corresponding P2 record using the stock permutation;
2. calls `set_keymap()` at `0x8035e83c`;
3. constructs `%s/save/%s.kmp`;
4. writes the 48-byte mapping;
5. closes the file.

If the probe mirrored P2 itself before invoking the writer, the writer could see no mismatch and return without persisting anything.

So the one-sided mutation is precisely what triggers the existing stock save machinery.

## Reused stock continuation

The branch target is runtime:

```text
0x80355808
```

which is an existing call site:

```asm
80355808  jal   0x80353fac
8035580c  sw    s6,-24424(gp)
```

The code after this is the normal state-0 writer/resume continuation. Therefore the expected page-4 confirm behavior is:

```text
hidden mapper page
  -> fixed P1 A->B mutation
  -> stock .kmp writer detects mismatch
  -> stock P2 mirroring
  -> stock set_keymap()
  -> stock per-ROM .kmp persistence
  -> normal resume path
```

No new filesystem code, compiler, runtime keymap representation, or executable code region is introduced.

## Complete firmware changes

The hardware candidate needs only three instruction changes from exact stock firmware:

```text
0x00354ec0  0x28700003 -> 0x28700004
             expose menu state 4 (already hardware-proven independently)

0x0035519c  0x146fff15 -> 0x546f019a
             state-4 branch-likely -> existing writer/resume path

0x003551a0  0x97848964 -> 0xae401908
             taken-only delay slot: P1 physical A -> logical B
```

The LCFG payload is then resealed with CRC-32/MPEG-2.

For exact stock SHA-256:

```text
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

the generated candidate is:

```text
LCFG payload CRC: 0xbfc64d81
SHA-256: 5052d6c61cae6d9cc94c7ebce37c085c360ca6eb00c341283f5a64cc4ee38262
```

## Reproducibility

The branch contains:

```text
tools/patch_mapper_probe_a_to_b.py
```

The patcher accepts only the exact known stock SHA, validates the stock CRC and original instruction words, performs the three edits, reseals the LCFG payload, and refuses in-place modification.

## Hardware test protocol

Use an SFC/SNES ROM on a backed-up/test SD card.

1. Boot the candidate firmware.
2. Launch the SNES game and verify physical A and B normally behave distinctly before invoking the mapper.
3. Open Select+Start pause menu.
4. Navigate to the hardware-proven hidden fifth controller screen.
5. Press confirm once.
6. Expected immediate result: the menu follows the normal resume path.
7. In game, physical A should now produce logical B.
8. Confirm that a per-ROM `.kmp` exists/changes under the normal save directory.
9. Reboot/relaunch the same ROM and verify the mapping survives, proving persistence.
10. Remove the generated `.kmp` (or restore the test-card save directory) to return to the embedded default.

## Success criterion

A successful hardware run closes the complete chain:

```text
hidden XGO mapper shell
  -> page-4 confirm hook
  -> active 48-byte keymap mutation
  -> stock P1/P2 mirroring policy
  -> stock set_keymap()
  -> stock per-game .kmp writer
  -> persisted changed gameplay mapping
```

At that point the remaining work is UI behavior, not mapping architecture.
