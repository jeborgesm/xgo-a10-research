# Hardware Test131 — GB helper execution PASS, catalog visibility FAIL

Date: 2026-09-23
Status: PARTIAL HW PASS / CATALOG-FRONTEND FAIL

## Hardware observations

User tested Test131 after correcting the GB helper pathname HI16 construction.

Observed:
1. First Refresh Games -> Game Boy returned **Games Updated**.
2. Second unchanged Game Boy refresh returned **No New Games**.
3. The visible Game Boy list was NOT updated with the newly imported game.
4. The visible Game Boy list was left at the stock catalog state.
5. Games previously discovered/added by earlier raw-scanner experiments were no longer visible.

## What this proves

HW: The Test127/128/130 pre-helper failure is closed. Correcting the signed-ADDIU HI16 pathname construction allows the GB materializer/helper sequence to execute and reach stable changed/no-change results.

HW: Idempotence at the helper level is working: first pass changed, second pass no change.

HW: End-to-end GB enrichment is NOT complete. A successful helper/catalog transaction is not reflected in the live/visible Game Boy frontend list.

INF, strongly supported by prior MD history: the remaining failure is catalog/frontend lifecycle integration, not GB materializer discovery. The symptom is analogous to the historical distinction between persistent catalog mutation and the native in-memory frontend/catalog workspace.

Important observation: previously raw-scanner-added GB entries disappearing while stock entries remain means Test131's catalog operation has restored/rebuilt the canonical stock-shaped catalog rather than preserving the earlier scanner-derived visible additions. Do not interpret Games Updated as proof that the frontend consumed the new catalog.

## Next gate

Do not change the GB materializer. Do not touch FC/SFC/MD/CLASSIC.

Recover the closest HW-proven MD post-catalog lifecycle mechanism, especially Test97/Test105/Test106 behavior around:
- catalog rewrite,
- count-cache invalidation,
- native in-memory catalog workspace reload/finalization,
- return to frontend,
- reboot visibility.

Compare GB catalog helper semantics against the exact MD hardware-proven sequence before producing another candidate.
