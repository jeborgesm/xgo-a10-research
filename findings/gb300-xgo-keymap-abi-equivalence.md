# GB300 v1 mapper and XGO keymap ABI equivalence

## Status

**Confirmed from executable code on both firmware branches.**

The GB300 v1 native mapper and XGO A10's retained per-game keymap engine use the same 4-byte mapping-record ABI and the same ordinary six-button physical record order.

This removes the need for a translation layer in an XGO mapper transplant.

## Shared 4-byte record ABI

GB300 mutation code at `0x80308ca0..0x80308d1c` constructs:

```text
bits 0..15  logical controller target ID
bit 16      autofire/turbo
```

XGO `set_keymap()` at `0x8035e83c` consumes the same representation:

```text
bits 0..15  libretro joypad target ID
bit 16      turbo/repeat flag
```

The GB300 logical encode table at `0x805f2a00` is:

```text
08 00 0a 0b 01 09
```

Numerically:

```text
8, 0, 10, 11, 1, 9
```

These are directly the libretro IDs already confirmed in XGO:

```text
8  -> A
0  -> B
10 -> L
11 -> R
1  -> Y
9  -> X
```

Therefore GB300's native mapper is editing the same logical target namespace XGO's runtime compiler already understands.

## Shared physical record order

XGO's canonical ordinary 48-byte mapping order is:

```text
P1: X, Y, L, A, B, R
P2: X, Y, L, A, B, R
```

GB300 `KeyMapInfo.kmp` uses the same ordinary per-player persisted order.

GB300's six-position UI transform is:

```text
[5, 2, 0, 1, 3, 4]
```

Therefore its UI indices target the ordinary records as:

```text
UI 0 -> R
UI 1 -> L
UI 2 -> X
UI 3 -> Y
UI 4 -> A
UI 5 -> B
```

Those transformed indices can address XGO's active 48-byte per-game map directly.

## Shared two-player structure

Both firmwares use:

```text
6 records P1 = 24 bytes
6 records P2 = 24 bytes
                  48 bytes total
```

GB300's native editor mirrors an edited P1 record to the corresponding P2 record at `+24` bytes.

XGO's runtime loader/compiler can preserve independent P1/P2 maps, but its stock save policy also synchronizes P2 back to P1 before persistence. Thus mirroring the first on-device mapper probe is compatible with both lineages and with XGO's existing save policy.

## Persistence differs, ABI does not

The principal architectural difference is persistence scope:

```text
GB300 v1:
  seven 48-byte system blocks
  -> global 336-byte Resources/KeyMapInfo.kmp

XGO A10:
  one active 48-byte mapping
  -> per-ROM %s/save/%s.kmp
```

This difference does not require changing the mapper record representation.

## Minimal transplant boundary

The first XGO mapper implementation can therefore be reduced to:

```text
1. expose/select dormant gpapi.bvs fifth page
2. maintain six-position UI selector
3. transform UI slot through [5,2,0,1,3,4]
4. maintain bounded logical target selector
5. encode target through [8,0,10,11,1,9]
6. maintain binary turbo flag
7. write the resulting 32-bit record into XGO active 48-byte map
8. mirror corresponding P2 record initially
9. call existing XGO set_keymap()
10. use existing XGO per-ROM .kmp persistence path
```

No GB300 `KeyMapInfo.kmp` writer, no system-block table, no record conversion, and no logical-button translation are needed.

## Why this matters

The fifth-page resurrection is no longer a speculative UI reconstruction. We have a manufacturer-implemented editor from a close descendant whose state semantics write exactly the ABI already consumed by XGO's surviving runtime.

The next engineering step is therefore a narrowly scoped XGO probe, not additional format archaeology.
