# Arcade Refresh — collision/idempotence planner milestone

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **SOURCE/DESIGN CLOSED; NO FIRMWARE CANDIDATE**

Source:
- `tools/arcade_refresh/import_planner.py`
- `tools/arcade_refresh/test_import_planner.py`

Rules frozen:
1. Existing `/ARCADE/bin/<driver>.zip`, byte-identical -> reuse.
2. Same ZIP basename with different bytes -> fail; never overwrite.
3. Existing outer ZFB pointing at same driver -> reuse.
4. Existing outer ZFB pointing at another driver -> fail.
5. Exact ZFB already in target family catalog and physical assets coherent -> no-change.
6. Exact ZFB cataloged only by another family -> fail cross-family; never silently duplicate.
7. Target catalog entry exists but required physical launch assets are missing -> fail closed; repair/reconciliation is not ordinary append.
8. New entry may reuse compatible existing physical ZIP/ZFB, then append target family catalog.
9. Catalog membership is the convergence/idempotence key.
10. Metadata/title changes after initial import do not create a duplicate and are deferred reconciliation.

Transaction contract is separately frozen in
`findings/arcade-refresh-transaction-recovery-contract.md`, derived from HW-proven Test106 logical marker semantics.

Next implementation task is recovery of the Test74/Test75 JPEG -> 144x208 RGB565LE worker and construction of an Arcade materializer around the already-closed ZFB serializer.
