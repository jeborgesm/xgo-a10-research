# Byte-exact stable append proof for XGO game catalogs

Date: 2026-09-06
Branch: research-game-list-scanning

Status: offline proof complete against captured XGO Resources; no firmware or hardware artifact generated.

## Catalog-wide structural audit

All 31 recovered XGO string-list resources were parsed using the confirmed 32-bit count/offset/string format.

For every file tested:
- the offset table is valid;
- every indexed string is NUL-terminated;
- the last indexed string ends exactly at EOF;
- there is no trailing padding or opaque footer after the string blob.

This includes User Games, all six console triplets, and the four curated Arcade triplets.

That property permits a byte-preserving stable append.

## Minimal append transform

For an existing file with N entries:

1. write count N+1;
2. copy the original N offset words byte-for-byte;
3. append one new offset equal to the original string-blob length;
4. copy the complete original string blob byte-for-byte;
5. append the new UTF-8 string plus NUL.

Because offsets are relative to the start of the string blob, no original offset value changes.

Every original OEM string byte also remains unchanged; the old blob merely moves four bytes later in the rebuilt file because the offset table gained one word.

This is materially safer than decoding and reserializing all existing names.

## Offline FC proof

Candidate physical-but-unindexed ROM:

`FC/Bomber Man 2.zfc`

Fallback synchronized triplet:

slot 0: `Bomber Man 2.zfc`
slot 1: `Bomber Man 2`
slot 2: `Bomber Man 2`

Exact captured input resources:

`rdbui.tax` SHA-256 00a15acd702e97e25d4eb8420c1efbc645a377de928125248f1869dd06449325
`fhcfg.nec` SHA-256 984cc22a261c4d80f73193cd073789f03d8848afd07733adabd040cfb9332422
`nethn.bvs` SHA-256 00cb20e66653eed21b264079ad9c4a5c8915de47de0b4b054c3fbf73d2a3b436

Offline output:

`rdbui.tax`: count 744 -> 745, size 16528 -> 16549, new SHA-256 18e96c0543f98e513af4a2cf4e7679d922e1d26bad7d242d1eb59492890556ab
`fhcfg.nec`: count 744 -> 745, size 13297 -> 13314, new SHA-256 c958891b891093ba1a3b23838798a89925f2419f10322e4059c5ad4f9b51e8de
`nethn.bvs`: count 744 -> 745, size 6990 -> 7007, new SHA-256 4d76f100fd672ff7557517e9fd671238c0002e5fac955856d0f831a5b9d7e62e

New relative offsets are exactly the original blob lengths:

`rdbui.tax` 13548
`fhcfg.nec` 10317
`nethn.bvs` 4010

Assertions passed that:

- all 744 old offset words are byte-identical;
- every old string-blob byte is byte-identical;
- only count/header layout plus the one new offset/string are introduced;
- all three final counts are exactly aligned at 745.

## Repository tool

`tools/game_lists/prototype_append_existing_fc_rom.py` reproduces this transform and refuses the captured FC base files unless their exact SHA-256 values match.

## Architectural consequence

A first metadata-only hardware proof does not require a general-purpose catalog parser or a full list rebuild.

It can be implemented as an exact append transform over three known resource files, followed by cached-count invalidation.

No old game index changes, so Favorites and History remain valid.

No ROM payload needs to be copied because `Bomber Man 2.zfc` is already physically present on the captured card.

## Still not a hardware candidate

This proof only establishes deterministic resource-file transformation.

Before hardware output, the remaining questions are:

- how the explicit user command should be triggered;
- whether the first test should modify only SD Resources or also patch firmware to perform the operation on-device;
- how to journal/restore the three canonical resources if power is lost during an on-device write;
- exact behavior when slot-1/slot-2 fallback text is used in Chinese display/search.

No ZIP was generated, so the artifact-vault archival rule has not yet been triggered.