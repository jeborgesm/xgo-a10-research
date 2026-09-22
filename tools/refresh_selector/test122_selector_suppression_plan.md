# Test122 source plan — selector-producer suppression only

Status: source design; derived from protected Test119. No framebuffer geometry changes.

## Purpose

Remove the underlying stock Setup blue selector/A-badge while REFRESH GAMES is active, by suppressing the native state-14 172x172 selector compositor that produces it.

## Protected behavior

Test119 SHA-256:
`d357a86a79175d7c07877026ccfaa94c352fd571ba7d54b08d1e9acf1cdf4c15`

All Test119 overlay, A/B, navigation, native Refresh, command bridge and re-entry logic remains unchanged.

## Hook

Replace the beginning of the native selector call-setup block at `0x80359B3C` with a jump to a helper in verified free tail space at `0x80A39000`.

The helper checks `selector_active @ 0x80A389C0`.

### Active

If nonzero:
- do not execute `0x80359B3C..0x80359B64`;
- jump to `0x80359B68`.

This suppresses only the stock 172x172 dynamic selector compositor.

### Inactive

Reproduce the exact displaced native block:

```
80359B3C  move  a0,s4
80359B40  move  a1,zero
80359B44  move  a2,zero
80359B48  li    a3,172
80359B4C  sw    a3,20(sp)
80359B50  sw    t2,24(sp)
80359B54  sw    ra,28(sp)
80359B58  sw    s0,32(sp)
80359B5C  sw    t0,36(sp)
80359B60  jal   0x80353250
80359B64  sw    a3,16(sp)
```

then jump to `0x80359B68`.

## Explicit non-changes

- no `memset`;
- no framebuffer fill changes;
- no 430/480-row repaint changes;
- no Test119 injected renderer changes;
- no extra text calls;
- no footer;
- no navigation terminal changes;
- no A/B changes;
- no Refresh lifecycle changes.

This is a producer-side suppression test only.
