# State-14 exact render/navigation patch surfaces recovered from Test05c

Date: 2026-09-20
Status: **SRC/BIN assertions from hardware-lineage builder**

Test05c preserves exact expected stock words before modifying the User Menu. These assertions give us instruction-level anchors for the replacement selector rather than address-only labels.

## Stock render block at 0x80359B1C

Test05c requires the following original words:

```text
80359B1C  00053840
80359B20  00E52021
80359B24  00046940
80359B28  01A46023
80359B2C  000C1040
80359B30  241900AC
80359B34  244A0034
80359B38  241F0097
```

It also asserts:
```text
80359B4C  AFB90014
80359B64  AFB90010
```

This is the selector-coordinate/stack-argument construction surface used by the stock User Menu renderer.

## Stock navigation/dispatch assertions from the same builder

Before Test05 expansion:
```text
80359AA4  24190002   terminal 2
80359E60  24020002   terminal 2
80359EA8  1469F354   original dispatch branch
80359EAC  24120001   delay slot
```

Test106 intentionally differs at these sites because it inherits the Test85 diagnostic four-row selector:
```text
80359AA4  24190003
80359E60  24020003
80359EA8  0828E17C   j 80A385F0
```

The delay-slot/continuation contract must be preserved when replacing the diagnostic dispatcher.

## Background repaint evidence

Test05c deliberately enlarged setup background copy through row 429 using the native state-14 repaint path, while preserving the stock footer/action overlays. This is direct source evidence that a state-14 repaint can clear selector artifacts without replacing the complete 640x480 screen resource.

For the final selector, prefer a native repaint/clear followed by stock TEXT_DRAW labels. Do not reproduce Test05c's six rewritten language bitmaps.

## Construction consequence

The replacement module can be built with three narrowly separated responsibilities:

1. **entry/active dispatch** at the proven Test85 row-dispatch seam;
2. **selector text overlay** after native background repaint;
3. **Refresh handoff** through native Refresh entry and post-workspace module dispatch.

Do not patch the entire 0x80359B1C render block unless needed. It is now an exact known-good fallback surface, but a smaller interception is preferred.

## Evidence labels

- exact Test05c stock-word assertions: **SRC against BIN**
- Test05c four-row UI behavior: **HW lineage**
- Test106 diagnostic replacements at navigation/dispatch sites: **BIN**
- final text-overlay interception: **DESIGN**
