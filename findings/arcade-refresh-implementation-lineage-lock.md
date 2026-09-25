# Arcade Refresh — implementation lineage lock

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: IMPLEMENTATION RULE — SUPERSEDES MD/TEST106 DETOUR

## Decision

Arcade Refresh will be implemented from the newest cumulative HW-proven handheld
Refresh architecture, not from the Test106 MD transaction experiment.

Immediate ancestors:

1. Final GBA/GBC golden propagation for invocation/lifecycle:
   materializer -> explicit 2642-byte catalog helper -> common native status.
2. Final GB 2642-byte explicit catalog helper for catalog stable-append mechanics.
3. Test75 materializer for three-character source-suffix/JPEG/metadata machinery.
4. Direct four-family ZFB byte proof for Arcade wrapper output.
5. Current cumulative firmware command 6 as the isolated new dispatcher slot.

Test106 ACTIVE/CLEAN, backup/rollback, 7000-byte Stage2, and per-family .catalog
ledger are NOT part of the Arcade implementation unless a concrete Arcade
failure later demonstrates a need for them.

The previously committed guarded Stage2 builder is retained only as historical
research evidence. Its *.partial outputs are not candidates and must not be
used by the Arcade build.

## Current proven catalog contract to preserve

Final GBA/GBC implementation mechanically specialized the final HW-proven GB
2642-byte explicit merge helper:

GB ancestor SHA:
66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb

The helper:
- scans the target system root for generated wrappers;
- compares exact wrapper filenames against slot0;
- appends only missing identities;
- preserves existing order/indices;
- updates all three catalog slots synchronously;
- invalidates the known list count cache;
- returns changed/no-change/failure to the current Refresh lifecycle.

For Arcade, the direct cache invalidation write must be omitted until an exact
Arcade cache location is BIN-proven. Normal page re-entry is the first-candidate
visibility mechanism.

## Four-family issue

A single shared /ARCADE root cannot be independently scanned by four catalog
helpers because all families use .zfb and ZFB contains no family tag.

Therefore family separation must occur before catalog merge.

The authoritative user input already provides that separation:
/ARCADE/CPS1/import
/ARCADE/CPS2/import
/ARCADE/IGS/import
/ARCADE/NEOGEO/import

The Arcade materializer/orchestrator must retain the exact list of wrappers
successfully produced/reused for each family during that invocation and feed
only those identities to the matching family catalog operation.

Do not solve this by reintroducing the Test106 persistent .catalog marker
filesystem solely to accommodate its older directory scanner.

The exact handoff mechanism between materializer and catalog helper is the one
remaining implementation detail to close. Prefer the smallest bounded
transient representation that can be produced by the materializer and consumed
by a mechanically adapted 2642-byte GB/GBA-style merge helper.

## Scope lock

No more broad ancestry research before construction.
No transaction framework work.
No speculative Arcade cache addresses.
No CLASSIC/list11 changes.
No changes to commands 0..5 or 7.
No firmware candidate until helper byte-delta audits pass.
