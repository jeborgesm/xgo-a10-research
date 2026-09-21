# CRITICAL: Refresh catalog persistence is non-atomic and explains SD corruption risk

Deep analysis of user-supplied 20260919XGO_MD_Analysis.zip and exact Test97 MD/catalog.xgc.

## Current forensic state

Current Resources after user's recovery:
- SCKSP.TAX: 23,458 bytes, count header = 839
- SETXA.NEC: 17,082 bytes, count header = 839
- wmiui.bvs: 8,160 bytes, count header = 788; SHA-256 exactly matches pristine XGoAnalisis baseline because user restored it after Windows reported 0x80070570 corruption.

Pristine baseline:
- scksp.tax: 22,156 bytes, count = 788
- setxa.nec: 15,984 bytes, count = 788
- wmiui.bvs: 8,160 bytes, count = 788

Thus the successful MD catalog pass expanded TAX/NEC from 788 to 839 entries: +51, not merely the four newly imported games.

The 51 appended TAX entries are 47 pre-existing top-level .zmd wrappers that were absent from the baseline catalog plus the four new Test97 wrappers. Final four are:
835 Streets of Rage.zmd
836 Ninja Gaiden.zmd
837 NBA Jam Tournament Edition.zmd
838 Super Street Fighter II - The New Challengers.zmd

SETXA.NEC has matching friendly display titles at the same indices.

## Catalog helper write architecture

MD/catalog.xgc loads the three catalog files independently into fixed 64 KiB buffers:
- TAX -> 0x87200000
- NEC -> 0x87210000
- BVS -> 0x87220000

It validates counts <= 0x1000 and appends at most 255 newly discovered entries. 51 additions are within those explicit limits; this is NOT a simple buffer-capacity overflow.

After scanning, it rewrites the live files IN PLACE, sequentially:

1. fopen("/Resources/scksp.tax", "wb")
   fwrite(full TAX)
   fclose

2. fopen("/Resources/setxa.nec", "wb")
   fwrite(full NEC)
   fclose

3. fopen("/Resources/wmiui.bvs", "wb")
   fwrite(full BVS)
   fclose

Then it clears MD count cache 0x80D2895C and returns.

There is:
- no temporary-file transaction;
- no backup/rollback;
- no all-three commit boundary;
- no explicit filesystem sync between/after the three writes.

Therefore interruption/hard-lock/power-cycle around Refresh can leave a partially committed triplet and/or dirty FAT state.

## Why wmiui.bvs is especially revealing

BVS is the THIRD and LAST live catalog file rewritten. The user's Windows copy failure specifically hit wmiui.bvs with 0x80070570. TAX and NEC survived with their expanded 839-entry state.

This ordering is consistent with a persistence window where the first two rewrites reached stable storage while the final BVS file/directory/FAT update remained vulnerable when the device later hard-locked and had to be power-cycled.

This is evidence of a dangerous persistence design, not proof that fwrite itself corrupts FAT. The forced shutdown after the frontend hard-lock is a plausible mechanism for turning an unsafe non-atomic rewrite into filesystem corruption.

## Immediate consequence

STOP using hardware Refresh experiments that rewrite stock catalog triplets until persistence is made safer. Repeated hard-lock/power-cycle cycles can contaminate the forensic baseline and produce misleading failures.

The current card is intentionally inconsistent after recovery (TAX/NEC 839, restored BVS 788). It should not be treated as a clean baseline for further Refresh tests.

## Architecture direction

Before Test103:
1. establish a known-consistent triplet;
2. redesign catalog persistence so all outputs are staged before touching live files;
3. add an explicit durability/sync boundary if the platform exposes one;
4. only replace live files after every staged output has been successfully produced;
5. preserve/restore the previous triplet on failure where practical;
6. fix the post-refresh frontend lifecycle/hard-lock so users are not forced to power-cycle immediately after writes.

Also investigate whether the native generalized scanner/lifecycle already provides safer persistence and can replace the custom catalog writer.

This finding supersedes treating SD corruption as incidental noise.
