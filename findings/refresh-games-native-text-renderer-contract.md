# Native text primitive selected for Refresh Games selector

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **BIN/SRC contract recovered; removes custom-raster requirement**

## Result

The project already has a repeatedly used stock text renderer:

```text
TEXT_DRAW = 0x803528A4
```

Recovered C-style contract:

```c
void text_draw(void *framebuffer,
               int x,
               int y,
               int mode,
               uint32_t arg4,
               uint32_t arg5,
               const char *text);
```

The stock-font timed Refresh status path demonstrates a live frontend call shape:

```text
a0 = *(gp-5136)       framebuffer
a1 = x
a2 = y
a3 = mode
stack+16 = stock style/font argument
stack+20 = stock style/font argument
stack+24 = char *text
jal 0x803528A4
```

This renderer has already been used by the Refresh lineage for:
- `Games Updated`
- `No New Games`
- `Refresh Failed`

and is also the stock list-label renderer family used elsewhere in the frontend.

## Consequence for REFRESH GAMES

The new selector does **not** need:
- eight rasterized option cards;
- a guessed resource triplet;
- a new font;
- Test05's hand-drawn ASCII glyphs.

It can render all selector labels through the native font path:

```text
REFRESH GAMES
Famicom
Super Famicom
Mega Drive
Game Boy
Game Boy Color
Game Boy Advance
Arcade
Classic
```

The selection indicator can also be text (`>`) or a tiny framebuffer primitive; no resource registration is necessary.

## Proposed rendering grammar

```text
native framebuffer/background
        |
        +-- TEXT_DRAW title
        |
        +-- TEXT_DRAW row 0
        +-- TEXT_DRAW row 1
        +-- TEXT_DRAW row 2
        +-- TEXT_DRAW row 3
        +-- TEXT_DRAW row 4
        +-- TEXT_DRAW row 5
        +-- TEXT_DRAW row 6
        +-- TEXT_DRAW row 7
        |
        +-- selected-row indicator
```

The exact coordinates/style values must be copied from a known native list/status presentation rather than invented until visually necessary.

## Evidence boundary

- `0x803528A4` is a generic stock text renderer: **BIN/SRC**
- live Refresh status uses it successfully: **HW lineage + SRC**
- framebuffer is available from `gp-5136`: **BIN**
- selector labels can therefore be emitted without resource injection: **strong implementation inference**
- final selector coordinates/style: **OPEN**
- background-clearing/repaint strategy: **OPEN**

## Remaining selector construction blockers

1. safe transient storage for `selector_active` and `selected_row`;
2. exact state-14 interception site with a clean continuation;
3. native background restore/clear path;
4. command adapter table, especially CLASSIC lifecycle entry.

The resource/font problem is closed.
