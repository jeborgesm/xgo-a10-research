# XGO Software Fork Identification — DY19 Resource Layout

Status: **major lineage finding, now strengthened by direct XGO database-content evidence**.

## Discovery

A 2025 fork of Tadpole contains an explicit commit titled `DY19` adapting the SF2000 tooling to the DY19 power-bank handheld. The changes encode the DY19 system/resource table.

That table matches the preserved XGO SD card for the full 10-system layout and all 30 list-resource filenames:

```text
system   list/resource triplet
FC       rdbui.tax   fhcfg.nec   nethn.bvs
SFC      urefs.tax   adsnt.nec   xvb6c.bvs
MD       scksp.tax   setxa.nec   wmiui.bvs
GB       vdsdc.tax   umboa.nec   qdvd6.bvs
GBC      pnpui.tax   wjere.nec   mgdel.bvs
GBA      vfnet.tax   htuiw.nec   sppnp.bvs
CPS1     mswb7.tax   msdtc.nec   mfpmp.bvs
CPS2     kjbyr.tax   djoin.nec   ke89a.bvs
NEOGEO   rmapi.tax   pcadm.nec   ntdll.bvs
IGS      subst.tax   aepic.nec   sensc.bvs
```

Every one of those filenames exists on the original XGO card.

## Important correction: filenames alone are positional, not unique semantic identifiers

A later cross-check against GB300v2 community tooling showed that at least one of these obfuscated triplets is reused positionally by another HC15xx-family fork for a different system. For example, GB300v2 tooling uses:

```text
kjbyr.tax / djoin.nec / ke89a.bvs -> PCE
```

while the DY19 adaptation assigns that same triplet to CPS2.

Therefore the opaque filenames **cannot by themselves prove system identity or DY19 lineage**. They are inherited resource slots whose semantics can be changed by an OEM fork.

This prompted a direct inspection of the preserved XGO resource databases.

## Direct XGO database contents confirm the four Arcade identities

The first file of each XGO Arcade resource triplet contains the indexed game filenames. The contents independently identify each slot:

### Slot 7 — `mswb7.tax` = CPS1

Representative XGO entries include:

```text
Cadillacs and Dinosaurs.zfb
Captain Commando.zfb
Carrier Air Wing.zfb
Dynasty Wars.zfb
Final Fight.zfb
Ghouls'n Ghosts.zfb
Knights of the Round.zfb
Street Fighter II'- Champion Edition.zfb
Street Fighter II- The World Warrior.zfb
The Punisher.zfb
```

This is a characteristic CPS1 set.

### Slot 8 — `kjbyr.tax` = CPS2

Representative XGO entries include:

```text
Super Street Fighter II- The New Challengers.zfb
Street Fighter Alpha 2.zfb
Street Fighter Alpha 3.zfb
Alien vs. Predator.zfb
Armored Warriors.zfb
Battle Circuit.zfb
Darkstalkers- The Night Warriors.zfb
Dungeons & Dragons- Shadow over Mystara.zfb
Marvel Vs. Capcom- Clash of Super Heroes.zfb
Progear.zfb
```

This is directly consistent with CPS2, not the PCE meaning used by a different GB300v2 fork.

### Slot 9 — `rmapi.tax` = Neo Geo

Representative XGO entries include:

```text
The King of Fighters '94.zfb
The King of Fighters '95.zfb
The King of Fighters '97.zfb
Metal Slug -Super Vehicle-001.zfb
Metal Slug 2 -Super Vehicle-001.zfb
Metal Slug 3.zfb
Garou -Mark of the Wolves.zfb
Fatal Fury Special.zfb
Samurai Shodown II.zfb
```

This directly identifies the slot as Neo Geo.

### Slot 10 — `subst.tax` = IGS/PGM

The XGO file contains:

```text
Knights of Valour.zfb
Knights of Valour 1.15.zfb
Knights of Valour Plus.zfb
Knights of Valour Plus a.zfb
Oriental Legend.zfb
Dragon World II.zfb
```

These are characteristic IGS PolyGame Master titles. The XGO BIOS directory also contains `pgm.zip`, independently consistent with PGM/IGS support.

