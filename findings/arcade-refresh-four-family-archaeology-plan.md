# Arcade Refresh four-family archaeology plan

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **OFFLINE ARCHAEOLOGY — NO HARDWARE CANDIDATE AUTHORIZED**

## Protected parent

This branch starts exactly from main commit `150bd7e1c8f8449b38212a858c7a7b7de46ce275`, whose physical baseline is `20260924_PostGBCGBARefresh_CLEAN.zip`.

Do not alter the HW-proven FC/SFC/MD/GB/GBC/GBA Refresh paths, CLASSIC, Mapper v19, Audio OSD, or stock Arcade runtime while this archaeology is open.

## Target

Design a deterministic on-device Refresh importer for the four stock curated Arcade families without runtime family guessing:

```
/ARCADE/CPS1/import
/ARCADE/CPS1/art
/ARCADE/CPS1/meta
/ARCADE/CPS2/import
/ARCADE/CPS2/art
/ARCADE/CPS2/meta
/ARCADE/IGS/import
/ARCADE/IGS/art
/ARCADE/IGS/meta
/ARCADE/NEOGEO/import
/ARCADE/NEOGEO/art
/ARCADE/NEOGEO/meta
```

The family folder is intended to be authoritative input classification. Actual stock output remains subject to archaeology; current evidence says stock launch data is shared under `/ARCADE` and `/ARCADE/bin`.

## Already confirmed

XGO list IDs and synchronized catalog triplets:

- 7 CPS1: `mswb7.tax / msdtc.nec / mfpmp.bvs` — 26 stock entries in original capture.
- 8 CPS2: `kjbyr.tax / djoin.nec / ke89a.bvs` — 28.
- 9 IGS/PGM curated: `subst.tax / aepic.nec / sensc.bvs` — 6.
- 10 Neo Geo: `rmapi.tax / pcadm.nec / ntdll.bvs` — 117.
- 11 fifth Arcade slot: `None / None / None`; separately repurposed for CLASSIC and out of scope here.

This XGO ordering is authoritative. DY19 Tadpole reverses IDs 9/10 and must not be copied blindly.

Catalog format is the same synchronized count/offset/string-blob structure already used by the successful console enrichment work.

Stock Arcade packaging differs from console Zxx packaging. Curated `.zfb` files are lightweight reference wrappers:
- 59,904-byte 144x208 RGB565 thumbnail;
- four zero bytes;
- real ZIP basename;
- NUL trailer.
Actual archive is under `ARCADE/bin/<zipname>`.

Stock firmware itself constructs the launch path as `%s/bin/%s`; current-system directory is at runtime global `0x810a0eb0`, current archive filename at `0x8109fce8`.

The stock embedded Arcade emulator is a vendor-modified/hybrid FB Alpha lineage with libretro-facing identity `v0.2.97.42 621e371`. Do not assume modern FBNeo or untouched upstream 621e371 ROM-set compatibility.

## Design consequence

The likely minimum importer is not a console WQW materializer. It is:

```
family/import/<driver>.zip
+ optional family/art/<same stem>.jpg
+ optional family/meta/<same stem>.txt
        ->
copy/retain actual ZIP as /ARCADE/bin/<driver>.zip
generate lightweight /ARCADE/<display title>.zfb
append synchronized record only to that family's exact resource triplet
invalidate/reload that family's frontend count/cache if required
```

This is an architecture hypothesis until all stock write/reload details are closed.

## Required offline closure before first candidate

1. Inventory every current `/ARCADE/*.zfb`, decode its referenced ZIP basename, and correlate it to exactly one of the four catalog triplets.
2. Inventory `/ARCADE/bin/*.zip`; classify indexed, referenced-but-missing, unreferenced, duplicate, and cross-family cases.
3. Byte-verify representative ZFBs from CPS1, CPS2, IGS, and NeoGeo. Establish whether the 59,904 + 4 + basename structure is identical across all four.
4. Establish exact visible-title behavior: whether slot 0 outer ZFB basename is the English display identity as with consoles.
5. Establish slot1/slot2 fallback policy acceptable for new entries.
6. Locate list-count caches/globals for IDs 7-10 and the exact refresh/reload mechanism required after catalog mutation.
7. Determine whether NeoGeo requires BIOS-presence or other family-specific handling beyond ordinary ZIP placement.
8. Determine whether IGS/PGM entries require BIOS or multi-archive dependencies.
9. Recover all seven historically physical-but-unindexed ZFBs and classify their actual families rather than assuming omission means unsupported.
10. Compare DY19 Tadpole/Frogtool Arcade add/remove implementation only after XGO-local contracts are mapped; reuse serialization/packaging logic, not DY19 list IDs.
11. Define collision/idempotence rules for driver ZIP basename, outer ZFB display filename, metadata title, and existing catalog identity.
12. Define transactional ordering so a failed materialization cannot leave a catalog pointing at a missing ZFB/ZIP and a failed catalog write cannot corrupt synchronized triplets.
13. Preserve append-only behavior for the first implementation; deletion/reconciliation remains a separate feature.
14. Do not issue a hardware candidate until the delta can be mechanically audited against the current physical baseline and all four family descriptors are closed.

## Candidate architecture if closure supports it

Use one descriptor-driven Arcade worker rather than four copied implementations. Descriptor fields should include at minimum:

```
family name
input folder
list ID
catalog slot0/slot1/slot2 paths
frontend count/cache address
BIOS/dependency policy
```

Common worker:
```
scan authoritative family import folder
-> validate ZIP basename and collision state
-> resolve friendly title/art
-> generate ZFB reference wrapper
-> place/verify /ARCADE/bin ZIP
-> stable-append synchronized catalog triplet
-> invalidate/reload exact family count
-> aggregate status
```

No family should be inferred by opening a ZIP if the source folder already provides the classification.

## Explicitly separate CLASSIC

CLASSIC/list 11 is not a fifth stock FBA family. Its current MAME2000 implementation, save/load, catalog and Refresh path are protected and must remain untouched.

## Evidence boundary

Everything above marked confirmed comes from existing XGO-local binary/card/hardware findings. The proposed folder/input worker is a design direction, not yet HW evidence.
