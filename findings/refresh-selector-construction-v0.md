# Refresh selector construction v0 — code skeleton and remaining hard gates

Date: 2026-09-20

A source-level MIPS reconstruction now exists at:
`tools/refresh_selector/selector_module_v0.S`.

It deliberately separates **closed semantics** from **unclosed hook mechanics**.

Closed in source:
- private selector state;
- row-3 entry concept;
- 0..7 wrap semantics;
- B cancel;
- A -> native Refresh entry;
- CLASSIC -> `s5=0; j 0x80A38000` only after native Refresh frame/workspace;
- stock TEXT_DRAW ABI and all nine strings.

Not yet permitted to emit:
1. selector-active UP/DOWN/B/A input interception because the exact state-14 event-load/comparison instruction and displaced continuation are not yet pinned;
2. text renderer interception because exact state-14 redraw hook stack preservation is not yet pinned;
3. non-CLASSIC module execution adapters.

The assembly intentionally marks these points OPEN rather than hiding guesses in generated opcodes.

## Recovered TEXT_DRAW ABI

From the hardware-lineage timed status renderer:
```text
a0 = lw -5136(gp)       current framebuffer
a1 = x
a2 = y
a3 = 0
sp+16 = s5
sp+20 = lw -30380(gp)   stock text config/color
sp+24 = string pointer
jal 0x803528A4
delay: fp=0
```

This is sufficient to implement the visual rows once the renderer hook frame/continuation is pinned.

## Safety result

We are now constructing executable source without prematurely producing a firmware. The fail-closed builder remains audit-only until the two exact hook mechanics above are closed.
