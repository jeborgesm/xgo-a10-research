# Interactive XGO mapper v19: intact v7 geometry + mature v14 behavior

## Root cause

Comparison of the v7 and v8 mapper resources identified the long-running left-edge regression.

The intact v7 mapper begins at:

```text
x = 225
```

In v8, the resource-generation cleanup treated:

```text
x = 260
```

as the mapper boundary and replaced the entire strip:

```text
x = 225..259
y = 0..479
```

with stock artwork. That is exactly 35 x 480 = 16,800 pixels.

The firmware binary itself was unchanged between v7 and v8, proving that the missing mapper edge was a resource regression rather than a renderer or clipping change.

All later visual refinements based on the v8-descended resource, including v10 and v14, therefore operated on an already-amputated mapper.

## v19 reconstruction

v19 deliberately combines two trustworthy ancestors:

- v7: intact mapper geometry
- v14: mature hardware-proven mapper behavior, persistence, corrected selector Y geometry, and 12% scale target

The full intact v7 mapper region is:

```text
x = 225..639
width = 415
height = 480
```

The complete mapper is scaled to 88%:

```text
width = 365
height = 422
```

and centered in the original mapper region at:

```text
x = 250
y = 29
```

This preserves the complete left border instead of scaling a crop that already lacked 35 pixels.

## Marker geometry

Original v7 dynamic marker X positions:

```text
physical = 270
target   = 470
```

Transformed through the restored full-width mapper geometry:

```text
physical = 290
target   = 465
```

The hardware-improved v14 vertical geometry is retained:

```text
y base     = 154
row stride = 37
```

## Legend

The resource now reflects actual hardware behavior:

```text
A = OPEN / SAVE+PLAY
ARROWS = CHANGE
```

No Start+Select save instruction remains.

## Identity

```text
firmware SHA-256:
466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab

LCFG CRC-32/MPEG-2:
0x83bc2420

gpapi.bvs SHA-256:
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8

card ZIP SHA-256:
c45925f965cf86b4e1efc622b02aabb5545122814743aaf7723d4dbf6ba4ec81
```

## Hardware result — PASS

v19 passed the physical-device presentation gate on September 3, 2026.

Confirmed on the tested XGO Plus:

- the complete mapper geometry, including the previously missing left side, is visible;
- the yellow physical and target selectors are centered closely enough to make every selected row unambiguous;
- interactive remapping remains functional;
- A/Confirm saves the mapping and resumes gameplay;
- per-game mapping persistence remains functional across game exit/relaunch;
- the mapper has been exercised successfully with NES, SNES, and CPS1 titles.

The v8 resource regression is therefore **closed**. v19 is the hardware-confirmed mapper release candidate and should supersede the rejected v11-v18 visual/diagnostic experiments.

## Preservation note

The final feature should be preserved primarily as reproducible patch/build logic, exact offsets/semantics, resource-generation steps, hashes, and hardware evidence. A redistributable release artifact should avoid publishing the proprietary stock XGO firmware or stock resource files unless redistribution rights are established. Prefer a patcher that accepts a user-supplied verified stock card/firmware and produces the v19 files locally.