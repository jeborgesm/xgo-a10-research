# Test126 pre-package isolation audit

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`

Status: **OFFLINE PASS — corrected selective handheld discovery may proceed to packaging**

Test125 remains HW FAIL and is not promoted.

## Root-cause correction

Test125 used a false 24-byte resource-table stride. The stock primary-console
resource table is 12-byte records (three 32-bit pointers). Correct descriptors:

- GB:  names `0x80A3C35C`, count `0x80D28964`, folder `GB`
- GBC: names `0x80A3C368`, count `0x80D2896C`, folder `GBC`
- GBA: names `0x80A3C374`, count `0x80D28974`, folder `GBA`

CLASSIC is unchanged and passed its Test125 regression check.

## Reproducible corrected Stage2 identities

- GB:  `6b3ec79439e7597044024bbf04a959b0309078c3e56b3884c8e277cc12f89568`
- GBC: `a79fb1b98ff6253d541e471a3741cb2dbed08dbf928621e2eb70192b4d2395f6`
- GBA: `1111a51ce927c68599df1dd0b8b958b3e7303ac1cb0b27f04c2e31f882a02635`

Each is exactly 7000 bytes. Stage1 remains byte-identical to Test125.

## CI isolation gate

GitHub Actions run `35811199041`, commit
`cd9a6ba1ac75b8d859c95e5b87069a9421895670`, completed successfully.

The generated helpers passed:

```
PASS gb:  names=0x80A3C35C count=0x80D28964 folder=GB
PASS gbc: names=0x80A3C368 count=0x80D2896C folder=GBC
PASS gba: names=0x80A3C374 count=0x80D28974 folder=GBA
```

The audit decodes the MIPS LUI + signed ADDIU address construction and rejects
foreign handheld folder literals. This directly guards the descriptor-class
mistake that escaped Test125.

## Test126 hardware question

Can the corrected, isolated Test08-derived worker selectively discover and
stable-merge the pending raw GBC and GBA ROMs from their own directories,
without cross-family catalog contamination and without regressing GB or
CLASSIC?

Expected:
- GBC first refresh: Games Updated; pending GBC ROM appears only in GBC.
- GBC second unchanged refresh: No New Games.
- GBA first refresh: Games Updated; pending GBA ROM appears only in GBA.
- GBA second unchanged refresh: No New Games.
- GB unchanged refresh: No New Games, assuming no additional unindexed GB ROM.
- CLASSIC unchanged refresh: No New Games and remains functional.

This remains a discovery/isolation proof only. A PASS unlocks, but does not
replace, the required import/art/meta -> stock-shaped .zgb enrichment stage.
