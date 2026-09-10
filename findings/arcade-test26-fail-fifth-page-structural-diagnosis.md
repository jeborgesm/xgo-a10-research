# Classic Arcade fifth-page structural diagnosis after Test26

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

## Hardware result

Test26 failed with the same shape as the recent Classic Arcade candidates:

```text
select Pac-Man
 -> Loading.....
 -> black screen
```

The tester also substituted a different ROM while keeping the fifth-page entry name as Pac-Man. The failure shape did not change.

This materially weakens a ROM-set-specific explanation.

## Structural conclusion

The fifth Arcade page / list ID 11 is not equivalent to stock Arcade lists 7-10.

Repository evidence already established:

```text
list 7  -> CPS1 fixed filename/title/search triplet
list 8  -> CPS2 fixed filename/title/search triplet
list 9  -> PGM/IGS fixed filename/title/search triplet
list 10 -> Neo Geo fixed filename/title/search triplet
list 11 -> None / None / None
```

The three list-11 resource pointers are:

```text
0x80a3c3b0 -> "None"
0x80a3c3b4 -> "None"
0x80a3c3b8 -> "None"
```

Adding a valid `Resources/None` catalog is sufficient to make visible browser rows appear. It does not prove that the stock launch path initializes every per-list runtime field expected by a normal Arcade page.

The historical hardware-working Test12 MAME2000 frontend depends on stock-resolved launch state including:

```text
0x810a0eb0 current selected system/list directory
0x8109fce8 current game/archive filename
```

Those values are guaranteed by the real stock CPS1 path. They have not been proven for the dormant fifth-page path.

## Why the recent tests did not improve

Tests 15-26 repeatedly changed the external-core side while continuing to assume that list 11 supplied a complete stock launch contract.

That assumption is now the primary architectural defect.

The correct next phase is not another MAME candidate.

## Required next work

Provision list 11 as a first-class stock-style Arcade category before attaching MAME2000 again.

Static work must close:

1. every list-ID-indexed table used from browser selection through arcade preprocessing;
2. count/cache initialization for list 11;
3. system-directory resolution for list 11;
4. selected wrapper/archive-name initialization;
5. any per-list emulator/system-family masks;
6. any table-driven branch that is populated for IDs 7-10 but null/default for ID 11.

The target design is:

```text
list 11
 -> real fixed metadata triplet
 -> real count/cache entry
 -> real ARCADE directory binding
 -> real selected archive-name state
 -> same stock arcade preprocessing contract as list 7
 -> dedicated external-MAME dispatch only at the final emulator ownership seam
```

Do not ask hardware to test another MAME package until the fifth-page launch contract is statically reconstructed and audited against list 7 end-to-end.
