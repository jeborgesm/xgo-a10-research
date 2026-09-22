# Refresh Games navigation and repaint closure

Date: 2026-09-20
Status: **offline selector mechanics closed enough for source construction**

## Native state-14 navigation seam

Historical Test05 binary/source archaeology identifies the two terminal constants in the stock User Menu linear selector:

```text
0x80359AA4  up-wrap terminal value
0x80359E60  down/forward terminal value
```

Stock values are both 2. Test05 changed both to 3 and hardware demonstrated stable 0..3 wrapping.

This proves the state-14 lifecycle already contains a linear previous/next selector. We do not need a controller-task modal.

For the final Refresh Games selector, however, we should **not** globally change these stock constants to 7, because that would expose rows 3..7 to the normal three-item User Menu whenever the overlay is inactive.

Instead, intercept the same navigation decision only when private `selector_active != 0`:

```text
UP:
    selected_row = (selected_row == 0) ? 7 : selected_row - 1

DOWN:
    selected_row = (selected_row == 7) ? 0 : selected_row + 1
```

When inactive, execute the exact original state-14 instructions and retain terminal 2.

## Confirm

A/confirm is already closed at the `0x80359E94` seam:
- inactive -> stock dispatch;
- active -> consume private selected_row, clear selector_active, enter native Refresh at `0x807DB5CC`.

## Cancel

Translated frontend B is `0x4000`.

The final overlay owns B semantically while active:

```text
B:
    selector_active = 0
    selected_row = 0
    mark/redraw stock User Menu
    do not enter Refresh
```

This is deliberately an overlay-owned cancel operation; no claim is made that every stock state assigns B the same meaning.

## Repaint path

The framebuffer geometry and presentation ABI are already recovered:

```text
0x80C33364 current framebuffer pointer
0x80C3395C width
0x80C33958 height
0x8035C398 run_screen_write
```

Stock User Menu redraw/re-entry is `0x80359ABC`.

Historical Test05 also proved the setup background can be recopied before selector drawing; its corrected variants repainted through row 429 while preserving the stock footer.

The final selector therefore does not need persistent custom raster resources. Two safe repaint operations are available:

### Enter / row change
1. let state-14 restore/repaint its known background surface;
2. draw REFRESH GAMES title + eight rows with stock `TEXT_DRAW 0x803528A4`;
3. present through normal frontend presentation.

### Cancel
1. clear selector_active;
2. jump to stock User Menu redraw/re-entry `0x80359ABC`;
3. no selector text remains after the stock repaint.

No guessed resource triplet is introduced.

## Eight rows fit

The logical frontend is 640x480. Eight rows do not require scrolling.

A conservative text layout can use approximately:
- title y ~ 70
- rows y ~ 120 + row*35

which places row 7 around y=365 and leaves the stock lower/footer area available.

Coordinates remain implementation constants, not architectural dependencies.

## Remaining construction work

The interaction model is now complete enough to build the module in source form:

```text
enter selector -> active=1,row=0
UP/DOWN       -> wrap 0..7 + redraw
A             -> module=row; active=0; native Refresh
B             -> active=0; stock User Menu redraw
```

Remaining work is engineering/audit rather than unknown UI semantics:
1. choose exact cave placement against Test106;
2. assemble source-preserved selector/render/adapter code;
3. map command IDs to only the module adapters that are actually authorized;
4. byte-audit every firmware delta;
5. only then decide whether a hardware UI-only gate is warranted.

## Evidence boundary

- state-14 linear selector terminal sites: **BIN**
- 0..3 modification/wrap behavior: **SRC + HW lineage**
- frontend framebuffer/presentation globals: **BIN + HW lineage**
- stock User Menu redraw target: **BIN + HW lineage**
- stock text renderer: **BIN + HW lineage**
- overlay-local B cancel semantics: **DESIGN**
- eight-row no-scroll geometry: **DESIGN, arithmetic fit**
