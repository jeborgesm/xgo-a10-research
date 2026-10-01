# Arcade compatibility gate — stock FBA family-unified loader closure

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **ARCHITECTURE CLOSED; implementation substrate still requires descriptor access**

## Question

Must CPS1, CPS2, IGS/PGM and NeoGeo each receive a different ZIP-compatibility
algorithm?

## Closure

No.

Existing stock-XGO archaeology identifies one installed stock FBA libretro
`retro_load_game` entry at `0x8036D658`. The stock arcade wrapper installs
that single callback into `gfn_retro_load_game`; there are not four
family-specific libretro load callbacks.

The source reconstruction pins that loader to the later
`Aftnet/fbalpha@621e371` archive-loader generation and explicitly preserves
its common `open_archive()` / `archive_load_rom()` behavior across drivers.

The loader diagnostics recovered from XGO are generic FBA diagnostics, including
archive parsing, ROM-index search, wrong-CRC filename fallback and unresolved
ROM failure.

Therefore the compatibility **algorithm** is family-unified:

1. select the active compiled FBA driver from the imported ZIP basename;
2. enumerate that driver's required ROM descriptors;
3. enumerate archive members;
4. satisfy each required ROM using the same stock archive-loader matching
   semantics already BIN-closed for CPS1;
5. publish only if the complete driver contract resolves.

CPS1/CPS2/IGS/NeoGeo differ in driver data, not in the frontend validation
algorithm.

## Important limitation

This does **not** mean the Refresh helper may assume a raw descriptor-table
layout and parse arbitrary firmware structures directly.

The remaining implementation problem is obtaining:
- driver selection;
- required ROM descriptor iteration;
- archive-member CRC/name/size data;

without duplicating an opaque stock-internal layout incorrectly.

Preferred implementation hierarchy:

1. reuse callable stock FBA driver/ROM-query functions if their ABI can be
   bounded safely;
2. otherwise generate a compact compatibility manifest offline from the exact
   firmware and consume that manifest in the Refresh helper;
3. do not hand-maintain per-game tables.

An offline generated manifest is acceptable only if it is tied to the exact
firmware hash and derived mechanically from the same compiled driver contracts.

## Family consequence

The prior concern that each family might require a distinct descriptor traversal
is narrowed: family-specific validation code is not justified by current
evidence.

The four-family Refresh may share one validator implementation while supplying
family identity/allowed-driver data.

## Publication invariant

No compatibility verdict may create:
- `/ARCADE/bin/<stem>.zip`;
- `<title>.zfb`;
- `.refresh-set/<title>.zfb`;
- catalog rows;

until every required ROM resolves.

This invariant is independent of the still-open quarantine rename primitive.
