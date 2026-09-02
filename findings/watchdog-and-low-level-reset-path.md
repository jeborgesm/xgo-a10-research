# XGO watchdog and low-level reset path

Status: **low-level executable reset path confirmed; exact semantic meaning of one SRAM marker remains open**.

## Headline

The XGO firmware contains a low-level reboot path that exits the normal SD-loaded application environment and jumps directly to:

```text
0xAFC00000
```

after disabling interrupts and resetting/clearing multiple hardware-control registers.

This is important for custom-code experiments because reboot behavior is implemented below the normal frontend/emulator layer rather than depending on a clean return through the UI.

## Primary reset routine

The sequence beginning around `0x80003000`:

1. performs preliminary low-level setup;
2. writes a SoC-specific control value through the `0xb880...` / alternate `0xb882e000...` register base selected by chip ID;
3. clears the global interrupt-enable bit in CP0 Status;
4. clears interrupt/control registers at `0xb8800038/3c` and `0xb8840038/3c`;
5. clears/reprograms several control registers in the `0xb88000xx` region;
6. clears bit 0 at `0xb8800223`;
7. executes a short settling loop;
8. jumps to:

```text
0xAFC00000
```

via:

```text
lui  $v0,0xafc0
jr   $v0
nop
```

The function therefore does not simply restart the XGO application in place; it transfers execution back to a lower boot/reset-side address space.

## Watchdog reboot path

The routine beginning at:

```text
0x800030d4
```

starts with the diagnostic sentinel:

```text
$fp = 0xDEADBEAD
```

then invokes additional low-level helpers before calling the reset sequence at `0x80003000`.

Classic SF2000 Multicore patches this same `0x800030d4` site to redirect watchdog failure into a diagnostic hook. Its presence and surrounding semantics on XGO confirm that the corresponding patch location is not an accidental same-address byte pattern.

## Alternate reset-side path

A neighboring low-level path around `0x800031c4` loads:

```text
$fp = 0xDEADBEEF
```

preserves arguments in registers, clears the same SoC control bit, performs low-level setup, and eventually jumps to:

```text
0xAFC00000
```

as well.

The two `DEADBEAD` / `DEADBEEF` values are therefore deliberate diagnostic/state markers associated with distinct reset-entry paths.

## `SRAM` reset marker

Immediately before entering another portion of the reset sequence, firmware writes four ASCII bytes to:

```text
0xB8853FFC
```

as:

```text
53 52 41 4D
 S  R  A  M
```

The executable writes the bytes individually at offsets `+0..+3`.

This is clearly intentional low-level state communication, but the receiving boot-stage consumer has not yet been recovered from the SD application image. The safest interpretation is therefore:

**CONFIRMED:** the XGO writes an `SRAM` marker at `0xB8853FFC` as part of a low-level restart path.

**OPEN:** whether the boot ROM/bootloader uses it to select SRAM execution, recovery behavior, or another restart mode.

## Relevance to experimental firmware

This result improves the recoverability model for SD-only code experiments:

```text
external/stock application execution
        -> watchdog/reset machinery
        -> low-level peripheral reset
        -> jump 0xAFC00000
        -> boot-side code
```

It does **not** mean every malformed injected program can recover automatically. Code that disables the relevant exception/watchdog machinery or wedges the CPU before the reset path can run may still require a power cycle.

It does show that the stock XGO contains a real board-level reboot mechanism independent of the normal frontend and that upstream Multicore's watchdog-hook location is semantically valid on this firmware.

## Related confirmed addresses

```text
watchdog/reset hook site     0x800030d4
primary low-level reset      0x80003000
alternate reset path         ~0x80003148 / 0x800031c4
boot-side transfer address   0xAFC00000
SRAM marker                  0xB8853FFC
watchdog sentinel            0xDEADBEAD
alternate sentinel           0xDEADBEEF
```
