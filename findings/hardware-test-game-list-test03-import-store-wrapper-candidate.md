# Hardware candidate — Game List Test03: generated SFC wrapper with ZIP STORE

Date: 2026-09-06
Branch: `research-game-list-scanning`

## Purpose

Test the complete XGO packaged-game import contract using only XGO-owned/captured test content.

Unlike Test01/Test02, this candidate creates a **new `.zsf` wrapper from scratch** rather than pointing a new catalog index at an existing packaged game.

## Artifact

`xgo-game-list-test03-sfc-import-store-wrapper.zip`

ZIP SHA-256:

`bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320`

## New wrapper

`SFC/XGO Import Test.zsf`

Size: `191,112` bytes

SHA-256:

`f600c45d37a77d9af80ecb1ad136e1dbcfbb7e22fd9afc91531f82cfd2fb03b1`

Construction:

- first 59,904 bytes: exact 144x208 little-endian RGB565 thumbnail from captured XGO `Resources/Test.zsf`;
- payload ROM: exact controller-test ROM extracted from captured XGO `Resources/Test.zsf`;
- ROM renamed inside package to `XGO-Import-Test.sfc`;
- ROM SHA-256 `76e60393139669b25c5a82247c3fbbc6f2a9715049532b2d14991adbec60ac9b`;
- WQW archive generated from scratch;
- ZIP compression method deliberately set to method 0 / STORE, so ROM bytes are not DEFLATE-compressed.

## Why method 0 matters

If stock XGO accepts this wrapper, a future on-device importer does **not need a compressor**.

Minimal package creation would require only:

1. write local ZIP/WQW header;
2. write raw ROM bytes;
3. write central-directory record;
4. write end-of-central-directory record;
5. XOR stored filename bytes by `0xE5` and use WQW signatures;
6. prepend 144x208 RGB565 thumbnail.

This is substantially smaller and safer than calling or porting zlib/deflate.

## Catalog append

SFC catalogs are stable-appended from 929 to 930 entries:

`urefs.tax` -> SHA-256 `f2cbc51c08689229216fab1024d7acd7c62480d96812d97c2efe984f1fe63916`, size 27,017

`adsnt.nec` -> SHA-256 `c010fca8f276bd73f34b7c01357979d94680961d4238fbb55521d589228ba2cb`, size 21,102

`xvb6c.bvs` -> SHA-256 `ccc7339310b785dce8537014af408b7e0aa09e9025dc2584ebac49bd159c032b`, size 10,310

New aligned metadata:

slot 0: `XGO Import Test.zsf`
slot 1: `XGO Import Test`
slot 2: `XGO Import Test`

All original SFC indexes remain unchanged.

## Expected hardware behavior

At end of SFC:

`930  XGO Import Test`

Selecting it should launch the Super Famicom controller-test program from the newly generated wrapper.

The thumbnail should render using the copied XGO test artwork.

Pause/quit should remain normal.

The existing FC Mega Man Favorite should still resolve normally as a cross-list stable-index sentinel.

## What a PASS proves

- a newly generated `.zsf` wrapper is accepted by stock XGO;
- wrapper thumbnail boundary/layout is correct;
- generated WQW local/central/EOCD structure is correct;
- stock XGO accepts ZIP method 0 / STORE inside WQW;
- raw ROM import does not require DEFLATE if STORE is accepted;
- stable append works for SFC as well as FC;
- wrapper filename becomes the persistent game identity for future save/remap state.

## Golden status

Candidate only. Do not promote to `golden/` until hardware confirms successful launch.