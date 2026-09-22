# Refresh Games selector input-loop architecture

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **offline design narrowed; no hardware candidate**

## Correction to the previous search direction

A byte-for-byte reusable stock "eight arbitrary command rows" input loop has not surfaced in the preserved findings. Search and the game browser have variable-row navigation, but their records are game/catalog objects. User Menu has command semantics but only a three-card bitmap grammar.

Therefore forcing one of those loops to become the Refresh selector would import the wrong ownership model.

The safer reuse boundary is lower-level:

- reuse the stock frontend's already-proven controller event identity;
- reuse the stock text renderer;
- reuse the stock state-machine dispatch/redraw cadence;
- implement only the tiny selector state transition logic required for eight command rows.

This is materially smaller than the Test84 mapper modal and does not poll/block inside a modal loop.

## Proven controller event identity

The XGO controller work already closes the directional/confirm bit identities:

```text
0x0010  Up
0x0020  Right
0x0040  Down
0x0080  Left
0x2000  A / confirm
```

Start/Select are not needed by the selector.

For this screen:
- Up decrements selection with wrap 0 -> 7;
- Down increments selection with wrap 7 -> 0;
- A confirms;
- B/cancel must be taken from the **existing frontend cancel event path**, not guessed from emulator/libretro mappings.

The exact frontend B/cancel event identity remains to be pinned from the native state handler before code generation.

## Non-modal state-machine design

Do not build:

```text
enter selector
   -> while(1) poll controller
   -> draw
   -> block frontend
```

That is the risky modal grammar used by prior experiments.

Build:

```text
normal frontend frame
      |
      v
state dispatch says REFRESH_SELECTOR
      |
      +-- consume one already-decoded event
      |
      +-- update selection if needed
      |
      +-- render current frame with stock primitives
      |
      +-- return to normal frontend loop
```

Thus Audio OSD, normal event cadence, and frontend ownership remain intact.

## Selector state

Only two pieces of state are required:

```c
uint8 refresh_selection;  // 0..7
bool  refresh_selector_active;
```

A dedicated frontend state value is preferable to overloading list IDs or User Menu selection. However, no new numeric state should be assigned until the central state dispatch table is mapped for a demonstrably unused/safely interceptable path.

The command ID and visual selection can be the same 0..7 value.

## Render grammar

Use `0x803528A4` for labels. No per-language 640x480 label bitmaps.

Conceptual frame:

```text
+------------------------------------------------+
|                  REFRESH GAMES                 |
|                                                |
|              > Famicom                         |
|                Super Famicom                   |
|                Mega Drive                      |
|                Game Boy                        |
|                Game Boy Color                  |
|                Game Boy Advance                |
|                Arcade                          |
|                Classic                         |
|                                                |
|              A Select       B Back             |
+------------------------------------------------+
```

The highlight should initially be text/cursor based, not a custom framebuffer overlay. Exact native cursor glyph/resource remains OPEN; a simple stock-font prefix is safer than inventing another graphics hook if no native cursor primitive is recoverable.

## Confirm path

```text
A on row N
   |
   v
refresh_selector_active = 0
refresh_command = N
   |
   v
enter native Refresh function 0x807DB5CC
   |
   v
native frame/workspace initialization
   |
   v
dispatch @ 0x807DB67C
```

CLASSIC then uses the already-closed continuation:

```text
N == 7
 -> s5 = 0
 -> j 0x80A38000
 -> /CLASSIC/refresh.xgc
 -> native status continuation
 -> native Refresh epilogue
```

## Cancel path

Cancel must simply restore User Menu state 14 and redraw. It must not enter Refresh and must not mutate any catalog state.

## Why this is not another "hacky modal"

The old diagnostic UI modified an existing Settings/card screen and mixed selection, execution and presentation.

The new architecture separates them:

```text
presentation state
      |
      | command ID only
      v
execution state
      |
      v
native Refresh lifecycle
```

No fake catalog.
No fake Search records.
No direct CLASSIC call.
No guessed resource triplet.
No blocking controller loop.
No full-screen localized bitmap rewrite.

## Remaining binary gates before construction

1. Pin native frontend B/cancel event identity from a stock frontend handler.
2. Map central state dispatch sufficiently to choose a safe selector-state interception strategy.
3. Map a stock background/redraw entry suitable for the selector.
4. Locate safe storage for two bytes/words of ephemeral selector state, or keep them in an already-proven injected data cave without colliding with Mapper/OSD code.
5. Confirm the Refresh entry can be entered from the selector's normal frontend dispatch context rather than called from an arbitrary nested renderer.

Until those five are closed, no hardware package.