## This resolves the repeated ARCADE sections independently of DY19

XGO `Foldername.ini` declares:

```text
ROMS
FC
SFC
MD
GB
GBC
GBA
ARCADE
ARCADE
ARCADE
ARCADE
```

and ends with:

```text
11 7 0
```

The database contents now establish directly from the XGO card:

```text
list id 7  -> CPS1
list id 8  -> CPS2
list id 9  -> NEOGEO
list id 10 -> IGS/PGM
```

The four visible `ARCADE` labels are therefore four independent arcade-family databases, not duplicate lists.

## Why DY19 remains a strong lineage match

The semantic mapping recovered directly from the XGO databases is the **same mapping encoded by the DY19 Tadpole adaptation**, including the non-stock expansion to CPS1, CPS2, Neo Geo and IGS in positions 7-10.

Public DY19 descriptions independently list the supported platforms as FC, SFC, MD, GB, GBC, GBA, CPS1, CPS2, IGS and Neo Geo.

The match therefore spans:

- system count and order;
- four-way Arcade subdivision;
- actual semantic identity of slots 7-10;
- all 30 resource-slot filenames;
- SF2000-derived firmware/resource architecture;
- the unusual game-console + power-bank product class;
- external two-player/gamepad support advertised for DY19.

This is materially stronger than a filename-only match.

## Important distinction

This does **not yet prove the XGO hardware is literally a rebadged DY19 PCB**, nor that its `bisrv.asd` is byte-identical to a retail DY19 image. The enclosure, battery, display, controller wiring, RF implementation, or board revision may differ.

The current evidence supports identifying the XGO software/resource layout as **DY19-family or a very closely shared sibling of the same OEM fork**.

DY19 firmware, SD images, controller accessories, teardown photographs, and community modifications are therefore first-class comparators.

## Additional DY19 tooling clue

The same `DY19` Tadpole commit changes the expected embedded boot-logo dimensions from stock SF2000's 512x200 to 128x128 while retaining the same `bad_exception` firmware landmark and button-map pre/post signatures. This is another example of the DY19 fork preserving deep SF2000 firmware structure while changing frontend-specific data.

The XGO image independently preserves those same deep landmarks at shifted offsets, as documented in `sf2000-171-build-fingerprint.md`.

## Confidence

### CONFIRMED directly from the XGO SD card

- list 7 database content is CPS1;
- list 8 database content is CPS2;
- list 9 database content is Neo Geo;
- list 10 database content is IGS/PGM;
- the four repeated visible `ARCADE` entries represent distinct arcade-family lists;
- the resource filenames are opaque positional slots and cannot safely be assigned semantics without examining the fork or database contents.

### CONFIRMED comparison evidence

- the DY19 Tadpole adaptation uses the same 10-system semantic ordering as the XGO databases;
- all 30 resource-slot filenames encoded by that adaptation exist on the original XGO card;
- another HC15xx fork (GB300v2) can reuse an inherited triplet with a different semantic role, demonstrating why content-level confirmation matters.

### STRONG EVIDENCE

- XGO software belongs to the DY19 firmware/resource fork family or an extremely close sibling derived from the same OEM build;
- the previously reported unnamed `11 7 0` console is likely part of this broader fork family.

### NOT YET CONFIRMED

- XGO and retail DY19 use byte-identical `bisrv.asd` firmware;
- XGO and DY19 use the same PCB or GPIO assignments;
- DY19 external-controller electrical protocol is identical to the XGO Handle Interface;
- whether XGO is a direct DY19 rebadge, a later hardware revision, or another product built from the same OEM software package.

## Next targets

1. Obtain/preserve a DY19 stock `bisrv.asd` and compare it byte-for-byte / function-for-function with XGO.
2. Compare DY19 controller/second-player accessory wiring with XGO's reconstructed B15/L0/B7 serial scanner.
3. Compare DY19 teardown PCB photos against the XGO PCB photographs.
4. Determine whether the DY19 controller connector exposes the same unusual serial load/clock/data behavior as XGO.
