# GB predicate repair — controlled hardware validation

Date: 2026-09-23
Branch: `research-refresh-gb-gbc-gba`
Status: READY FOR CONTROLLED HW TEST
Ancestor: exact HW-observed Test132 GB materializer

## Input identity
`GB/refresh.xgc`
size 1,056,520
SHA-256 `00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810`

## Candidate identity
size 1,056,520
SHA-256 `082c17e8a31cfae474aef4e401906be5fd7c05271a2eade5b6cf6e1ce2a09119`

Mechanical diff: exactly one byte at file offset 0x009C:
`05 -> 06`
which changes instruction `ori s4,s7,0x0005` to `ori s4,s7,0x0006`.

No `bios/bisrv.asd` modification is required.
No catalog helper modification is part of this validation.
No gameplay path is modified.

## Expected first-run result

With the same Test132 setup:
`/GB/import/Tetris.gb`

Refresh Games -> Game Boy should now pass the two-character suffix predicate and proceed beyond the previously proven rejection at runtime PC 0x8700024C.

The decisive artifact is creation of `/GB/Tetris.zgb` (or a later, newly localized materializer failure). Do not interpret the frontend status alone as proof.

## Test protocol

1. Preserve the current known-booting SD/baseline.
2. Replace only `/GB/refresh.xgc` with the candidate SHA above.
3. Keep `/GB/import/Tetris.gb` unchanged.
4. Boot and invoke Refresh Games -> Game Boy exactly once.
5. Record the UI status.
6. Check whether `/GB/Tetris.zgb` was created.
7. If created, launch only after wrapper/catalog state is understood; this candidate's immediate purpose is materializer validation.
8. Do not repeatedly press Refresh.

## Pass boundary

PASS for this predicate repair means the prior Test132 rejection is gone and the helper progresses beyond the filename gate. Wrapper creation is the preferred observable proof.

A different later failure does not invalidate the predicate repair; it localizes the next stage.

## Rollback

Restore the exact Test132 helper SHA above. No firmware rollback is necessary because this candidate does not modify `bisrv.asd`.
