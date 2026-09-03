# GB300 v1 KeyMapInfo record semantics

## Status

**Externally corroborated and consistent with the binary lift.**

This note tightens the target for the native mapper mutation site recovered in `gb300-v1-native-mapper-handler-and-commit-path.md`.

Independent GB300 firmware documentation describes the on-disk `Resources/KeyMapInfo.kmp` representation in enough detail to resolve the 4-byte mapper record:

```text
uint16_t logical_assignment;
uint16_t autofire_flag;
```

The logical assignment is stored first, followed immediately by the autofire/turbo state.

For most systems, the six physical slots are persisted in this order:

```text
X, Y, L, A, B, R
```

The documented GBA entry is an exception and is stored as:

```text
L, R, X, A, B, Y
```

The GB300 editor also contains known visual L/R and GBA X/Y presentation bugs, so UI-highlight order must not be assumed to equal physical save order without tracing the native index transformation.

## Binary consequence

The stock writer previously recovered writes:

```text
84 records * 4 bytes = 336 bytes
```

which is:

```text
7 systems * 12 records/system * 4 bytes/record
```

The external format description explains the 12-record block precisely: six physical-button records are duplicated immediately for the second player.

Thus each 48-byte system block is:

```text
player 1: 6 * 4 bytes = 24 bytes
player 2: 6 * 4 bytes = 24 bytes
--------------------------------
                         48 bytes
```

For a mapper-selected physical slot `slot` in the first-player half, the native mutation address must therefore reduce to:

```text
system_base + slot * 4
```

with:

```text
+0: uint16 logical assignment
+2: uint16 autofire flag
```

This materially narrows the next disassembly search. We should look around the mapper state machine and the three persistence callers for halfword stores (`sh`) whose address expression uses the six-position mapper selection, normally scaled by four. A logical-assignment change should hit offset `+0`; turbo toggling should hit offset `+2`.

## Known assignment encoding examples

The external documentation records these assignment values among others:

```text
0x0800
0x0000
0x0A00
0x0B00
0x0900
0x0100
```

Their semantic meaning depends on the emulated system. For example, FC uses `0x0800` for A and `0x0000` for B, while SFC additionally uses `0x0A00`/`0x0B00` for X/Y and `0x0900`/`0x0100` for L/R.

The autofire field is documented as logically odd/even:

```text
odd  -> autofire enabled
 even -> autofire disabled
```

with stock normally using `0x0100` for enabled and `0x0000` for disabled.

## Implication for XGO transplant

This reinforces the architecture already chosen for XGO:

```text
GB300 navigation + assignment/turbo behavior
        |
        v
XGO active 48-byte per-game map
        |
        +-- selected physical slot = base + slot*4
        +-- logical assignment   = +0 halfword
        +-- turbo state          = +2 halfword
        |
        v
set_keymap()
        |
        v
existing per-game <game>.kmp persistence
```

We still should not port GB300's global `KeyMapInfo.kmp` writer. Only the interaction semantics and record mutation behavior are useful.

## Next exact lift target

Search the GB300 native mapper region for:

1. an `sh` into the approximately `0x80ae8c70` global KeyMapInfo table,
2. an address calculation using the six-position selection multiplied by four,
3. a companion `sh` at address `+2` for turbo,
4. the logical-value cycling source/table feeding the first halfword store,
5. the transformation from visual slot index to persisted physical slot, especially the documented L/R and GBA anomalies.

## External corroboration

Source: nummacway's GB300 technical documentation, `KeyMapInfo.kmp` section:

https://nummacway.github.io/gb300/
