# XGO Multicore watchdog / exception hook compatibility

Status: **CONFIRMED from XGO executable disassembly; no device image has been patched.**

## Headline

The three low-address hook sites used by classic/newer SF2000 Multicore are not merely present in XGO at the same numerical addresses. Their **runtime semantics match the reasons Multicore patches them**.

```text
0x800030d4  watchdog/reboot failure path
0x800495a0  general-exception infinite loop
0x80049744  IRQ-path call site used for stock-GP restoration
```

This removes another board-port uncertainty from an XGO Multicore build.

## Watchdog path at `0x800030d4`

XGO disassembly begins:

```text
0x800030d4  lui   $fp,0xdead
0x800030d8  ori   $fp,$fp,0xbead
0x800030dc  move  $23,$zero
...
```

Thus the path starts by constructing the conspicuous sentinel:

```text
$fp = 0xDEADBEAD
```

Classic SF2000 Multicore patches this exact address to jump to its watchdog diagnostic handler. The matching address and failure-marker semantics strongly establish that XGO inherited the same low-level watchdog/reboot path.

## General-exception trap at `0x800495a0`

Immediately before the site, XGO reads CP0 Cause and masks exception-code bits:

```text
0x80049580  mfc0  $26,$13
...
0x80049590  addiu $27,$zero,0x7c
0x80049594  and   $27,$27,$26
0x80049598  beqz  $27,0x800495a8
```

If those exception bits are nonzero, execution reaches:

```text
0x800495a0  b     0x800495a0
0x800495a4  nop
```

That is a literal infinite loop. Multicore replaces this exact stock dead-end with a jump to an exception diagnostic handler.

Therefore `0x800495a0` is semantically the correct XGO equivalent, not just an address inherited by coincidence.

## IRQ GP repair at `0x80049744`

XGO IRQ code contains:

```text
0x80049744  jal   <IRQ helper>
0x80049748  nop
0x8004974c  jal   <next IRQ helper>
```

The newer Multicore strategy overwrites `0x80049744/48` with the two GP-initialization instructions copied from firmware startup. This guarantees that an interrupt occurring while a dynarec core has changed `$gp` re-enters stock interrupt code using the stock firmware GP.

XGO startup contains:

```text
0x80001270  lui   $gp,0x80c3
0x80001274  addiu $gp,$gp,0x4774
```

so the runtime stock value is:

```text
$gp = 0x80c34774
```

Copying the instructions rather than hard-coding a constant is the preferred XGO port strategy.

## Porting consequence

The XGO now independently satisfies all three low-level patch assumptions used by Multicore's loader architecture:

1. watchdog failures can be redirected from `0x800030d4`;
2. general exceptions can be redirected from the dead loop at `0x800495a0`;
3. stock `$gp` can be restored in the IRQ path at `0x80049744` using XGO's own startup instructions.

For the **first controlled proof**, watchdog/exception visual diagnostics are optional. A minimal loader can avoid adding SF2000-specific LCD debug code and preserve the original handlers, while still applying the GP restoration required for dynarec safety. The diagnostic hooks can be added once the core-launch path itself is validated.

## Sources

- Preserved XGO `bios/bisrv.asd`, SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.
- `madcock/sf2000_multicore` classic loader/Makefile.
- `Trademarked69/sf2000_multicore` newer GP-restoration implementation.
