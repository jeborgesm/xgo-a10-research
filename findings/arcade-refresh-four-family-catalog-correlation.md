# Arcade Refresh four-family catalog correlation and baseline-residue audit

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **BIN/CARD EVIDENCE — FOUR-FAMILY FRONTEND IDENTITY CLOSED; CPS1 BASELINE RESIDUE IDENTIFIED**

## Inputs

Current validated physical snapshot:
`20260924_PostGBCGBARefresh_CLEAN.zip`
SHA-256 `5df0b1340e7950ee072ccd72dd6f40fd84535d095f1dabd2359e7c5d9d60872e`

Four directly supplied stock ZFB fixtures:
- CPS1 `Cadillacs and Dinosaurs.zfb`
- CPS2 `Street Fighter Alpha 3.zfb`
- IGS/PGM `Knights of Valour.zfb`
- NeoGeo `The King of Fighters '94.zfb`

## Exact catalog correlation

The current physical baseline's resource triplets contain the four supplied outer filenames exactly.

| Family | list ID | index | slot0 | slot1 | slot2 |
|---|---:|---:|---|---|---|
| CPS1 | 7 | 0 | Cadillacs and Dinosaurs.zfb | 恐龙新世纪 | KLXSJ |
| CPS2 | 8 | 2 | Street Fighter Alpha 3.zfb | 少年街霸 3 | SNJB3 |
| IGS/PGM | 9 | 0 | Knights of Valour.zfb | 三国战纪 | SGZJ |
| NeoGeo | 10 | 0 | The King of Fighters '94.zfb | 拳皇 '94 | QH94 |

Combined with direct ZFB byte evidence:

```
CPS1   Cadillacs and Dinosaurs.zfb -> dino.zip
CPS2   Street Fighter Alpha 3.zfb  -> sfa3.zip
IGS    Knights of Valour.zfb       -> kov.zip
NeoGeo The King of Fighters '94.zfb -> kof94.zip
```

This closes the stock identity chain for representative entries:

```
list ID/family
 -> catalog slot0 outer ZFB filename
 -> physical ZFB reference record
 -> inner driver ZIP basename
 -> stock /ARCADE/bin/<driver>.zip launch target
```

Family is carried by list/catalog context, not by ZFB bytes.

## Metadata policy implication

OEM slot1 is localized Chinese display text and slot2 is a pinyin/romanized search key. For imported games without curated Chinese metadata, reuse the already-proven console fallback:

```
slot0 = exact generated outer ZFB filename
slot1 = friendly basename/title
slot2 = friendly basename/title
```

Stock search normalization already handles Latin letters/digits. Do not invent pinyin for user-added titles.

## Current baseline counts

The validated PostGBCGBA baseline currently contains:

```
CPS1   27
CPS2   28
IGS     6
NeoGeo 117
```

The original captured stock CPS1 count was 26.

The 27th current CPS1 record is:

`Pac-Man.zfb`

Repository history identifies this exactly as Test11 diagnostic residue. Test11 intentionally stable-appended Pac-Man to CPS1 to compare audio behavior and explicitly stated that the insertion was diagnostic only.

Therefore:
- the current physical baseline is functionally valid but its CPS1 catalog is not pristine OEM;
- `Pac-Man.zfb` must not be mistaken for a vendor CPS1 classification;
- future Arcade Refresh must preserve existing indices by default, so it must not silently delete this residue during ordinary Refresh;
- cleanup of the diagnostic entry is a separate maintenance action if desired.

This is analogous to other historical catalog residue already handled explicitly elsewhere in the project.

## ROM-free baseline limitation

The validated physical snapshot intentionally omits ROM payloads. It contains the Arcade save directory and resource triplets but not the full stock `/ARCADE/*.zfb` or `/ARCADE/bin/*.zip` inventory.

Therefore the complete 184-ZFB inventory matrix cannot be reconstructed from this ROM-free baseline alone.

The four supplied fixtures are sufficient to close representative stock wrapper/catalog semantics across every family, but classifying all historical unindexed ZFBs still requires the preserved original-card inventory/artifacts or additional physical files.

## Closed

- slot0 is the outer ZFB frontend/launch reference filename for all four families;
- representative outer ZFB -> driver ZIP mapping for all four;
- family comes from list/catalog context;
- slot1/slot2 semantics match the common XGO catalog model;
- current CPS1 27th entry is known Test11 diagnostic residue, not OEM family evidence.

## Still OPEN before candidate

- current golden binary list-count/cache handling for IDs 7..10;
- complete historical unindexed-ZFB classification;
- BIOS/parent dependencies;
- exact command-6 integration and helper placement;
- transaction-marker policy;
- deterministic ZFB generator and unit tests against all four supplied fixtures.
