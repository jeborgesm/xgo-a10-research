# XGO Software Fork Identification — DY19 Resource Layout

Status: **major new lineage finding**.

## Discovery

A 2025 fork of Tadpole contains an explicit commit titled `DY19` adapting the SF2000 tooling to the DY19 power-bank handheld. The changes encode the DY19 system/resource table.

That table matches the preserved XGO SD card **exactly for all 10 systems and all 30 list-resource filenames**.

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

## This resolves the repeated ARCADE sections

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

The DY19 tooling supplies the missing semantic labels for the four repeated Arcade slots:

```text
list id 7  -> CPS1
list id 8  -> CPS2
list id 9  -> NEOGEO
list id 10 -> IGS
```

This closes the earlier open question about XGO list IDs 8-10. They are not arbitrary duplicate Arcade databases; they are separate arcade-family categories hidden behind the same displayed `ARCADE` label.

## Why this is stronger than the earlier unnamed-device match

An earlier 4PDA report reproduced XGO's exact `Foldername.ini` from an unnamed AliExpress console. At that point the device family was unknown.

The DY19 Tadpole adaptation independently provides the exact 10-system structure and exact obfuscated resource filenames. Public DY19 descriptions also list the supported platforms as:

```text
FC, SFC, MD, GB, GBC, GBA, CPS1, CPS2, IGS, NEOGEO
```

The match therefore spans:

- system count/order;
- four-way Arcade subdivision;
- all 30 resource filenames;
- SF2000-derived firmware/resource architecture;
- the unusual game-console + power-bank product class.

## Important distinction

This does **not yet prove the XGO hardware is literally a rebadged DY19 PCB**. The external enclosure, battery, display, controller wiring, RF implementation, or board revision may differ.

The evidence is sufficient, however, to identify the XGO's **software/resource fork as DY19-family or a very closely shared sibling of the DY19 fork**.

This changes the research priority: DY19 firmware, SD images, controller accessories, teardown photographs, and community modifications are now first-class comparators rather than generic SF2000 relatives.

## Additional DY19 tooling clue

The same `DY19` Tadpole commit changes the expected embedded boot-logo dimensions from stock SF2000's 512x200 to 128x128 while retaining the same `bad_exception` firmware landmark and button-map pre/post signatures. This is another example of the DY19 fork preserving deep SF2000 firmware structure while changing frontend-specific data.

The XGO image independently preserves those same deep landmarks at shifted offsets, as documented in `sf2000-171-build-fingerprint.md`.

## Confidence

### CONFIRMED

- all 30 DY19 system-list resource filenames encoded by the DY19 Tadpole adaptation exist on the original XGO SD card;
- XGO's four repeated Arcade slots map naturally to CPS1, CPS2, NEOGEO and IGS in the DY19 table;
- XGO list IDs 7-10 can therefore be assigned CPS1/CPS2/NEOGEO/IGS respectively;
- DY19 uses the same SF2000-derived resource architecture.

### STRONG EVIDENCE

- XGO software belongs to the DY19 firmware/resource fork family or an extremely close sibling derived from the same OEM build;
- the previously reported unnamed `11 7 0` console is likely part of this same fork family.

### NOT YET CONFIRMED

- XGO and retail DY19 use byte-identical `bisrv.asd` firmware;
- XGO and DY19 use the same PCB or GPIO assignments;
- DY19 external-controller electrical protocol is identical to the XGO Handle Interface;
- whether XGO is a direct DY19 rebadge, a later hardware revision, or another product built from the same OEM software package.

## Next targets

1. Obtain/preserve the DY19 stock `bisrv.asd` and compare it byte-for-byte / function-for-function with XGO.
2. Compare DY19 controller/second-player accessory wiring with XGO's reconstructed B15/L0/B7 serial scanner.
3. Compare DY19 teardown PCB photos against the XGO PCB photographs.
4. Revisit XGO UI/resource semantics using the now-known CPS1/CPS2/NEOGEO/IGS category identities.
