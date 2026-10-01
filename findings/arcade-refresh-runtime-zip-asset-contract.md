# Arcade Refresh - runtime ZIP asset contract

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: IMPLEMENTATION CONTRACT CLOSED; DEVICE CODE NOT YET EMITTED

Arcade differs from the console materializer because a successful import owns
two physical launch assets:
- /ARCADE/bin/<driver>.zip
- /ARCADE/<friendly>.zfb

The source ZIP under the family import directory is retained.

## Required order

For each source:
1. validate basename and .zip extension;
2. derive driver basename and friendly title;
3. inspect /ARCADE/bin/<driver>.zip;
4. if absent, copy source there with exact-count checked bounded transfers;
5. reopen destination and byte-compare against source;
6. if present initially, byte-compare against source before reuse;
7. same basename with different bytes is a hard collision; never overwrite;
8. only after runtime ZIP convergence may the ZFB be created/reused;
9. only after both physical assets converge may catalog append begin.

## Why byte identity, not only size/CRC

No new hash/CRC ABI is required in the device helper. A bounded streaming
byte comparison is deterministic, avoids trusting archive metadata, and fits
the same stock fopen/fread/fwrite/fclose primitives already exercised by the
golden materializer and Test105/Test106 catalog verification lineage.

The reference transfer chunk is 0x2000, matching the golden Test75 preview
copy buffer scale. Runtime code may reuse that bounded workspace if lifetime
analysis confirms it is free at this phase.

## Failure semantics

- source open/read failure: item fails;
- destination create/write/short-write failure: item fails;
- post-copy reopen/compare failure: item fails;
- existing destination different bytes: collision/fail, never overwrite;
- existing destination identical bytes: reuse;
- source is never deleted.

A failed copy may leave an unindexed physical file. On the next Refresh:
- if complete and identical, reuse it;
- if incomplete/different, fail collision rather than overwrite it.

This conservative rule avoids destructive repair in ordinary Refresh.
Maintenance/reconciliation can be a separate operation later.

## Relationship to transaction marker

Runtime ZIP and ZFB convergence occur before catalog ACTIVE. They are not
rolled back by the catalog transaction.

This is deliberate: unindexed but valid physical assets are harmless and
reusable; catalog entries whose launch assets do not exist are forbidden.

## Host reference

tools/arcade_refresh/runtime_zip_contract.py implements the same decision
surface for offline tests:
- CREATED
- REUSED
- COLLISION
- FAILED

The device implementation should mirror this contract using stock firmware
file I/O wrappers and exact-count checked bounded transfers.
