# Interactive XGO mapper v4 hardware result and v5 label fix

## v4 hardware result

Hardware testing confirmed that the v4 architecture works:

- the pause menu opens normally;
- the added MAPPER entry is usable;
- the dedicated mapper editor can be entered;
- arbitrary six-button remapping works;
- the resulting mapping persists through the proven per-ROM `.kmp` path.

The remaining v4 defect is visual: the added `MAPPER` label appears multiple times. The mapper logic itself is functioning.

## Cause and v5 strategy

v4 draws the fourth-row `MAPPER` label independently of the stock three-entry QUIT/LOAD/SAVE text buffer. That avoided the v3 buffer overrun, but the extra label draw occurs on a renderer path that can be revisited. Because the label area is not explicitly cleared by the stock three-row renderer, repeated passes can leave accumulated copies/artifacts.

v5 preserves all v4 mapper/input/save behavior and changes only the independent label path:

1. clear a small framebuffer rectangle covering the fourth-row label area;
2. draw `MAPPER` using the same native text primitive and selected/unselected color logic;
3. continue through the untouched stock renderer.

This makes the extra row idempotent even if the renderer revisits the hook.

## v5 identity

```text
firmware SHA-256:
29d500b16b16bbb451238ebc74c9764964e4b56a0e078747b0eb6a66fc4d461d

LCFG CRC-32/MPEG-2:
0x38cf0868

card ZIP SHA-256:
9e6b43bb8344a1b18f3f6ec5bd5c11e97d58b5909a100514998cc0202b217725
```

The first v5 hardware test should focus only on whether the pause-menu MAPPER label appears exactly once; the remap path is intentionally unchanged from v4.