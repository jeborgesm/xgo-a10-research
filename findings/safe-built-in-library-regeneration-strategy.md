# Safe XGO built-in library regeneration strategy

Date: 2026-09-06
Branch: `research-game-list-scanning`

Status: **design narrowed from full rebuild to stable merge; no firmware modification yet**

## Why a blind native-style rebuild is unsafe

The stock User-ROM scanner alphabetically sorts every discovered filename.

That behavior is safe for list ID 0 because User Games uses a disposable runtime-generated index and is not represented in the built-in History data observed on the captured card.

It is unsafe to apply unchanged to built-in list IDs.

Built-in Favorites and History records are index-based:

```text
uint16 list_id
uint16 game_index
```

Re-sorting FC/SFC/MD/GB/GBC/GBA or curated Arcade catalogs would change many existing `game_index` values.

That would silently redirect old Favorites/History records to different games unless every reference were remapped in the same transaction.

## Lower-risk strategy: stable merge

The safer first implementation is:

```text
load existing synchronized triplet
scan physical ROM directory
keep every existing catalog entry in its current position
identify physical filenames absent from slot 0
append only newly discovered entries
write all three resources with identical final counts
```

This deliberately does **not** globally re-sort the built-in library.

### Consequences

Existing entries keep their exact index.

Therefore existing:

- Favorites;
- History;
- per-game positional references;

continue to resolve to the same game without migration.

New games receive new indices only at the end of the list.

This is much safer than rebuilding from the directory in alphabetical order.

## New-entry fallback metadata

The XGO browser proves:

- slot 0 is the filename/English catalog;
- slot 1 is used for Chinese display names;
- slot 2 is used by search-oriented paths.

For a newly discovered ROM with no OEM metadata, the minimum structurally safe fallback is:

```text
slot 0 = exact physical filename including extension
slot 1 = readable basename without extension
slot 2 = uppercase/alphanumeric search form derived from basename
```

Example:

```text
Actraiser 2.zsf
Actraiser 2
ACTRAISER2
```

The slot-1 fallback avoids showing a wrapper extension in Chinese UI.

The search code normalizes candidate characters and explicitly recognizes ASCII A-Z and 0-9 classes, so an uppercase alphanumeric basename is a plausible safe fallback search key. This is a **design candidate**, not yet a hardware-proven search contract.

Existing OEM Chinese/pinyin metadata must remain untouched.

## Family-tool corroboration

The maintained GB300/SF2000 tool treats filename, Chinese-name, and pinyin/search lists as one synchronized object.

Its Add/Insert/Delete methods mutate all three lists together, and SaveToFiles writes all three resources.

That independently supports the XGO requirement that new entries must be added positionally to all three catalogs.

## Missing physical ROM policy

For the first on-device implementation, do **not** delete catalog entries whose files are currently absent.

Deletion would shift every later index and again require Favorites/History migration.

A safe first command should therefore behave as:

```text
discover and append
never reorder
never delete
```

A later maintenance mode could support cleanup only after filename-based reference remapping is implemented.

## Transaction requirement

The stock User-ROM scanner opens `tsmfk.tax` with `wb` and rewrites it in place.

That is acceptable for a boot-regenerated disposable index.

It is not acceptable for canonical built-in triplets: interruption after truncating one file could leave the library inconsistent.

A built-in rebuild command therefore needs a recoverable write protocol.

Preferred shape:

```text
build complete new triplet in memory
validate equal counts and all offsets
write backup or temporary copies
verify writes
replace canonical triplet in a controlled commit sequence
refresh in-memory counts only after all three are valid
```

An atomic rename primitive has not yet been identified in the mapped XGO filesystem wrappers, so exact commit mechanics remain open.

## Session-state requirement — simplified by stock lazy reload

The main browser caches one 32-bit count per list in the shared array beginning at:

```text
0x80d2894c
```

The scanner uses the same array while generating the User-ROM list.

Deeper control-flow tracing shows the built-in browser already has a lazy reload path: when the current list's cached count is zero, it seeks to offset 0 of the selected catalog and reads the 4-byte count directly into that list's count slot.

One confirmed instance is around:

```text
0x80357f1c..0x80357f54
```

Therefore a future rebuild does **not** need to reconstruct the complete frontend initialization sequence.

After a successful catalog commit it can invalidate the affected cache by setting:

```text
count[list_id] = 0
```

and allow the stock browser to reload the new count from the resource on its normal path.

This substantially reduces the runtime integration required. Cursor/page state still needs to be kept within the new count, but the count itself already has a native reload mechanism.

## Recommended first hardware experiment

Before implementing a general scanner command, use the safest possible proof:

1. choose one physical-but-unindexed ROM already present on the card;
2. preserve all existing entries/order;
3. append that filename to slot 0;
4. append aligned fallback values to slots 1 and 2;
5. update only the relevant list count/state if necessary;
6. verify the new title appears and launches;
7. verify existing Favorites/History still resolve correctly;
8. verify Chinese UI and Search do not crash or mis-index.

This test proves the stable-append architecture without adding a new ROM payload.

## Current conclusion

The project no longer needs to answer "can XGO scan folders?" That is proven.

The practical problem is now:

> how to safely merge newly discovered physical ROMs into the existing polished catalog without changing legacy indices or corrupting the three synchronized metadata resources.

Stable append is currently the lowest-risk answer.
