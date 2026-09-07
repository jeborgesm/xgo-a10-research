# XGO game-list caller gate and fixed-catalog semantics

Date: 2026-09-06
Branch: `research-game-list-scanning`

Status: **caller gate closed; fixed-catalog random-access behavior confirmed; earlier loader label corrected**

## Provenance

Static analysis in this note uses the preserved stock-analysis firmware:

```text
bios/bisrv.asd
SHA-256 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
runtime base 0x80000000
```

The protected hardware baseline remains Audio OSD v8 and is not modified by this work.

## Exact one-shot scanner gate

The native scanner remains:

```text
0x80353ae0
```

The only direct caller is:

```text
0x80359404 -> 0x80353ae0
```

Immediately before that call, the frontend tests the one-shot flag at:

```text
gp - 0x5f64
```

The entire stock firmware contains exactly two accesses to this flag:

```text
0x80359378  read flag
0x80353e74  write 1 after successful generation path
```

No reset/write-zero path exists.

The scanner also reads the active list/menu byte at:

```text
gp - 0x0da4
```

and the surrounding frontend transition code compares:

```text
gp - 0x0df4   current visible list/menu state
gp - 0x0da4   selected/target list/menu state
```

The scanner path is reached when those states have converged and the one-shot flag is still zero.

These globals are in runtime BSS beyond the stored ASD payload. Under normal startup they are zero-initialized. Therefore initial state is naturally:

```text
current list  = 0
selected list = 0
scan-done     = 0
```

List ID 0 is independently mapped to:

```text
folder    ROMS
resource  tsmfk.tax / tsmfk.tax / tsmfk.tax
```

After generation, `scan-done = 1`, and there is no firmware path that resets it.

### Conclusion

**CONFIRMED:** the native directory scanner is a once-per-runtime-session mechanism.

**STRONG CONCLUSION:** normal startup/initial frontend convergence runs that scanner for list ID 0, producing `Resources/tsmfk.tax` from `ROMS`, after which the scanner cannot run for later built-in categories during that session.

This closes the principal caller-scope question from the first scanner note.

## Correction: 0x803536ec is not the main .tax string-list loader

Earlier notes referred to `0x803536ec` as a generic built-in-list loader because it indexes the same resource table and opens a selected resource.

Deeper read-width analysis shows that label was too broad.

That routine reads:

```text
4-byte leading count
then count * 2 bytes
```

and is directly called with resource-table ID 14, which resolves to:

```text
Hisas.boa
```

This is consistent with history/favorites-style 16-bit record processing, not the 32-bit-offset string catalogs.

The main game-browser string access is a separate random-access path in the large frontend routine around `0x80357b..`.

## Main fixed-catalog access pattern

The visible game browser selects one of the three resource slots from the list-ID triplet table at:

```text
0x80a3c32c
```

It opens the selected resource and retrieves individual strings without loading the complete catalog.

For a requested game index, the path performs the equivalent of:

```text
seek(4 + index * 4)
read uint32 offset

seek(4 + count * 4 + offset)
read NUL-terminated string
```

Relevant code is in the `0x80357cec..` range.

This directly confirms the independently recovered physical format:

```text
uint32 count
uint32 offsets[count]
char strings[]
```

and explains why large built-in catalogs can be browsed without keeping all their text resident.

## Language-to-resource-slot mapping

The persistent language selector is:

```text
gp - 0x0d7c
```

already identified as `Archive.sys` word 0.

The browser maps the six XGO languages to resource slots as follows:

```text
English  -> slot 0: filename/English catalog
Chinese  -> slot 1: Chinese display-title catalog
Arabic   -> slot 0
Hebrew   -> slot 0
Spanish  -> slot 0
Russian  -> slot 0
```

Therefore the Chinese catalog is an actual alternate display-name list. The other five UI languages display the filename/English catalog.

Slot 2 is not part of ordinary game-name display and remains associated with the search path.

## Built-in metadata integrity requirement

For list IDs 1..10, the stock resource table contains synchronized triplets:

```text
slot 0 filename/English
slot 1 Chinese title
slot 2 search key
```

The three files have position-coupled indexes and matching counts on the captured card.

Consequently, an on-device built-in rebuild must preserve a common ordering and common count across all three files if it is expected to support:

- ordinary browsing;
- Chinese UI;
- stock search.

A filename-only rebuild would be structurally incomplete even though it would appear to work in the five UI languages that display slot 0.

## Family-tool corroboration

The maintained GB300/SF2000 tool models these resources as one `TNameLists` object containing:

```text
FileNames
ChineseNames
PinyinNames
```

Its Add/Insert/Delete operations change all three lists in lockstep, and `SaveToFiles` writes all three catalogs.

This is external family evidence, not XGO authority, but it matches the XGO positional coupling exactly.

The family serializer also independently uses the same 32-bit count/offset/string format.

## Fifth Arcade / list ID 11

The XGO resource triplet remains:

```text
11 -> None / None / None
```

A scan of the main frontend code for a direct list-ID-11 comparison found no dedicated branch analogous to the explicit special states 13, 14, and 15.

The one-shot directory scanner cannot normally populate ID 11 because it has already latched complete after ID 0.

This materially weakens the prior hypothesis that the fifth Arcade entry is a dynamic raw-ZIP scanner.

Current classification:

### CONFIRMED

- ID 11 has no fixed catalog triplet;
- normal once-per-session scanner is consumed by ID 0 and cannot later rebuild ID 11;
- no direct immediate comparison against list ID 11 appears in the main game-browser state machine.

### STRONG EVIDENCE

- the fifth repeated Arcade menu entry is an empty/placeholder or otherwise dormant slot in this XGO build, not the normal dynamic raw-arcade browser.

### OPEN

- whether an indirect/table-driven special path can populate ID 11 without an explicit numeric comparison;
- whether another firmware-family revision activates that slot differently.

## Design consequence

We should not write a new filesystem scanner.

The XGO already has the expensive/low-level pieces:

- directory enumeration;
- extension filtering;
- alphabetical sorting;
- stock list serialization;
- filesystem sync.

The engineering problem has narrowed to an explicit rebuild coordinator that can:

1. reuse or adapt the native enumeration logic;
2. build three aligned catalogs for fixed system pages;
3. preserve or repair Favorites/History references when ordering changes;
4. write all affected resources atomically/recoverably;
5. expose a user-triggered command rather than scanning every boot.

No firmware candidate has been generated yet.
