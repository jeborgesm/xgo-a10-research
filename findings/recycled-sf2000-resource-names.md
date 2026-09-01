# XGO Recycled SF2000 Resource Names

Status: **multiple SF2000 resource filenames are deliberately repurposed for unrelated XGO arcade metadata, proving that filename compatibility does not imply resource compatibility.**

## Major finding

The XGO/DY19-style resource fork does more than omit stock SF2000 assets. It **reuses several stock SF2000 filenames for completely different data structures**.

This is important because the filenames look familiar enough that an SF2000 theme/resource tool could assume they have stock meanings and overwrite them with unrelated graphical assets.

Four especially clear collisions are now documented.

## Exact collisions

### `aepic.nec`

Stock SF2000 1.71 documentation identifies:

```text
aepic.nec
1008x164 BGRA
Korean user-settings icons/labels artwork
```

XGO contains:

```text
aepic.nec
140 bytes
PGM/IGS curated-group Chinese display-title list
```

Its XGO strings correspond to the six-game PGM/IGS metadata group and line up entry-for-entry with `subst.tax` and `sensc.bvs`.

### `djoin.nec`

Stock SF2000:

```text
djoin.nec
1008x164 BGRA
Spanish user-settings icons/labels artwork
```

XGO:

```text
djoin.nec
808 bytes
CPS2 Chinese display-title list
```

It pairs with XGO CPS2 filename database `kjbyr.tax` and search-key database `ke89a.bvs`.

### `ke89a.bvs`

Stock SF2000:

```text
ke89a.bvs
1008x164 BGRA
Portuguese user-settings icons/labels artwork
```

XGO:

```text
ke89a.bvs
357 bytes
CPS2 compact search-key / romanization database
```

### `ntdll.bvs`

Stock SF2000:

```text
ntdll.bvs
1008x164 BGRA
Polish user-settings icons/labels artwork
```

XGO:

```text
ntdll.bvs
1,276 bytes
Neo Geo compact search-key / romanization database
```

It pairs with XGO Neo Geo filename database `rmapi.tax` and Chinese-title database `pcadm.nec`.

## Why this appears deliberate

The XGO frontend exposes only six languages:

```text
English
Chinese
Arabic
Hebrew
Spanish
Russian
```

while later stock SF2000 firmware has a broader multilingual resource set containing dedicated settings artwork for languages including Korean, Portuguese, Polish, etc.

Several of those now-unneeded stock language-art filename slots were therefore available for reuse in the XGO fork. The XGO resource table points those same names at tiny string/index files instead of large image resources.

This is **STRONG EVIDENCE of deliberate resource-table recycling during the OEM fork**, rather than accidental filename collision.

It also helps explain how the vendor could expand the arcade frontend into separate CPS1/CPS2/PGM/Neo Geo metadata groups without redesigning the surrounding resource-loader architecture: existing resource-table slots/names could be reassigned to new roles.

## Compatibility implication

A resource utility must identify the **device/resource schema**, not merely recognize familiar filenames.

For example, replacing XGO `aepic.nec` with a stock SF2000 Korean-settings image would destroy the XGO PGM/IGS title database. Replacing `ke89a.bvs` with stock Portuguese artwork would destroy CPS2 search metadata.

Therefore:

```text
same filename != same semantic resource
```

between SF2000 and XGO.

This is stronger than the previous general warning that the XGO is a board-specific/software fork. It is a concrete example where apparent file-level compatibility is actively dangerous.

## Relationship to DY19 fork evidence

The XGO's ten-system resource naming/layout already matches the public DY19-oriented Tadpole fork for the expanded arcade sections. The repurposed filename behavior is consistent with that software lineage: the vendor reused the inherited SF2000 resource mechanism while assigning new meanings to slots required by the expanded menu/content layout.

## Confidence

### CONFIRMED

- XGO file sizes and parsed contents establish the XGO roles listed above;
- public stock SF2000 resource documentation assigns the same filenames to large language-settings graphics;
- the stock and XGO meanings are mutually incompatible;
- XGO exposes only six language choices while several repurposed stock names belonged to other language assets.

### STRONG EVIDENCE

- the filename reuse was deliberate resource-table recycling during the XGO/DY19-style fork;
- discarded multilingual resource slots were repurposed to support expanded arcade metadata.

### OPEN

- complete mapping of every stock-resource slot repurposed in the XGO build;
- exact development sequence in which the multilingual SF2000 table was transformed into the XGO/DY19-style layout;
- whether sibling DY19/X60/Q19 cards reuse precisely the same individual stock filename slots.
