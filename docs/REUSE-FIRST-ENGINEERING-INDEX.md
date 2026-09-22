# Reuse-first engineering index

Status: **mandatory preflight index** for XGO modification work.

This file exists because documentation is only useful if future work is forced to consult it. Before inventing a renderer, menu, overlay, persistence path, loader, scanner, input hook, or lifecycle transition, search this index and the linked source/findings first.

## UI / framebuffer / modal composition

### Interactive Mapper v19 — HW
Authoritative:
- `findings/interactive-mapper-handoff.md`
- mapper implementation/source under the mapper tooling lineage.

Reusable lessons:
- complete visual resource and dynamic selector can be separated;
- explicit modal entry/exit is safer than incidental activation;
- selector coordinates and static artwork must share geometry;
- legend: `A = OPEN / SAVE+PLAY`, `ARROWS = CHANGE`;
- final mapper visual resource occupied x=225..639 before v19 transform.

### Mapper v16 stock-layer suppression — BIN/HW lineage
Authoritative:
- `findings/interactive-xgo-mapper-v16-editor-overlay-diagnostic.md`

Reusable mechanism:
- draw the modal resource, then conditionally skip the underlying stock pause-menu row/highlight pass while mapper edit state is active.
- This is the first comparison target when a new modal visually leaks stock selection/highlight underneath it.

### Setup / Refresh Test05b–Test06 full-screen repaint — SRC/HW lineage
Authoritative source:
- `tools/game_lists/build_test05b_polished_refresh_menu.py`
- `tools/game_lists/build_test06_explicit_staged_refresh.py`
- `tools/game_lists/build_test06b_timed_status.py`

Reusable mechanism:
- existing source explicitly expands the Setup background refresh to a 640x480 RGB565 repaint before active-selector drawing.
- Contains preserved six-language 640x480 resource handling and known Setup renderer patch sites.
- This MUST be reviewed before any new attempt to make Refresh Games cover the whole screen.

### Audio OSD framebuffer/presentation — HW/BIN/SRC
Authoritative:
- `findings/audio-osd-framebuffer-hook-and-storage-surface.md`
- `findings/audio-osd-v3-sparse-main-menu-repaint-candidate.md`

Reusable facts:
- frontend framebuffer pointer `0x80C33364`;
- width `0x80C3395C`, height `0x80C33958`;
- presentation `0x8035C398`;
- mapper marker work already proved RGB565 writes through the frontend surface.

### Root framebuffer geometry — BIN
Authoritative:
- `findings/lcfg-runtime-board-config.md`

Reusable facts:
- logical framebuffer 640x480 RGB565;
- pitch 0x500;
- allocation 0x96004;
- clear size 0x96000.

## Current Refresh selector — HW

Protected checkpoint: **Test119**.

Authoritative:
- `HANDOFF-CURRENT.md`
- `tools/refresh_selector/README.md`
- `tools/refresh_selector/selector_module_v0.S`
- `tools/refresh_selector/build_test119_from_test106.py`
- `findings/refresh-selector-command-and-reentry-closure.md`
- `findings/refresh-post-operation-reentry-selection-closure.md`

Do not alter Test119 lifecycle merely to solve presentation.

## Rejected full-screen experiments

### Test120 — HW FAIL
Introduced `memset` plus additional footer/text helper inside current selector renderer. Refresh framebuffer became visible only after Volume OSD presentation and controls were unresponsive.

### Test121 — HW FAIL
Tried to enlarge/reposition the current Test119 hand-drawn fill loop. Device became completely unresponsive on entering Refresh.

**Rule:** no more local immediate/loop experiments on the Test119 backdrop until the existing higher-level Mapper and Test05/06 composition mechanisms have been compared against the current selector.

## Mandatory reuse preflight

Before writing a new patch, builder, or candidate, answer in the finding/source commit:

1. What existing XGO implementation solves the same or nearest problem?
2. What source file implements it?
3. What HW/BIN evidence established it?
4. Can that mechanism be reused without changing the protected lifecycle?
5. If not, what exact incompatibility prevents reuse?

A hardware candidate is not authorized if these questions have not been answered.

## Principle

**Search source before bytes. Reuse before invention. Hardware tests validate a bounded unknown; they do not rediscover mechanisms already preserved in the repository.**
