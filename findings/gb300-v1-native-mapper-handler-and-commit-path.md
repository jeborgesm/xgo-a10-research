# GB300 v1 native mapper handler and persistence path

## Status

**Binary-grounded.** This finding comes from direct disassembly of stock GB300 v1 `bisrv.asd`, SHA-256 `4084798a21d4abd93893f03f8fc4e1e4a8c9e31d4c60857328a9cab0cf892627`.

## Key result

The working GB300 mapper is integrated directly into the stock pause-menu state machine. Pause-menu position `4` enters a substantial native controller-mapping handler, making it the closest known completed descendant of XGO's dormant `gpapi.bvs` fifth pause-menu position.

## Exact pause-menu resource table

```text
0x806ced80 -> dism.cef
0x806ced84 -> d2d1.hgp
0x806ced88 -> bisrv.nec
0x806ced8c -> pwsso.occ
0x806ced90 -> gpapi.bvs
0x806ced94 -> fhshl.skb
```

The table is materialized from code at:

```text
0x80308964
0x80308da8
0x80309108
```

and indexed as an array of resource pointers.

## Native mapper entry

```asm
80308ea4  lw    a0,-18596(gp)      # current pause-menu mode
80308ea8  li    a2,4
80308eac  bne   a0,a2,0x80308d24
```

Mode `4` falls through into the mapper beginning around `0x80308eb4`.

## Correction: `0x80c615f8` is a system discriminator, not mapper input

Earlier analysis provisionally labeled the byte at `0x80c615f8` (`-18304(gp)`) as a mapper button/event code. That interpretation is now disproved by the deeper binary lift.

The mapper reads it at `0x80308eb4` and dispatches values:

```text
1, 2, 4, 8, 16, 32, 128
```

but the branch destinations write a **system keymap index** to `0x80c61554` (`-18468(gp)`):

```text
value 1   -> system block 0
value 2   -> system block 0
value 128 -> system block 1
value 8   -> system block 2
value 4   -> system block 3
value 32  -> system block 4
value 16  -> system block 5
```

Representative code:

```asm
80308eb4  lbu   v1,-18304(gp)
80308eb8  li    a2,1
80308ebc  beq   v1,a2,0x80309b74
...
80308ec8  beql  v1,a1,0x80308ef8   # a1 = 2
80308ecc  sb    zero,-18468(gp)     # block 0
...
80308ed8  beq   v1,a3,0x80309cf8   # a3 = 8
...
80308ee0  beql  v1,s4,0x80308ef8   # s4 = 16
80308ee4  sb    s1,-18468(gp)       # s1 = 5
...
80308ee8  beq   v1,s3,0x8030a56c   # s3 = 32
...
80308ef0  beql  v1,s3,0x80308ef8   # s3 = 128 after reload
80308ef4  sb    a2,-18468(gp)       # block 1
```

and the remote destinations complete the mapping:

```asm
80309b78  sb    zero,-18468(gp)     # value 1 -> block 0
80309cf4  sb    s0,-18468(gp)       # value 4, s0=3 -> block 3
80309cfc  sb    a1,-18468(gp)       # value 8, a1=2 -> block 2
8030a570  sb    a0,-18468(gp)       # value 32, a0=4 -> block 4
```

Independent GB300 documentation gives the seven persisted `KeyMapInfo` blocks in this order:

```text
0 FC
1 PCE
2 SFC
3 MD/SMS
4 GB/GBC
5 GBA
6 unknown/reserved (defaults like SFC)
```

Therefore the binary dispatch resolves to:

```text
1 or 2 -> FC
128    -> PCE
8      -> SFC
4      -> MD/SMS
32     -> GB/GBC
16     -> GBA
```

The fact that two discriminator values share FC block 0 is consistent with GB300 v1 having two NES emulator paths that share one FC keymap. The seventh persisted block is not selected by this mapper dispatch.

## Mapper UI state variables, corrected

