# XGO search semantics, browser state, and recoverable catalog updates

Date: 2026-09-06
Branch: research-game-list-scanning

Status: search behavior substantially closed; stable-append runtime state minimized; transaction design assumes no atomic rename.

## Provenance

Static analysis uses preserved stock-analysis bios/bisrv.asd, SHA-256 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf, runtime base 0x80000000. No protected firmware artifact was modified.

## Search architecture

The search routine around 0x8035a9a8 directly references the format string `SearchKey: %s`.

Normal browser language-to-slot mapping at approximately 0x80a3c1f8 is 0,1,0,0,0,0: English/Arabic/Hebrew/Spanish/Russian use slot 0 and Chinese uses slot 1.

The search language-to-slot mapping at approximately 0x80a3c210 is 0,2,0,0,0,0: Chinese search uses slot 2 while other languages search slot 0.

Search starts at list ID 1 when the language is Chinese and at list ID 0 otherwise. This deliberately skips User Games in Chinese search because list ID 0 has no true Chinese/pinyin triplet.

For each candidate string, stock code normalizes candidate characters through helper 0x801b0fdc, accepts ASCII A-Z and 0-9 classes, ignores punctuation/spacing while matching, and compares against the entered search key.

Matches are stored as 4-byte records: uint16 list_id plus uint16 game_index. Search result capacity in this path is 200 records.

## Display-name correction

Only English language state 0 explicitly strips the filename extension in the observed visible-name path around 0x80357d70..0x80357d84. Other languages using slot 0 do not take this exact stripping branch.

## Better fallback metadata

The stock matcher already normalizes candidate strings, so manufacturing a compact key such as ACTRAISER2 is unnecessary. The safer fallback for a newly appended game is:

slot 0 = exact physical filename
slot 1 = basename without extension
slot 2 = basename without extension

Example: Actraiser 2.zsf / Actraiser 2 / Actraiser 2.

This keeps the launch filename exact, provides readable Chinese-mode fallback text, and gives Chinese Search a Latin-title key without inventing a second normalization algorithm.

## Browser state

The shared per-list count array begins at 0x80d2894c.

A second per-list array at 0x80d289cc is used as a list-position/base index and is added to the visible row before modulo by the list count.

Under stable append, every old index remains unchanged and the current list position remains valid. No cursor/page reset is required merely because the count increased. After commit, only the cached count needs invalidation; stock code already lazy-reloads a zero cached count from catalog offset 0.

## First metadata-only proof candidates

Captured physical-but-unindexed wrappers include FC/Bomber Man 2.zfc, FC/Commando.zfc, FC/Star Soldier.zfc, SFC/Actraiser 2.zsf, SFC/Batman Returns.zsf, and GBC/Shantae.zgb.

FC is the lowest-complexity first target because it is a smaller catalog and lets the first proof change metadata only. No compatibility claim is made until hardware launch is tested.

## Filesystem replacement surface

The mapped filesystem block exposes sync/open/opendir/mkdir/access/fstat/stat/read/write/lseek/readdir/close/closedir.

Deeper executable tracing identifies 0x802abf50 as a directory-removal operation: a live caller invokes it on a directory path and reports `[FS]remove dir %s failed! err = %d`.

No literal `rename` string occurs in the stock ASD, no rename wrapper has been identified in the mapped filesystem block, and no frontend rename/replace usage has surfaced. This does not prove the underlying VFS lacks rename, but the first catalog design must not depend on an unproven atomic rename primitive.

## Recoverable transaction without rename

Recommended design: build and validate all three new catalogs in RAM; write known-good backup copies; sync; write a small transaction marker; rewrite canonical slot 0/1/2 one at a time while advancing and syncing the marker; reopen and validate the completed triplet; clear the marker; then invalidate count[list_id].

On boot or before another rebuild, if the transaction marker exists, inspect its phase and either finish the new triplet or restore the known-good backups.

Because backup/temp paths can be overwritten with ordinary `wb`, recovery does not require rename.

## Minimum first mutation surface

One already-present unindexed ROM + one aligned append to each of three catalog files + one cached-count invalidation.

No ROM copy. No existing index change. No Favorites/History rewrite. No emulator-core change. No Audio OSD change.

The remaining prerequisite is a deterministic triplet writer and offline byte audit against a disposable copy of the captured Resources set before any hardware-test firmware is composed.