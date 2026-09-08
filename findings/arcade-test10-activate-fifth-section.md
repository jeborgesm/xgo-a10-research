# Arcade Test10 — activate inherited fifth Arcade section via Foldername.ini

Date: 2026-09-07
Branch: `research-game-list-arcade-expansion`

Status: **hardware candidate; NOT golden**

## Corrected architecture

Direct hardware observation shows four visible Arcade sections.

The preserved XGO `Resources/Foldername.ini` nevertheless defines twelve section lines:

```text
0  ROMS
1  FC
2  SFC
3  MD
4  GB
5  GBC
6  GBA
7  ARCADE
8  ARCADE
9  ARCADE
10 ARCADE
11 ARCADE
```

but its control line is:

```text
11 7 0
```

Established SF2000-family documentation identifies those three fields as:

```text
active section count / boot-default section / settings section
```

Therefore XGO is configured to expose IDs 0..10 only. The fifth inherited ARCADE line is physically present in the config but excluded by the active-section count.

This exactly explains the user's hardware observation and the dormant firmware resource-table entry:

```text
list ID 11 -> None / None / None
```

## Test10

Test10 changes only the active-section count:

```text
11 7 0
   ->
12 7 0
```

and supplies a valid one-entry `Resources/None` catalog for list ID 11.

No firmware modification is made.

The page contains one `Pac-Man.zfb` reference to `ARCADE/bin/pacman.zip`.

No ROM image is included.

## Why this is lower risk than firmware patching

The fifth `FF8000 ARCADE` definition already exists in XGO's own `Foldername.ini`.
The list-ID-11 resource pointers already exist in XGO's own firmware.
Test10 only makes the configuration's active-section count include the already-defined final section.

## Hardware interpretation

If a fifth Arcade section becomes visible, the config/count hypothesis is proven.

If its list shows Pac-Man, list ID 11 and `Resources/None` are both proven.

If Pac-Man then launches with a compatible user-supplied `pacman.zip`, the stock XGO FBA classic Pac-Man driver and a native Classic Arcade presentation path are proven simultaneously.

If the fifth section causes a frontend failure, restore golden Test08. No firmware bytes or existing catalogs are changed by this probe.


## Exact candidate

```text
xgo-arcade-test10-fifth-section-pacman.zip
size       4,921,962 bytes
SHA-256    1a55e95702c225788cc1ed3e14a6dca294f2d30c75c3b6e3681dbc4e24e9f759
Foldername.ini SHA-256
           28ea468c2321f49b115be41e36ecab49b017a838f18502f7308ec52039faa2df
Resources/None SHA-256
           27387fdfb31fc2d3d14070578782484e85ded64b0f85c49dff9f5dab2d932159
Pac-Man.zfb SHA-256
           5fd31a661e852c07e526d0b762a1154400184fd31723af6ebc279156e1db1aa1
```

The package was built from the exact golden Test08 ZIP and its firmware remains unchanged.

Exact builder:
`tools/game_lists/build_arcade_test10_fifth_section_pacman.py`