```text
0x80c61554 (-18468 gp) byte - selected KeyMapInfo system block (0..5 here)
0x80c6153e (-18490 gp) byte - six-position physical-button UI selector (0..5)
0x80c614dc (-18588 gp) byte - logical-target UI selector
0x80c614dd (-18587 gp) byte - autofire/turbo UI state
0x80c614d4 (-18596 gp) word - pause/menu mode; 4 enters mapper
0x80c614c8 (-18608 gp) word - mapper edit/commit state
0x80c615f8 (-18304 gp) value - emulator/system discriminator used to choose keymap family
```

The physical-button selector wraps through six positions. At `0x803090a0` decrement from zero wraps to five; at `0x80309254` increment past five wraps to zero.

## Exact keymap selection and mutation

The full record-level semantics are documented in `gb300-v1-keymap-record-semantics.md`.

The critical results are:

```text
UI slot transform @ 0x805f2a08 = [5,2,0,1,3,4]
logical encode    @ 0x805f2a00 = [8,0,10,11,1,9]
KeyMapInfo base                 = 0x80ae8c70
system block size               = 48 bytes
record size                     = 4 bytes
```

The mapper mutation site is `0x80308ca0..0x80308d1c`. It composes a complete 32-bit logical+autofire record and mirrors it to the same physical slot in both 24-byte player halves.

## Global KeyMapInfo persistence

The writer at `0x80308208` constructs:

```text
%s/Resources/KeyMapInfo.kmp
```

and writes:

```text
84 records * 4 bytes = 336 bytes
7 systems * 48 bytes = 336 bytes
```

The source table begins at `0x80ae8c70`.

The mapper calls this writer from:

```text
0x8030a504
0x8030a524
0x8030a574
```

After the latter commit paths, the selected system block is computed as:

```text
0x80ae8c70 + system * 48
```

and passed to `0x8030ca4c` with `a1 = 8`.

## Runtime keymap application helper

`0x8030ca4c` is not a persistence routine. It consumes the selected 48-byte keymap block and expands/translates all 12 records into runtime controller state.

The function iterates 12 input records. For each record it compares the stored logical ID against a system-dependent lookup family rooted around `0x805f2d5c..0x805f2d8c`, preserves the record's autofire bit, and builds an intermediate 12-word representation on its stack. It then processes the two six-record player halves separately into runtime mapping structures.

This closes the post-save flow conceptually:

```text
edit 4-byte record
  -> mirror P1/P2 record
  -> persist 336-byte KeyMapInfo.kmp
  -> select current 48-byte system block
  -> 0x8030ca4c translates/applies 12 records to runtime input state
```

## Architectural consequence for XGO

The manufacturer interaction model is now sufficiently recovered that XGO does not need a newly invented mapper design.

The transplant should be:

```text
GB300 mapper UI/navigation + slot transform + logical/turbo mutation semantics
        |
        v
XGO resurrected gpapi.bvs fifth pause-menu position
        |
        v
XGO active 48-byte per-game map
        |
        v
XGO set_keymap() / existing runtime application path
        |
        v
XGO existing <game>.kmp persistence
```

Do **not** port GB300's global 336-byte persistence layer.

## Next lift targets

1. Resolve the exact visual UI index to physical-button label mapping, using renderer resource positions plus the proven slot transform `[5,2,0,1,3,4]`.
2. Recover the logical-target and autofire navigation actions that modify `0x80c614dc/0x80c614dd` before the commit path.
3. Compare GB300 `0x8030ca4c` runtime translation directly against XGO's existing `set_keymap()` behavior to determine how much logic can be reused unchanged.
4. Build the first minimal XGO fifth-menu-position probe that changes one mapping and persists through XGO's existing per-ROM `.kmp` path.

## External corroboration

nummacway GB300 technical documentation, `KeyMapInfo.kmp` section: https://nummacway.github.io/gb300/
