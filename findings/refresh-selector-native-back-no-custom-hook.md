# Refresh selector UI gate — eliminate custom B hook

Date: 2026-09-21
Status: **design simplification grounded in stock lifecycle**

A dedicated B-event interception is not required for the first selector implementation.

## Reason

The selector remains hosted inside frontend state 14. Its private `selector_active` flag changes presentation/navigation interpretation but does not create a new frontend state.

Therefore stock B/Back can continue to perform its native state-14 exit behavior. The selector does not need to reinterpret B as an internal "Back row" command.

When the user returns to state 14 later, selector entry initializes:
```text
selector_active = 1
selected_row = 0
refresh_command = -1
```
so stale selector state is not required for correctness.

For an explicit internal return to the ordinary User Menu, the selector can use a rendered `< Back` row only if later UX testing demands it; current requested eight-module layout does not include Back.

## Safety advantage

Removing the custom B hook means the first UI proof needs no new controller/event interception at all:
- Up/Down: stock state-14 navigation;
- A: stock state-14 confirm seam;
- B: stock state-14 Back behavior.

The replacement only needs:
1. conditional navigation terminal 3/7;
2. row-3 entry into selector mode;
3. selector-active renderer;
4. selector-active confirm substitution.

This further reduces perturbation of the frontend.

## Evidence boundary

- state14 ownership and normal Back lifecycle: **BIN/HW behavior lineage**
- exact physical B -> translated event 0x4000: **BIN**
- no need to intercept B while preserving native exit semantics: **INF/DESIGN**
- hardware behavior of B from the new selector overlay: **OPEN until UI gate**
