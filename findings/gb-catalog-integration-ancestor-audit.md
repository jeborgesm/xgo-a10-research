# GB catalog integration — proven ancestor audit

Date: 2026-09-23
Branch: `research-refresh-gb-gbc-gba`
Status: **ARCHITECTURE CLOSED / exact helper-byte derivation pending artifact recovery**

## Evidence used

HW:
- Test74 SFC explicit catalog merge passed single + three-game enrichment.
- Test75 FC explicit catalog merge passed a five-game batch, launch, artwork repair,
  and stable reuse without duplicate catalog records.
- Test97 MD ultimately produced a coherent 839/839/839 triplet and working frontend
  from a coherent starting state.

BIN/SRC:
- Test74 `SFC/catalog.xgc` size 2642, SHA
  `7c45d63c4f15a23661a6f47873bd5c664d68a0a0806155a422f123952bc28a01`.
- Test75 `FC/catalog.xgc` size 2642, SHA
  `b12541d5daede8c6e35c0f6f3a53c35c705a7d7ea7bbb508a6ae7e1b8d956067`.
- Test75 explicitly documents that FC catalog helper is the exact Test74 SFC
  helper with only system-contract substitutions.
- GB catalog triplet is already closed:
  `vdsdc.tax / umboa.nec / qdvd6.bvs`.
- GB count-cache target is already closed: `0x80D28964`.
- GB top-level generated wrapper filter is `.zgb`; scan root is `/GB`.

## Selected parent

For GB **catalog merge**, use Test75 FC / Test74 SFC explicit catalog helper
architecture, not Test124-126 scanner experiments and not Test103 native-scanner
substitution.

Required system substitutions from the proven helper family are exactly:

```
wrapper filter  -> .zgb
catalog slot 0  -> vdsdc.tax
catalog slot 1  -> umboa.nec
catalog slot 2  -> qdvd6.bvs
scan root       -> /GB
count cache     -> 0x80D28964
```

Semantics remain inherited:
- scan top-level generated wrappers;
- exact slot-0 filename identity;
- preserve existing order/indexes;
- collect missing wrappers;
- append synchronized triplet;
- basename fallback for slots 1/2;
- invalidate only the selected count cache after successful merge;
- unchanged second pass returns no-change;
- append-only; no deletion/resort.

## Why this is the correct catalog ancestor

Test74 solved the exact failure mode relevant to enrichment: a wrapper could be
materialized correctly yet not become visible because discovery later in the
same Refresh was insufficient. The explicit catalog merge made materialization
and indexing deterministic.

Test75 then proved the same helper architecture was portable to another stock
family by changing only wrapper extension, triplet, root, and count-cache target.

That is precisely the GB problem. Test08/124-126 raw discovery does not provide
the art/meta/wrapper enrichment transaction we are propagating.

## Important MD lesson retained without importing the failed mechanism

MD later exposed persistence/interruption hazards and received transaction
hardening. Those lessons remain relevant to eventual generalized safety, but
Test103 direct native-scanner substitution is a NO-BOOT negative and is not the
GB catalog parent.

Do not mix persistence-hardening redesign into the first GB propagation proof.
First reproduce the already-HW-proven Test74/Test75 catalog contract for GB;
then harden the common mechanism separately if required.

## Current blocker is archival, not architectural

The repository preserves exact hashes and behavioral/source reconstruction for
Test74/Test75, but no deterministic source builder for their 2642-byte
`catalog.xgc` helpers is currently present under `tools/`.

Therefore do not guess byte offsets.

Next mechanical step:
1. recover exact Test75 `FC/catalog.xgc` (or Test74 SFC helper) from the
   artifact lineage;
2. diff the exact FC and SFC 2642-byte helpers;
3. identify every system-contract byte range;
4. create a fail-closed deterministic GB catalog builder;
5. verify only enumerated bytes differ.

This is now a bounded artifact-recovery task, not another scanner investigation.
