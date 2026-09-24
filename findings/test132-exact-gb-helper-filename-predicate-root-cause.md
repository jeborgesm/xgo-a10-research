# Test132 exact GB helper — filename predicate root cause

Date: 2026-09-23
Branch: `research-refresh-gb-gbc-gba`
Evidence: BIN, reconciled with HW Test132
Input supplied from tested SD: `GB/refresh.xgc`

## Identity

Size: 1,056,520 bytes (0x101F08)
SHA-256: 00addd59c2b3305e936021bb6cb7c66e03cac334816cd2a61e5c216315e19810

## Decisive result

The Test132 failure is now statically localized. Ordinary `Tetris.gb` is rejected at helper offset 0x024C / runtime PC 0x8700024C, before wrapper generation.

The helper retains four-character-extension geometry.

Initialization:
- s7 = 0x87600000
- s2 = 0x87600008
- s3 = 0x8760000A
- s4 = 0x87600005
- frame+0xC0 = 0x87600006
- frame+0xBC = 0x87600007

The directory entry filename begins at 0x87600008.

The length loop at 0x0220 starts v0=-2 and scans from s3+v0, therefore from 0x87600008. On the terminating NUL, v0 becomes filename_length-1.

For `Tetris.gb`, length=9, so v0=8.

The first extension test:
- 0x0244 computes v0+s4 = 0x8760000D
- relative to filename base 0x87600008 this is index 5
- `Tetris.gb` index 5 is 's'
- 0x0248 loads that byte
- 0x024C compares it with s5='.'
- mismatch branches to 0x870001F4, the next-entry path

Therefore the observed HW result:
`/GB/import/Tetris.gb` present -> `No New Games` -> no `.zgb`
is exactly explained by the binary.

## Why the existing 0x027C NOP is insufficient

0x027C is already NOP in this helper. That does not fix the first fixed-geometry dot test at 0x024C.

The later checks use neighboring fixed bases and expect:
- 0x02A8: 'g'
- 0x02D4: 'b'

For a two-character `.gb` suffix, the correct final positions are:
- dot = filename[length-3]
- g = filename[length-2]
- b = filename[length-1]

The current first-dot address resolves to filename[length-4], proving the one-byte geometry error before any materialization body executes.

## Consequence

We no longer need a hardware trace to discover the Test132 failure. The uploaded exact helper closes it offline.

Do not patch 0x024C away. The correct repair is to make the suffix geometry derive the final dot / two-character extension positions coherently, preserving rejection of unrelated filenames.

The XGO TRACE infrastructure remains valuable for future failures, but it should not be inserted into Test132 merely to rediscover a now-proven branch.

## Next gate

Construct the smallest deterministic GB predicate repair from this exact SHA and prove statically with representative filenames:
- Tetris.gb -> accept
- Tetris.GB -> accept if current case-folding semantics are preserved
- foo.gbc -> reject for GB helper
- foo.gba -> reject
- foo.sfc -> reject
- foo -> reject
- .gb / malformed short names -> reject according to existing minimum-length guard

Preserve all bytes after the predicate except the minimum required address geometry changes. No firmware/bisrv.asd change is required.
