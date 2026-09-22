# Refresh state-14 composition-order closure

Date: 2026-09-21
Status: BIN/SRC closure; Test119 remains protected.

## Correction to the first reuse audit

The first audit correctly identified the Test05b state-14 repaint mechanism, but later preserved Test05c/Test05d/Test06 source refines its meaning.

Test05d explicitly sets:
```
a2 = 0x86600 = 430 * 640 * 2
```
with the source comment:
> redraw through row 429 ... covers both selector rows but deliberately leaves the stock footer/action overlays alone.

Therefore Test119's existing `0x86600` is not an unexplained partial repaint. It is the **mature preserved Setup composition choice** inherited from that lineage. Expanding it to 480 rows is not automatically desirable; it would repaint the footer/action region.

This is exactly why reuse-first review matters: Test05b alone suggested 480 rows, while later source records why the implementation was refined back to 430.

## State-14 order

The stock User Menu/state-14 render sequence is now bounded as:

1. `0x80359AFC..0x80359B0C` — copy/repaint 430 rows of the 640-wide RGB565 Setup resource.
2. `0x80359B1C...` — stock dynamic selector coordinate/render work.
3. `0x80359BA8` — historical post-TV hook/branch seam. Test119 redirects this seam into its selector renderer when active.
4. Test119 injected renderer draws REFRESH GAMES presentation, then returns to the native tail at `0x807DB9D4`.

The visible blue Setup boxes behind Refresh are therefore not evidence that the base resource failed to repaint. They are native state-14 dynamic selector/highlight output produced before the Test119 overlay hook.

## Reuse consequence

Mapper v16's proven composition strategy applies conceptually: when a modal is active, suppress the underlying native dynamic row/highlight layer rather than enlarging the modal's framebuffer fill.

For Refresh, however, we must not transplant Mapper's pause-menu addresses. The safe XGO-specific solution must conditionally bypass the state-14 dynamic selector draw **only when selector_active != 0**, while preserving:
- stock Setup rendering when inactive;
- stock state-14 navigation/selection ownership used by Test119;
- Test119 renderer hook and native-tail return;
- footer/action region;
- all Test119 A/B/Refresh lifecycle bytes.

## Why Test120/121 were wrong-layer changes

Test120 and Test121 modified the injected Refresh renderer. The unwanted blue boxes originate earlier in the native state-14 dynamic selector pass. Painting over that layer changed execution/presentation behavior and caused HW freezes.

The correct target is now the producer of the unwanted layer, not the overlay that follows it.

## Next binary gate

Pin the exact call/instruction range in `0x80359B1C..0x80359BA8` that emits the 172x172 Setup selector/highlight/A badge. Identify a continuation that reaches the Test119 `0x80359BA8` hook with all registers/stack expected by the selector renderer.

Only after that range and continuation are exact may a selector-active conditional suppression helper be emitted.

No full-screen repaint change is authorized.

## Exact native selector producer — BIN closure

Direct disassembly of protected Test119 closes the dynamic selector producer before the overlay hook:

```
80359B10  lw    a1,0x1A4(sp)       # current state-14 selection
80359B14  lw    s0,-5136(gp)       # frontend framebuffer
80359B18  lw    t0,-3608(gp)
80359B1C..80359B38                # derive selector x/y from selection
80359B3C  move  a0,s4
80359B40  move  a1,zero
80359B44  move  a2,zero
80359B48  li    a3,172
80359B4C  sw    a3,20(sp)
80359B50  sw    t2,24(sp)          # x
80359B54  sw    ra,28(sp)          # y
80359B58  sw    s0,32(sp)          # framebuffer
80359B5C  sw    t0,36(sp)
80359B60  jal   0x80353250         # native 172x172 selector compositor
80359B64  sw    a3,16(sp)          # 172 height/width companion
```

The call target `0x80353250` has a normal function prologue and is distinct from the stock text renderer `0x803528A4`. This pins `0x80359B3C..0x80359B64` as the dynamic 172x172 selector/highlight composition call.

After it returns, native code continues at `0x80359B68` with TV-mode/text handling and reaches the existing Test119 hook at `0x80359BA8`.

### Safe suppression seam

The narrowest producer-side suppression is therefore to bypass **only** the call setup/call block `0x80359B3C..0x80359B64` when `selector_active @ 0x80A389C0 != 0`, continuing at `0x80359B68`.

This preserves:
- selection load and coordinate math at `0x80359B10..0x80359B38`;
- stock navigation/state ownership;
- all post-selector native TV/text work at `0x80359B68...`;
- Test119 hook at `0x80359BA8`;
- Test119 overlay renderer and native-tail return.

When selector_active == 0, execution must reproduce the exact original `0x80359B3C..0x80359B64` block with its original delay-slot semantics. No instruction in that block may simply be discarded.

This is the state-14 analogue of the Mapper-v16 producer-suppression pattern, now pinned to XGO BIN addresses rather than inferred from Mapper addresses.
