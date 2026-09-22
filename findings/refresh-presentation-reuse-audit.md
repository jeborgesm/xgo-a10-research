# Refresh presentation reuse audit — Test119 versus proven XGO UI mechanisms

Date: 2026-09-21
Status: source/BIN architecture audit; no hardware candidate authorized by this document alone.

## Question

Can the requested full-screen REFRESH GAMES presentation be obtained by reusing an already-proven XGO UI mechanism instead of modifying Test119's injected backdrop loop?

## Reuse candidate 1 — Test05b/Test06 Setup repaint

Source: `tools/game_lists/build_test05b_polished_refresh_menu.py`.

The preserved builder patches the **stock state-14 User Menu renderer**, not an injected modal framebuffer loop. Its explicit full-screen repaint patch is:

```
0x80359AFC  lui   a2,0x0009
0x80359B00  ori   a2,a2,0x6000    # a2 = 0x96000 = 640*480*2
0x80359B04  move  a0,t1
0x80359B0C  move  a1,t3
```

The source comment states that stock copied only the region needed by its one-row menu and this expands that refresh to all 640x480 RGB565 pixels before the active selector is drawn.

### Critical incompatibility with current Test119

Test119's selector renderer hook is at `0x80359BA8`, after the `0x80359AFC..0x80359B0C` stock repaint/copy setup.

Therefore the earlier Test05b full-screen repaint mechanism is upstream of the Test119 injected overlay and can potentially establish a clean full-screen base **without touching the Test119 injected fill loop at all**.

This is categorically different from failed Test120/121:
- Test120 replaced/augmented the injected selector renderer.
- Test121 changed the injected selector fill loop.
- the Test05b mechanism changes the already-existing stock state-14 repaint extent before Test119's hook executes.

OPEN: exact Test119 words and register/dataflow at `0x80359AFC..0x80359B0C` must be checked before transplant. No candidate until displaced/current words and destination/source semantics are pinned against Test119.

## Reuse candidate 2 — Mapper v16 stock-layer suppression

Source finding: `findings/interactive-xgo-mapper-v16-editor-overlay-diagnostic.md`.

Mapper v16 solved stock-menu leakage by conditionally bypassing the native row/highlight pass after the modal resource was drawn. The key architectural lesson is proven: suppressing the underlying native selection layer can be safer than painting over it.

However its concrete hook is pause-menu-specific:
- pause renderer `0x80354640`;
- row/highlight pass `0x80354710`;
- mapper flag `0x800018E0`;
- epilogue `0x803547E0`.

These addresses cannot be transplanted into state 14. The reusable item is the **composition pattern**, not the addresses.

For Refresh, the equivalent question is now explicit: locate the state-14 User Menu row/highlight draw pass relative to Test119's `0x80359BA8` hook. If the unwanted blue borders are drawn after the base resource and can be conditionally skipped when `selector_active != 0`, that is the preferred solution for visual leakage.

## Reuse candidate 3 — Mapper v19 resource-backed modal

Mapper v19 proves a rich XGO modal can use a static resource for the visual foundation and dynamic overlays for state. It also proves the resource geometry can be transformed offline while keeping dynamic coordinates coherent.

For Refresh this is a larger architectural option, not the first next patch. Test119 already has working text, navigation, A/B, native Refresh entry, and re-entry. Replacing that presentation with a new resource would add packaging/resource dependencies. It should be considered only if the stock state-14 repaint/suppression mechanisms cannot provide the desired clean canvas.

## Protected Test119 layer

The following Test119 behavior is out of scope for presentation work:
- selector_active at `0x80A389C0`;
- refresh_command at `0x80A389C4`;
- stock state-14 selection ownership;
- active terminal 7 / inactive terminal 3;
- B-active proven close path;
- A-active command save + normalize selection to 3 + `0x807DB5CC`;
- native Refresh status/epilogue and re-entry.

## Result

The next investigation is **not** another backdrop-loop edit.

Priority:
1. disassemble/pin Test119 `0x80359AFC..0x80359BA8`;
2. compare exact words with Test05b's full-screen state-14 repaint patch;
3. identify the state-14 native highlight pass responsible for the blue boxes;
4. determine whether selector-active can conditionally suppress that pass using the Mapper-v16 composition pattern;
5. only then decide whether any firmware candidate is warranted.

This audit demonstrates a concrete reusable path already present in repository source and bounds what still requires binary closure.
