# XGO CPS1 active-driver selection — instruction-level BIN closure

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Status: BIN
Hardware candidate: NOT AUTHORIZED

## Exact function

The native XGO arcade callback installer maps:

gfn_retro_load_game 0x80c33acc <- 0x8036d658

Direct disassembly of exact bios/bisrv.asd now closes the beginning and driver-selection portion of that function.

## Exact basename extraction

At 0x8036d690 the function loads info->path.

It then calls the firmware string-search routine with '/':

8036d694  a1 = 0x2f
8036d698  call string-search

The returned path component is copied into a 128-byte stack basename buffer at sp+0x20.

At 0x8036d6d4 it searches that basename for '.':

8036d6d8  call string-search
8036d6dc  a1 = 0x2e
8036d6e4  store NUL at returned extension position

This is the compiled XGO equivalent of the 621e371 extract_basename() logic.

Therefore an info->path ending in:

.../1941.zip

is reduced to:

1941

before driver lookup.

Likewise:

.../dino.zip -> dino

## Exact active-driver scan

XGO then performs the driver scan directly in 0x8036d658.

Relevant globals:
- gp-24068: nBurnDrvCount-equivalent
- gp-30192: nBurnDrvActive-equivalent

The loop at 0x8036db6c..0x8036dba8 does:

1. increment candidate driver index;
2. compare candidate index against driver count;
3. store candidate index to gp-30192;
4. call 0x8036f7d0 to obtain the candidate driver name;
5. call 0x80294dec, the firmware strcmp routine, with:
   a0 = returned driver name
   a1 = stack basename at sp+0x20
6. continue scanning when strcmp != 0;
7. preserve the matching index when strcmp == 0.

Key instructions:

8036db80  call 0x8036f7d0
8036db84  sw s0,-30192(gp)
8036db88  a0 = v0
8036db8c  call 0x80294dec
8036db90  a1 = sp+0x20
8036db94  bne v0,zero -> continue loop
8036db9c  s1 = s0              ; matched driver index

If no driver matches, execution reaches the error logger using XGO string at 0x809a4e9c:

[FBA] Cannot load this game.

## Exact correspondence with preserved source

This is not merely similar to upstream. The XGO instructions implement the same algorithm as the identified 621e371 libretro source:

extract_basename(basename, info->path, ...)
i = BurnDrvGetIndexByName(basename)

and BurnDrvGetIndexByName():
- iterate 0..nBurnDrvCount-1;
- set nBurnDrvActive;
- strcmp(BurnDrvGetText(DRV_NAME), name);
- retain matching index.

The correspondence is now BIN-closed for the driver-selection boundary.

## Consequence for Test04

Given a correctly constructed retro_game_info path ending in 1941.zip:

XGO itself deterministically strips .zip and searches for driver name 1941.

The exact XGO binary contains a compiled 1941 driver identity.

Therefore the hypothesis:

"Test04 fails because XGO cannot map 1941.zip to the 1941 driver"

is closed/eliminated unless the frontend supplies a different/corrupted info->path than the already-established stock preprocessing contract predicts.

This moves the first unresolved failure boundary forward.

## Next boundary

After a successful driver-name match, XGO enters the initialization/archive path. The same function contains the exact XGO "Cannot find driver" diagnostic at 0x809a4f18, referenced near 0x8036df8c, which belongs to the archive/init failure branch rather than the short-name lookup branch.

Next offline work:
- reconstruct the post-match transition into fba_init/open_archive;
- distinguish archive-open failure from missing-required-ROM failure;
- recover 1941 BurnDrvGetZipName dependency behavior at BIN level if possible;
- continue looking for exact Test04 1941.zip provenance/content.

No Test05 authorized.
