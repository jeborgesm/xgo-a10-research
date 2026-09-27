# XGO stock FBA driver table and ROM-descriptor ABI — BIN closure

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **BIN CLOSED for driver enumeration; CPS1/CPS2/NeoGeo direct descriptor form closed; PGM special composition OPEN**

## Exact driver pointer table

Direct disassembly of the current XGO `BurnDrvGetText`-equivalent at
`0x8036F7D0` shows active-driver indexing into the pointer table at:

```
runtime 0x80A3D7F8
file    0x00A3D7F8
```

The table contains 1438 consecutive non-null driver pointers before the first
zero entry.

This is the authoritative enumeration anchor for compatibility-manifest
generation. A whole-binary heuristic scan is no longer needed.

The first entries independently validate the interpretation:

```
index 0 -> driver object whose short name is "1941"
index 1 -> "1941j"
index 2 -> "3wonders"
index 3 -> "3wonderu"
```

## Driver object fields used by the extractor

For the compiled XGO BurnDriver object generation:

```
+0x00  short-name pointer
+0x1C  system-name pointer
+0x40  ROM-info callback
+0x44  ROM-name callback
```

For 1941, the object begins at runtime `0x80A8B8E0`:
- +0x00 -> `"1941"`
- +0x1C -> `"CPS1"`
- +0x40 -> `0x804611D4`
- +0x44 -> `0x80461234`

The ROM-info callback directly materializes descriptor base
`0x80A8B968` and bounds the index to 12, exactly matching the previously
recovered 1941 descriptor contract.

## Exact target-family population

Enumerating the 1438 authoritative driver objects by their compiled system
string gives:

```
CPS1              133
CPS1 / QSound      21
CPS2              232
PGM                34
Neo Geo           258
```

For Refresh family purposes, CPS1 + CPS1/QSound form the CPS1 stock family,
PGM is the IGS family, and Neo Geo maps to NeoGeo.

## Direct descriptor representation

The generated ROM-info callbacks for all inspected/automatically decoded
CPS1, CPS1/QSound, CPS2 and NeoGeo target drivers expose a direct descriptor
base and count. The direct record generation matches the already-closed
1941 shape: 32-byte member name followed by size, CRC and type/flags.

A mechanical prototype successfully decoded all 644 target drivers in these
three Refresh families:

```
CPS1    154
CPS2    232
NeoGeo  258
total   644
```

No target driver in those three families failed callback/base/count recovery.

## PGM/IGS is a real exception

PGM must **not** be forced through the direct-record extractor.

Example: `orlegend` (driver-table index 1046) has ROM-info callback
`0x80493038`. That function references at least two data regions:

```
0x80B1746C  game-specific direct ROM records
0x80B1767C  composition/index metadata
```

and its ROM-name callback additionally references the common PGM region around
`0x80B173E8`.

Direct inspection shows `0x80B173E8` contains shared PGM ROM descriptors,
while `0x80B1746C` begins the game-specific `orlegend` records.

Therefore the stock PGM callback composes ROM metadata rather than exposing one
simple contiguous per-driver table. This is data-layout divergence underneath
the already-closed common stock FBA loader algorithm.

This corrects any over-broad interpretation of the earlier family-unified
loader finding:

> the **matching algorithm** is common, but the compiled driver callbacks are
> allowed to synthesize/compose their descriptor stream differently.

## Manifest-generator consequence

The exact-firmware manifest remains the selected architecture, but extraction
must follow the compiled driver callbacks rather than assume every family has
the 1941 inline table form.

Safe implementation split:

1. enumerate all drivers from `0x80A3D7F8`;
2. identify Refresh family from compiled system metadata;
3. CPS1/CPS2/NeoGeo: decode the proven direct callback form;
4. IGS/PGM: reproduce the callback's composed descriptor result only after its
   index/composition tables are closed;
5. retain the original type/flags word so required/optional classification can
   be derived without losing stock semantics.

No Test05 is authorized while PGM composition remains OPEN.
