# Test133 — GB two-character first-dot gate isolation

Date: 2026-09-23
Status: bounded hardware diagnostic

## New binary finding

Re-decoding the exact Test97/Test132 filename predicate exposed an earlier gate that
the prior audit had not reconciled.

The FC/SFC three-character predicate uses:
- helper 0x024C: branch away unless the byte at the L-4 position is '.'
- helper 0x027C: branch for the next extension character
- helper 0x02AC / 0x02D8: remaining extension characters.

For a two-character suffix '.gb', L-4 is one byte before the dot. Therefore retaining
the FC/SFC 0x024C L-4-dot rejection can reject a valid two-character filename before
the later Test97-derived '.','g','b' checks can admit it.

Test132 retains:
  0x024C = 0x1435FFE9  (bne -> next entry)
  0x027C = 0x00000000  (Test97 NOP)
  0x02A8 = compare 'g'
  0x02D4 = compare 'b'

This creates a static contradiction with the historical interpretation that Test97's
single 0x027C NOP alone explains acceptance of ordinary .md filenames. That historical
HW result remains authoritative, but the exact static mechanism needs correction in
our documentation. Do not erase the contradiction.

## Diagnostic

Test133 starts from Test132 exactly:
- same firmware SHA 9d9030b1d4218561e8c042d406cb035bf8679b15166dcdedd601299429639acb
- catalog remains bypassed
- same /GB/import/Tetris.gb fixture
- same corrected firmware pathname
- same g/b comparisons
- same Test97 0x027C NOP

Only GB/refresh.xgc helper offset 0x024C changes:
  0x1435FFE9 -> 0x00000000

This removes only the inherited L-4 dot rejection. It does NOT bypass the later
case-folded 'g' and 'b' checks.

Test133 GB helper SHA:
889d6c6fd540711f0016a03e0c70cd568827d2360301c46ec935c7538d67fe86

Candidate ZIP SHA:
23ec671d50f7c7ecfa65a234d18a3139f6c2c8766304393ec7256de969834aae

Expected discriminator:
- Games Updated + generated .zgb: L-4 inherited dot gate was the GB rejection.
- No New Games + no .zgb: rejection is later; continue offline.
- Refresh Failed: candidate passed farther downstream but encountered a fatal materializer path.
