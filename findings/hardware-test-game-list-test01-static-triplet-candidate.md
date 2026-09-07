# Hardware Test01 candidate — static FC catalog append

Date: 2026-09-06
Branch: `research-game-list-scanning`

Status: **ARCHIVED; READY FOR HARDWARE TEST; NOT GOLDEN**

## Purpose

Prove the XGO stock FC browser can consume a synchronized stable-appended catalog triplet for an already-present but previously unindexed ROM, without changing firmware or ROM payload.

## Test entry

`FC/Bomber Man 2.zfc`

The preserved card inventory confirms this wrapper is physically present while the stock 744-entry FC catalog omits it.

## Exact artifact

`xgo-game-list-test01-bomberman2-static-triplet.zip`

ZIP SHA-256:

`45182596fd1f0598f356901b06ffc3cca94dcfcb445ac8e3b272702c6f9a3350`

Private vault path:

`xgo-game-list-test01-bomberman2-static-triplet.zip`

Vault status: present at repository root; intentionally not copied to `golden/` until hardware passes.

## Members

`README-HARDWARE-TEST.txt` size 1711 SHA-256 `679b708ca8c02a945bfd74225735f5ff948ab641a5a27eccaac602e3b46978c5`

`Resources/rdbui.tax` size 16549 SHA-256 `18e96c0543f98e513af4a2cf4e7679d922e1d26bad7d242d1eb59492890556ab`

`Resources/fhcfg.nec` size 13314 SHA-256 `c958891b891093ba1a3b23838798a89925f2419f10322e4059c5ad4f9b51e8de`

`Resources/nethn.bvs` size 7007 SHA-256 `4d76f100fd672ff7557517e9fd671238c0002e5fac955856d0f831a5b9d7e62e`

## Exact mutation

All three FC catalogs move from 744 to 745 entries.

Appended records:

```text
slot 0  Bomber Man 2.zfc
slot 1  Bomber Man 2
slot 2  Bomber Man 2
```

All 744 original offset words remain byte-identical and every original string-blob byte remains byte-identical. No existing index moves.

## No firmware modification

This artifact contains only three `Resources` files plus test instructions.

It does not contain `bios/bisrv.asd`, a ROM payload, or any Audio OSD binary.

Therefore the protected Audio OSD v8 baseline is unaffected.

## Hardware test gate

On a disposable clone:

1. back up the three existing FC Resources files;
2. copy the three files from this ZIP;
3. boot normally;
4. open FC and go to the end of the list;
5. confirm `Bomber Man 2` appears as the final entry;
6. launch it and verify gameplay starts;
7. exercise Search for the title or a useful substring;
8. if practical, switch to Chinese and confirm the final entry is stable/readable;
9. confirm an existing Favorite/History entry still resolves to the same old game.

## Interpretation

If Test01 passes, it proves the static catalog architecture and stable-append metadata contract independently of any on-device writer.

Only after that should runtime scanning/writing, transaction recovery, and a Refresh Games trigger be introduced.

Do not promote to golden until hardware passes.