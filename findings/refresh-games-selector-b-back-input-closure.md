# Refresh Games selector input identity — B/Back closed

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **BIN input identity closed; selector state-dispatch mapping still open**

## Result

The frontend event translation table is already fully recovered and hardware-correlated.

For Player 1:

```text
physical    raw mask    UI event
SELECT      0x0020      0x0001
START       0x0010      0x0008
UP          0x0008      0x0010
DOWN        0x0004      0x0040
LEFT        0x0002      0x0080
RIGHT       0x0001      0x0020
A           0x0080      0x2000
B           0x0040      0x4000
L           0x0800      0x1000
X           0x4000      0x0400
Y           0x2000      0x0800
R           0x1000      0x8000
```

Therefore the selector can use the **translated frontend event word**, not raw controller bits:

```text
UP       0x0010
DOWN     0x0040
A        0x2000
B        0x4000
```

This closes the physical/event identity. It does **not** by itself prove every stock state assigns B semantic "Back"; our selector can explicitly assign B/0x4000 to its Back action while remaining in the normal frontend event domain.

## Why this is safer than raw polling

The normal input task already:
1. scans local controller streams;
2. merges RF state;
3. translates physical bits to frontend event masks;
4. publishes current/snapshotted Player 1 event words.

The selector should consume the translated event word just like stock frontend logic. It must not poll GPIO, serial input, or libretro state directly.

## Selector event table

```text
event 0x0010 (UP)
    selection = selection == 0 ? 7 : selection - 1
    redraw

event 0x0040 (DOWN)
    selection = selection == 7 ? 0 : selection + 1
    redraw

event 0x2000 (A)
    command = selection
    leave selector
    enter native Refresh command path

event 0x4000 (B)
    leave selector
    restore state 14 / User Menu
    redraw
    NO Refresh call
```

Left/Right/Start/Select/L/R/X/Y are ignored by this selector unless later native-menu archaeology gives a reason to preserve a stock behavior.

## Evidence boundary

- physical -> UI event translation: **BIN**
- L+SELECT composite `0x1001` physical reproduction: **HW**, corroborates translated-event model
- B -> UI event `0x4000`: **BIN**
- B meaning "Back" in the proposed Refresh selector: **DESIGN**
- exact stock state-14 B branch target: **OPEN** and not required to identify the button.

## Remaining gates

Input identity is no longer a blocker.

Remaining before construction:
1. map central frontend state dispatch and choose a safe selector-state interception;
2. choose native background/redraw path;
3. select safe ephemeral state storage;
4. verify selector-confirm -> native Refresh entry calling context;
5. byte-audit against Test106 cumulative firmware.
