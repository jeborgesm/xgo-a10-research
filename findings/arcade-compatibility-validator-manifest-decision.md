# Arcade compatibility validator — stock query ABI vs exact manifest decision

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **IMPLEMENTATION DIRECTION LOCKED: exact-firmware manifest**

## Reuse-first result

The exact XGO stock FBA loader entry and driver-name query path are BIN-closed:
- `retro_load_game = 0x8036D658`;
- candidate driver name query = `0x8036F7D0`;
- active driver/count state is stock-FBA global state.

However, repository archaeology does not yet contain BIN-closed callable ABIs for
the equivalent of:
- `BurnDrvGetRomInfo`;
- `BurnDrvGetRomName`;
- archive enumeration/CRC query.

Calling internal stock FBA routines from an external Refresh helper would also
mutate/use global `nBurnDrvActive` state belonging to the resident stock core.
That expands the Refresh ABI surface and creates a frontend/core-state coupling
that is unnecessary for a pre-publication validator.

Therefore option 1 (live stock-query ABI reuse) is rejected for the first
implementation unless future archaeology independently closes a side-effect-free
query interface.

## Selected implementation

Use an **offline mechanically generated compatibility manifest** tied to the
exact firmware.

The manifest is data, not a hand-maintained ROM database.

Generator inputs:
- exact `bios/bisrv.asd` SHA-256;
- BIN-recovered compiled driver identities;
- BIN-recovered required ROM descriptors.

Per driver record:
- family/list identity;
- exact short driver name used by XGO basename selection;
- required ROM count;
- for each required ROM:
  - expected filename;
  - expected size;
  - expected CRC32;
  - exact type/flags word retained for required/optional classification.

The validator then needs only:
1. ZIP central-directory enumeration;
2. CRC/name/size comparison;
3. manifest lookup by family + stem.

No stock FBA global state is touched.

## Firmware binding

A generated manifest must carry the exact source firmware SHA-256 and generator
version/schema. Packaging must fail if the manifest was not generated from the
firmware baseline declared by the candidate.

This prevents silently validating against a different FBA driver generation.

## Matching semantics

For each required descriptor:
1. seek an archive member with matching required CRC (and expected size where
   the stock descriptor contract requires it);
2. if CRC resolution fails, seek the expected filename using the stock
   filename-fallback semantics;
3. unresolved required descriptor => incompatible.

Optional/non-required descriptor semantics must be derived from the compiled
type flags before the generator is considered complete.

## Why this is preferable to calling stock internals

- deterministic and offline auditable;
- no dependency on hidden stock-core global state;
- no mutation of `nBurnDrvActive`;
- no family-specific parser in the on-device helper;
- exact XGO data rather than a generic MAME/FBA version assumption;
- positive/negative compatibility can be regression-tested without ROM payloads.

## Remaining generator boundary

The 1941 table proves the record shape for that driver, but a generic extractor
still needs a mechanically reliable way to enumerate all relevant compiled
driver records and classify required versus optional entries.

Do not implement a heuristic whole-binary scan and call it authoritative.
Anchor extraction through the compiled driver metadata/table relationships or
another BIN-closed index.

Until that enumeration is closed, no Test05.
