# Interactive mapper v0 hardware failure and v1 visible-state candidate

## Status

**v0 HARDWARE-REJECTED AS A USABLE EDITOR; v1 STATICALLY BUILT, HARDWARE TEST PENDING.**

The low-level XGO mapping/persistence architecture remains hardware proven. This finding concerns only the first attempt to turn the dormant fifth pause page into an interactive editor.

## v0 hardware result

The first interactive candidate (`89e2006...`) booted and displayed the modified `gpapi.bvs`, but the interaction was not usable or reliably testable:

- reaching the fifth pause page effectively activated the mapper behavior immediately;
- pressing the ordinary A/confirm button returned to gameplay;
- attempted blind directional sequences did not produce a verified remap;
- the screen text was too small;
- there was no dynamic indication of selected physical button or selected logical target;
- using A as save/confirm is intrinsically poor UX because A is itself one of the remappable physical controls.

The hardware tester correctly rejected blind press-counting as an acceptable validation method.

## v0 control-map error

The v0 instructions also did not match the injected event handler. The code assigned:

```text
0x20 / 0x80 -> physical source +/-
0x40 / 0x10 -> logical target +/-
```

while the test instructions described Up/Down as source and Left/Right as target.

Stock XGO behavior plus the recovered GB300 mapper strongly support:

```text
0x10 = Up
0x20 = Right
0x40 = Down
0x80 = Left
0x2000 = A/confirm
```

In particular, the stock XGO `0x40` path increments the pause-menu page and the tester physically uses Down to advance through those pages. Therefore v0's actual source/target axes were the reverse of the supplied instructions.

This means the failed blind sequence is not evidence against arbitrary record addressing. It is evidence that v0's controller/UI contract was defective.

## Start and Select event bits

The stock pause poll asks for mask `0x20f8` at `0x80354e78`, which excludes Start and Select as individual events.

Elsewhere the raw controller state is compared against `0x1001` for the existing Start+Select trigger. This establishes the pair as:

```text
Start  = 0x1000
Select = 0x0001
```

v1 expands the pause poll mask:

```text
0x00354e78  0x240420f8 -> 0x240430f9
```

so the editor can use Start and Select without consuming a remappable face button.

## v1 interaction contract

The fifth page is now a launcher rather than an automatically active editor.

Launcher:

```text
RIGHT       enter editor
A           ignored
LEFT / UP   leave toward previous pause page
```

Editor:

```text
UP / DOWN     select physical button
LEFT / RIGHT  change logical target for that physical button
START         save all edits and resume game
SELECT        cancel edits and return to mapper launcher
A             ignored
```

This deliberately avoids using any of X/Y/L/A/B/R as the commit control.

## Working-state behavior

On entry v1:

1. initializes source index to 0;
2. decodes the six currently active P1 records from `0x810a0f58`;
3. maps the logical IDs through `[0,1,8,9,10,11]` = `[B,Y,A,X,L,R]`;
4. stores six editable selector bytes in the injected cave;
5. renders the stock page and overlays visible source/target markers.

Directional edits change only the cave working copy. The active XGO map remains untouched until Start is pressed, so Select can cancel cleanly.

On Start, v1 updates all six P1 records while preserving each record's upper 16 bits, then jumps to the already hardware-proven writer/resume path at `0x80355804`. The stock writer performs P1/P2 synchronization, `set_keymap()`, and corrected per-ROM persistence.

## Visible-state requirement

v1 does not permit another blind test. The rebuilt `gpapi.bvs` has large PHYSICAL and MAP TO columns and a large control legend. When edit mode is entered, firmware draws two 14x30 RGB565 marker bars directly into the framebuffer:

```text
source marker x = 42
target marker x = 350
y = 138 + selector*48
```

The marker routine uses the same renderer globals observed in stock XGO code:

```text
gp-0x1410 -> framebuffer pointer
gp-0xe18  -> framebuffer width/pitch
```

The stock renderer at `0x80354640` itself loads these globals, so the overlay is grounded in the native rendering path.

Hardware test gate:

```text
navigate to fifth page
  -> press RIGHT once
  -> two bright markers must appear
```

If the markers do not appear, testing stops there. No blind remap sequence should be attempted.

## Injected controller

v1 uses the previously exercised zero cave beginning at runtime `0x800014a0`.

Static build:

```text
injected size: 968 bytes
end:           0x80001868
```

Important internal labels:

```text
entry       0x800014a0
enter       0x80001510
editing     0x800015a8
save        0x800016f4
render      0x80001760
draw_marker 0x800017dc
edit_mode   0x80001850
source      0x80001854
work        0x80001858
encode      0x80001860
```

Firmware patches from exact stock include:

```text
0x00354054  0x24e7fc20 -> 0x24e7fce8  corrected .kmp filename source
0x00354e78  0x240420f8 -> 0x240430f9  include Start + Select in pause poll
0x00354ec0  0x28700003 -> 0x28700004  expose fifth page
0x00354e88  0x104d001e -> J 0x800014a0  route pause events through v1
```

The hook recreates the displaced stock `0x20` branch for all non-mapper pages, so ordinary pause-page dispatch remains on the stock paths.

## Candidate identity

Exact stock SHA-256:

```text
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

v1 firmware:

```text
LCFG CRC-32/MPEG-2: 0x6a3aead7
SHA-256: 56b1477af8f14ad179f9396efd5bf103da5b341d0ae6fbde7b1502287e9a9c7c
```

## Next hardware criterion

The next test is intentionally staged:

1. prove explicit Right-to-enter behavior;
2. prove markers appear;
3. prove markers follow arrow input correctly;
4. only then save one visible remap with Start;
5. verify gameplay behavior and restart persistence.

The first three conditions are required before any mapping result is interpreted.