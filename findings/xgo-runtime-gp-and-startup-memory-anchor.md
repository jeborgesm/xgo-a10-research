# XGO runtime GP and startup memory anchors

Status: **confirmed from startup instructions**.

## Runtime `$gp`

The XGO startup code at virtual addresses `0x80001270-0x80001274` explicitly initializes the MIPS global pointer:

```text
0x80001270  lui    $gp, 0x80c3
0x80001274  addiu  $gp, $gp, 0x4774
```

Therefore:

```text
XGO stock runtime $gp = 0x80c34774
```

This is a high-value disassembly anchor because many application globals are accessed as signed offsets from `$gp` and can now be assigned absolute runtime addresses deterministically.

For example, previously reconstructed frontend globals become:

```text
$gp - 0x0e18 = 0x80c3395c   logical framebuffer width  (640)
$gp - 0x0e1c = 0x80c33958   logical framebuffer height (480)
$gp - 0x0d7c = 0x80c339f8   Archive.sys first persistent word / six-state selector
$gp - 0x0d20 = 0x80c33a54   Archive.sys volume word
$gp - 0x5f40 = 0x80c2e834   Archive.sys binary-toggle word
```

These names retain the semantics established in earlier findings; the new result is the absolute address mapping.

## Comparison with public SF2000 stock reconstruction

The public `sf2000_multicore` reconstruction documents the original stock SF2000 `$gp` setup as:

```text
lui   $gp, 0x80c1
addiu $gp, $gp, 0x14f4
```

or:

```text
SF2000 stock $gp = 0x80c114f4
XGO stock $gp    = 0x80c34774
Delta            = +0x23280
```

This is another direct demonstration that XGO data/global layout cannot be mapped using the small code-section deltas already identified for libc/display code. The XGO application's global-data region has moved substantially.

## Startup stack reservation

Immediately before `$gp` initialization, XGO startup constructs an aligned memory region beginning at approximately `0x80f883b0`, advances by `0x4000`, and assigns the resulting value to `$sp`. It also writes the marker `0xABCDEF12` at the lower address.

Relevant instructions:

```text
0x80001240  lui    $t0, 0x80f9
0x80001244  addiu  $t0, $t0, -31824   ; 0x80f883b0
...
0x80001254  addiu  $t1, $t0, 16384    ; +0x4000
0x80001258  addu   $sp, $t1, $zero
0x8000125c  lui    $t0, 0x80f9
0x80001260  addiu  $t0, $t0, -31824
0x80001264  lui    $t1, 0xabcd
0x80001268  ori    $t1, $t1, 0xef12
0x8000126c  sw     $t1, 0($t0)
```

The exact role of the `0xABCDEF12` marker should remain conservatively described as a startup memory/stack-boundary marker until its readers are traced.

## Reverse-engineering consequence

Use `0x80c34774` as the canonical XGO `$gp` for future static analysis. This allows GP-relative loads/stores in anonymous functions to be converted into stable absolute globals and should make the next firmware-wide symbol-map pass substantially more productive.
