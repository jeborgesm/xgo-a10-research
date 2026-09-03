# GB300 v1 native mapper handler and persistence path

## Status

**Binary-grounded.** This finding comes from direct disassembly of the stock GB300 v1 `bisrv.asd` (SHA-256 `4084798a21d4abd93893f03f8fc4e1e4a8c9e31d4c60857328a9cab0cf892627`).

## Key result

The working GB300 mapper is not a separate application. It is integrated directly into the stock pause-menu state machine, and the code path for pause-menu index `4` enters a substantial native mapper handler.

This is the closest known completed descendant of the dormant XGO `gpapi.bvs` fifth pause-menu position.

## Exact pause-menu resource table

The GB300 pause-menu resource table begins at runtime address `0x806ced80`:

```text
0x806ced80 -> dism.cef
0x806ced84 -> d2d1.hgp
0x806ced88 -> bisrv.nec
0x806ced8c -> pwsso.occ
0x806ced90 -> gpapi.bvs
0x806ced94 -> fhshl.skb
```

The working firmware materializes this table in three distinct pause-menu code paths:

```text
0x80308964 -> table base 0x806ced80
0x80308da8 -> table base 0x806ced80
0x80309108 -> table base 0x806ced80
```

The table is indexed with `menu_index * 4`, exactly as expected for an array of resource pointers.

## Native mapper entry

The important transition occurs after pause-menu index handling around `0x80308ea4`:

```asm
80308ea4  lw    a0,-18596(gp)      # current pause-menu index/state
80308ea8  li    a2,4
80308eac  bne   a0,a2,0x80308d24
```

When the active pause-menu position is `4`, execution does **not** fall back to the ordinary action cases. It proceeds into a dedicated native mapping state machine beginning around `0x80308eb4`.

This is direct executable proof that GB300's fifth pause-menu item is a functioning controller mapper.

## Mapper input/event state

The mapper reads a byte at:

```text
$gp = 0x80c65d78
-18304(gp) = 0x80c615f8
```

and dispatches on values including:

```text
0x01
0x02
0x04
0x08
0x10
0x20
0x80
```

Representative branch sequence:

```asm
80308eb4  lbu   v1,-18304(gp)
80308eb8  li    a2,1
80308ebc  beq   v1,a2,...
80308ec4  li    a1,2
80308ec8  beql  v1,a1,...
80308ed0  beq   v1,a0,...          # a0 == 4 here
80308ed4  li    a3,8
80308ed8  beq   v1,a3,...
80308edc  li    s4,16
80308ee0  beql  v1,s4,...
80308ee8  beq   v1,s3,...          # s3 == 32
80308eec  li    s3,128
80308ef0  beql  v1,s3,...
```

This is a compact button/event dispatch table implemented as comparisons rather than a jump table.

The exact physical meaning of each event value still needs to be mapped, but the structure is now recovered.

## Mapper-specific resources are used from the native handler

Immediately after the event dispatch, the code addresses the mapper resource table around `0x806cec90` and loads entries from it. For example:

```asm
80308ef8  lui   t5,0x806d
80308f04  addiu t4,t5,-5048        # 0x806cec48
80308f10  lw    a3,88(t4)          # 0x806ceca0 = mczwq.ikb
```

This ties the native handler directly to the known mapper artwork/resource family (`hctml.ers`, `ztrba.nec`, `lk7tc.bvs`, `mczwq.ikb`, etc.).

## Mapper UI state variables

Several persistent mapper globals are now identifiable by GP-relative address:

```text
0x80c61554  (-18468 gp) byte - mapper sub-selection / physical-button state
0x80c6153e  (-18490 gp) byte - mapper selection state, bounded around 0..5
0x80c614dc  (-18588 gp) byte - secondary mapper choice/index
0x80c614d4  (-18596 gp) word - current pause/menu mode; value 4 enters mapper
0x80c614a8  (-18640 gp) word - mapper auxiliary state
0x80c615f8  (-18304 gp) byte - current button/event code
```

At `0x803090a0`, the mapper manipulates the `0x80c6153e` byte as a six-position value:

```asm
803090a0  lbu   v0,-18490(gp)
...
803090a8  li    v0,5
...
803090ac  addiu v0,v0,-1
803090b0  sb    v0,-18490(gp)
```

Elsewhere the code checks the same state against an upper bound of five:

```asm
80309254  lbu    v1,-18490(gp)
80309258  sltiu  t3,v1,5
```

This is consistent with the six physical remappable controls documented in the family (`X,Y,L,A,B,R`), although the exact visual-index-to-button mapping should still be established before transplanting behavior.

## Global KeyMapInfo persistence

GB300's later firmware stores mappings in a global table rather than XGO's per-ROM `.kmp` files.

The writer is at:

```text
0x80308208
```

It constructs:

```text
%s/Resources/KeyMapInfo.kmp
```

and writes:

```asm
li a1,4
li a2,84
```

through the firmware fwrite-like routine.

Therefore the file payload is:

```text
84 records * 4 bytes = 336 bytes
```

which equals:

```text
7 systems * 48 bytes/system = 336 bytes
```

The source table written by this routine begins at approximately:

```text
0x80ae8c70
```

This independently confirms the later family architecture: seven system mappings, each retaining the same 48-byte / 12-record structure.

## Mapper commit path

The native mapper calls the `KeyMapInfo.kmp` writer directly from three sites:

```text
0x8030a504
0x8030a524
0x8030a574
```

The first is guarded by mapper state immediately before it:

```asm
8030a4b0  li    a2,6
...
8030a4c8  bnez  s4,0x8030a504
...
8030a504  jal   0x80308208       # persist KeyMapInfo.kmp
```

The later paths also write after updating mapper state, confirming persistence is part of the native editor's normal confirm/exit flow rather than a separate settings-save operation.

## Architectural consequence for XGO

We no longer need to invent the mapper interaction model.

The defensible transplant strategy is now:

```text
GB300 pause-menu index-4 mapper state machine
        |
        | reuse navigation/event semantics and rendering sequence
        v
XGO hidden gpapi.bvs position 5
        |
        | operate on XGO's existing 48-byte per-game map
        v
XGO set_keymap()
        |
        v
XGO existing <game>.kmp writer
```

Do **not** port GB300's 336-byte `KeyMapInfo.kmp` persistence layer. XGO's older per-ROM mapping architecture is preferable for the multicore goal and is already executable-proven.

## Next binary-lift targets

1. Map GB300 event codes `1,2,4,8,16,32,128` to physical controls by tracing their shared input producer.
2. Recover exact six-position physical-button navigation and logical-target cycling.
3. Identify the code that modifies the 4-byte mapping record inside the 336-byte table.
4. Translate only that state-machine behavior to XGO's 48-byte active-game map.
5. Build a minimal XGO hardware probe that changes one mapping from the resurrected fifth menu position and persists it through the existing per-ROM `.kmp` writer.
