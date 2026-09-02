# XGO startup stack canary and exception-path corruption guard

Status: **confirmed executable behavior**.

## Headline

The startup marker previously observed as `0xABCDEF12` is an active stack-corruption canary.

The XGO startup code writes:

```text
0x8000125c  lui   $t0,0x80f9
0x80001260  addiu $t0,$t0,-0x7c50
0x80001264  lui   $t1,0xabcd
0x80001268  ori   $t1,$t1,0xef12
0x8000126c  sw    $t1,0($t0)
```

which resolves to:

```text
address = 0x80f883b0
value   = 0xabcdef12
```

## Exception handler checks the canary

The general exception path later executes:

```text
0x800496b4  lui   $k1,0x80f9
0x800496b8  addiu $k1,$k1,-0x7c50
0x800496bc  lw    $k1,0($k1)
0x800496c0  lui   $k0,0xabcd
0x800496c4  ori   $k0,$k0,0xef12
0x800496c8  beq   $k1,$k0,0x800496d4
0x800496cc  nop
0x800496d0  sdbbp
```

Therefore any exception that reaches this path verifies that the word at `0x80f883b0` still contains the startup sentinel. If the value differs, firmware executes the MIPS software-debug-break instruction `sdbbp`.

This establishes the marker as a live corruption guard, not an unused SDK constant.

## Exception-stack window

Earlier in the same exception handler, the firmware compares the current stack pointer against a range built from the same base:

```text
base = 0x80f883b0
size = 0x3ffc
```

The effective range is approximately:

```text
0x80f883b0 .. 0x80f8c3ac
```

or about 16 KiB.

If the interrupted stack is outside the expected exception-stack range, the handler switches to the protected stack area before saving the remaining context.

## Why this matters for firmware modification

This is useful for future injected-code work for two reasons:

1. the low-level exception architecture around `0x80049580` is confirmed active on XGO rather than inherited dead code;
2. preserving the `0x80f883b0` canary and exception-stack region is important when experimenting with external cores or altered memory ceilings.

A custom loader/core should not allocate over or repurpose this region.

## Related Multicore relevance

Classic SF2000 Multicore redirects the general-exception loop at `0x800495a0` to its diagnostic hook. XGO contains the same live loop at the same address:

```text
0x80049598  beqz  $k1,0x800495a8
0x8004959c  nop
0x800495a0  b     0x800495a0
0x800495a4  nop
```

This confirms that the upstream exception-hook patch site is semantically valid on XGO as well.
