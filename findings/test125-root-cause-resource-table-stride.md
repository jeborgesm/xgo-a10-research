# Test125 root cause — handheld resource-table stride was wrong

Date: 2026-09-22
Branch: `research-refresh-gb-gbc-gba`
Evidence: BIN/SRC + Test125 HW failure

## Root cause closed

The Test125 Stage2 descriptors used:

- GB  `0x80A3C374`
- GBC `0x80A3C38C`
- GBA `0x80A3C3A4`

Those addresses are wrong.

The reconstruction incorrectly treated the stock resource table at
`0x80A3C32C` as if each system occupied **24 bytes**. Direct repository
evidence for the native scanner says the table index is `list_id + 1` and
each entry is **12 bytes** (three 32-bit filename pointers).

The HW-proven Test08 record independently says its engine iterates one-based
IDs 1..6 against that same table.

Therefore the exact primary-console table is:

| Test08 ID | native zero-based list | system | table address |
|---:|---:|---|---:|
| 1 | 0 | FC  | 0x80A3C338 |
| 2 | 1 | SFC | 0x80A3C344 |
| 3 | 2 | MD  | 0x80A3C350 |
| 4 | 3 | GB  | 0x80A3C35C |
| 5 | 4 | GBC | 0x80A3C368 |
| 6 | 5 | GBA | 0x80A3C374 |

This exposes the Test125 error immediately: its supposed **GB** pointer,
`0x80A3C374`, is actually the real **GBA** triplet entry. Its GBC and GBA
pointers are beyond the six-console table.

That is sufficient to explain why Test125 violated per-system catalog
isolation. The hardware symptom — GB/GBA state crossing — is consistent with
this descriptor error.

## Important non-failure

CLASSIC is not implicated. Hardware showed that CLASSIC activated and returned
`No New Games`, which was the expected unchanged result. Preserve the
Test123 CLASSIC route unchanged.

## Count cache

Do not conflate this table-stride error with the Test08 count-cache stride.
The catalog resource table is 12-byte records. The separately recovered
Test08/FC-SFC-MD count-cache lineage uses its own 8-byte stride:
FC `0x80D2894C`, SFC `0x80D28954`, MD `0x80D2895C`, therefore GB
`0x80D28964`, GBC `0x80D2896C`, GBA `0x80D28974`.

Those count-cache addresses remain supported by the Test08 lineage unless
direct binary decoding contradicts them.

## Required source correction

`tools/game_lists/build_test125_handheld_stage2.py` must use:

- GB names = `0x80A3C35C`
- GBC names = `0x80A3C368`
- GBA names = `0x80A3C374`

No hardware candidate is authorized from this finding alone. After correcting
source, perform an offline descriptor/isolation audit and re-pin all Stage2
hashes. Test125 remains a failed artifact; the corrected candidate must receive
a new test number.
