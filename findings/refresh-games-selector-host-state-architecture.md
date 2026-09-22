# Refresh Games selector host-state architecture

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **offline architecture narrowed; no hardware candidate yet**

## Finding

The safest selector architecture is not a new frontend state.

The main frontend state byte is `0x80C33980`. Existing binary archaeology maps:

```text
0..11  catalog/list states
12     Favorites
13     History
14     User Menu / Setup
15     Search
```

Dispatch around `0x80357768` explicitly treats 13/14/15 as special. Therefore an invented state 16 has no proven semantic contract and is rejected.

## Proven state-14 surface

The User Menu implementation already exposes a compact, well-mapped control surface:

```text
0x80359AA4  navigation up-wrap bound
0x80359ABC  User Menu redraw/re-entry
0x80359B1C  selector-render coordinate path
0x80359E60  navigation down bound
0x80359E94  confirm-action dispatcher
0x80359E98  row-0 branch -> 0x80357468
0x80359EA8  row-2/fallback dispatch surface
0x80359EB0  stock TV-system path
```

Historical Test05 proved that this surface can be modified coherently enough to create a fourth command without requiring a new frontend state. That old 2x2 UI is **not** the desired final UX; only its binary mapping is reused.

## Selected architecture

Keep frontend state 14 active while a transient selector-active flag changes the state-14 presentation/input subpath:

```text
state 14 / User Menu
       |
       +-- normal ----------> untouched stock User Menu
       |
       +-- selector-active --> REFRESH GAMES list
                                |
                                + UP    0x0010
                                + DOWN  0x0040
                                + A     0x2000 -> command
                                + B     0x4000 -> cancel
```

This preserves:
- central frontend state dispatch;
- normal input translation/task;
- state 14 lifecycle;
- stock User Menu behavior whenever selector-active is false.

It avoids:
- invented state 16;
- guessed dormant resources;
- Test90/91 resource injection;
- raw controller polling;
- mapper modal;
- direct CLASSIC bootstrap call;
- returning to the old Settings-card selector as the final UI.

## Important distinction from Test05

Test05 changed the visible User Menu itself into a 2x2 four-card screen.

The new design does **not** do that.

The intended final transition is:

```text
stock User Menu
    |
    | select REFRESH GAMES command
    v
same valid state-14 lifecycle
but selector-active presentation
    |
    v
+--------------------------------+
|         REFRESH GAMES          |
|--------------------------------|
| > Famicom                      |
|   Super Famicom                |
|   Mega Drive                   |
|   Game Boy                     |
|   Game Boy Color               |
|   Game Boy Advance             |
|   Arcade                       |
|   Classic                      |
+--------------------------------+
```

B clears selector-active and returns to the untouched User Menu redraw path.

A converts the selected row into a command ID and enters the native Refresh command path.

## Current evidence boundary

- state byte/address and 0..15 map: **BIN**
- state-14 renderer/navigation/confirm addresses: **BIN**
- historical four-command modification of that surface: **SRC/HW lineage evidence**
- translated UP/DOWN/A/B event masks: **BIN**
- selector-active state-14 overlay: **DESIGN**
- exact selector drawing primitive and scratch byte: **OPEN**
- exact final entry command for each Refresh target: **OPEN until adapter construction closes it**

## Construction gates remaining

1. identify a safe transient byte/word that is not persisted and is not owned by emulator runtime;
2. reuse a native text/list drawing grammar rather than shipping eight custom raster cards;
3. intercept state-14 input only while selector-active is true;
4. bind command IDs 0..7 to the native Refresh adapter table;
5. preserve Test106 firmware deltas byte-for-byte outside the audited patch surface.

No hardware test is justified yet.
