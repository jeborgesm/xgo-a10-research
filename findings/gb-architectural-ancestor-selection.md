# GB Refresh architectural ancestor selection

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Status: **design gate closed from preserved HW evidence; no hardware candidate yet**

## Why this record exists

Before another GB/GBC/GBA implementation, choose the closest already-proven
ancestor by mechanism rather than by test chronology.

## Component ancestry

| Component | Closest proven ancestor | Evidence / reason |
|---|---|---|
| import/art/meta enrichment | Test74 SFC / Test75 FC | HW-proven source + JPG + TXT -> packaged wrapper -> visible entry -> launch |
| two-character native extension | Test97 MD | HW proved inherited FC/SFC four-byte suffix geometry was wrong for `.md`; bypass of only redundant dot gate produced Games Updated and playable imports |
| short-extension stem handling | MD Tests93-101 record | inherited helper removed four suffix bytes; `.md` needs three. This is directly relevant to `.gb`, which also has a two-character extension and three-byte suffix including dot |
| generated packaged wrapper | stock common packaged-console contract | GB output is `.zgb`; preview is 144x208 LE RGB565 / 0xEA00 prefix under common launcher evidence |
| catalog identity | GB descriptor | `vdsdc.tax / umboa.nec / qdvd6.bvs`, count cache `0x80D28964` |
| final live frontend/catalog lifecycle | MD later architecture | custom isolated catalog writes can leave frontend workspace stale; preserve lifecycle lesson rather than rediscovering it |
| raw top-level discovery | Test08 | supporting evidence only; NOT the parent architecture for enriched import |

## Critical GB/MD correlation

For the parser/materializer, GB and MD have the same suffix geometry:

```
MD source: .md   = 3 bytes including dot
GB source: .gb   = 3 bytes including dot
```

The FC/SFC ancestor assumed:

```
.nes / .sfc = 4 bytes including dot
```

The preserved MD investigation proves that blindly cloning the FC/SFC checks
creates a false four-byte pattern. For MD it effectively expected:

```
L-4 '.'
L-3 '.'
L-2 'm'
L-1 'd'
```

GB must therefore NOT be produced by merely replacing `.sfc` with `.gb` in
the Test74 helper. The GB source-extension gate and stem length must inherit the
MD short-extension correction.

## GB target contract

```
/GB/import/<stem>.gb
/GB/art/<stem>.jpg       optional; .jpeg where inherited helper supports it
/GB/meta/<stem>.txt      optional
          |
          v
/GB/<friendly-or-basename>.zgb
          |
          v
GB stock catalog / live frontend lifecycle
```

Output wrapper suffix `.zgb` is four bytes including dot; the special geometry
problem is the **input `.gb` suffix**, not the generated wrapper suffix.

## What must be reused, not redesigned

1. Test74/Test75 JPEG decode/scale and 144x208 RGB565 preview generation.
2. Existing STORE WQW writer / packaged-wrapper construction.
3. Existing import/art/meta naming convention and source-retention/no-overwrite semantics.
4. MD-proven two-character input-extension handling lesson.
5. GB-specific descriptor paths/catalog identity already preserved in source.
6. MD lifecycle findings concerning persistent catalog vs live frontend state.

## Explicit exclusions

- Do not use Test124-126 raw-ROM scanner work as the GB enrichment parent.
- Do not require FC/SFC/MD scans before GB.
- Do not invent another extension parser before comparing the exact MD helper.
- Do not produce a hardware candidate until the exact MD materializer bytes/source
  used by the HW-positive Test97 path have been recovered and the GB substitutions
  are enumerated.

Test08 remains useful archaeology but is not the implementation lineage for this feature.
