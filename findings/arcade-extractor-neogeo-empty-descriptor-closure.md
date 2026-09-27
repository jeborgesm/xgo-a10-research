# Arcade extractor callback 0x804744AC closure

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **BIN CLOSED / OFFLINE REGRESSION CLOSED**

Fresh extraction had stopped at callback `0x804744AC`.

Direct inspection of exact firmware
`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`
identified its owner:

```
driver index 787
driver object 0x80AF2550
short name    neogeo
system        Neo Geo
ROM-info      0x804744AC
ROM-name      0x8047450C
ROM table     0x80AF25D8
count         25
```

This is not a new callback/macro form. The extractor rejected the ordinary
direct table because its `roms()` helper incorrectly required every descriptor
slot to have a non-empty name.

The exact Neo Geo BIOS table contains legitimate empty descriptors. Examples
include indices 5, 7, 10, 11, 17, 18, 19, 21, 22 and 23 with name empty and
length/CRC/type all zero. This agrees with the already pinned stock loader
semantics: descriptors with type/length/CRC zero are treated as satisfied.

The extractor was corrected to preserve an all-zero empty descriptor while
still rejecting a nameless descriptor carrying nonzero length, CRC or type.

A fresh independent mechanical sweep using the corrected rule traversed all
target callbacks successfully:

```
CPS1    154 / 154 parsed
CPS2    232 / 232 parsed
IGS      34 / 34 parsed
NEOGEO  258 / 258 parsed
failures 0
```

These counts are observations of this exact firmware, not compiler limits.

## Parent / board pointer spot-check

The same exact firmware also directly confirms the currently used BurnDriver
metadata offsets on representative drivers:

```
1941j   +0x04 -> "1941"    +0x08 -> NULL
orlegend +0x04 -> NULL      +0x08 -> "pgm"
mslug    +0x04 -> NULL      +0x08 -> "neogeo"
kof98    +0x04 -> NULL      +0x08 -> "neogeo"
1941     +0x04 -> NULL      +0x08 -> NULL
neogeo   +0x04 -> NULL      +0x08 -> NULL
```

Thus +0x04 parent and +0x08 board/dependency naming are directly supported for
the representative clone/PGM/NeoGeo cases used by the compatibility design.

No hardware claim is made. No Test05.
