# Interactive XGO mapper v16 editor-overlay diagnostic

## Why this exists

Hardware testing showed that narrowing and moving the mapper bitmap did not restore the missing left border. Therefore the missing edge is not a bitmap-size problem.

Static tracing of the v14 editor render path shows that the editor calls the full stock pause renderer at `0x80354640`. That renderer draws the selected resource first, then begins the stock pause-menu row/highlight pass at `0x80354710`.

The v16 diagnostic keeps the normal pause menu unchanged but, when the mapper edit flag at `0x800018e0` is nonzero, skips the stock row/highlight pass after `gpapi.bvs` has already been drawn.

## Patch

Stock renderer hook:

```text
0x80354710 / ASD 0x00354710
li s1,3
li s6,0x28
```

becomes a jump to a small cave hook at `0x80001900`.

The hook:

```text
if mapper_edit_active:
    jump renderer epilogue at 0x803547e0
else:
    restore li s1,3 / li s6,0x28 / li s2,0x106
    return to 0x8035471c
```

Thus the base resource draw remains intact while the native Resume/Quit/Load/Save row/highlight pass is suppressed only inside the mapper editor.

## Baseline

v16 is based on v14 because v14 is the current hardware-proven geometry/selector baseline. Marker coordinates, mapping semantics, persistence, and resource bytes are unchanged from v14.

## Identity

```text
firmware SHA-256:
c17cceff619e90d96ad8c797d57c0c7b3de16fe78c37815ae12aa6aab3a2e6e8

LCFG CRC-32/MPEG-2:
0x6234a80e

resource SHA-256:
46ad48aa063dcb5ab58e4c1d4634944a079627d8359311b80161cb03af5f1314

card ZIP SHA-256:
edd226d230e00912c667ac3e99b49c4ef180afdb1c2af4a5d8c98fd9fe4fdffc
```

## Hardware gate

1. Normal pause menu must remain unchanged.
2. Entering Mapper should remove the stock menu rows/highlight layer from the editor view.
3. Check whether the previously missing mapper left border becomes visible.
4. Verify selector movement and one remap still work.

If the left border appears, the composition-order hypothesis is confirmed and the branch can be finalized around a dedicated mapper render state rather than further bitmap resizing.