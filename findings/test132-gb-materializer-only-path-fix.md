# Test132 — corrected GB materializer-only discriminator

Date: 2026-09-23
Status: offline-audited hardware diagnostic

Purpose: separate the GB materializer return value from the misleading aggregate
status seen in Test131.

Parent is exact Test128 materializer-only diagnostic. Test128 already bypasses the
GB catalog stage after the first helper. Test132 changes only the malformed HI16
of the GB refresh pathname:
  0x80A39050: lui a0,0x80A3 -> lui a0,0x80A4
The following addiu low half remains 0x90C0, yielding effective 0x80A390C0.

The Test128 catalog bypass remains unchanged:
  0x80A3907C = j 0x80A38808
  0x80A39080 = nop

Exact GB helper is unchanged:
SHA-256 00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810

Candidate:
- firmware SHA-256 9d9030b1d4218561e8c042d406cb035bf8679b15166dcdedd601299429639acb
- LCFG CRC 0xB8DB6F69
- ZIP SHA-256 8bf39fc0f667a1d195785e76f363f1c4dbf9048f7d419782c3641429bf8dc6da

Hardware interpretation with /GB/import/Tetris.gb already present:
- Games Updated + Tetris.zgb => materializer succeeds; Test131 ambiguity came later.
- No New Games + no Tetris.zgb => materializer executes but rejects/skips input.
- Refresh Failed => helper executes and reaches an internal failure or runner failure.

This diagnostic changes no FC/SFC/MD/CLASSIC helper/path and performs no GB catalog
operation.
