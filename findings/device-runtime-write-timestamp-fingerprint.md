# XGO Device Runtime-Write Timestamp Fingerprint

Status: **a distinctive zero/epoch timestamp pattern identifies files written or rewritten by the XGO runtime.**

## Major finding

The original card inventory contains exactly **63 files** whose Windows `LastWriteTime` is:

```text
12/31/1600 6:00:00 PM
```

The inventory was produced in Central time. That local value corresponds to:

```text
1601-01-01 00:00:00 UTC
```

which is the zero epoch of Windows FILETIME.

The striking part is not merely the anomalous date. **Every one of the 63 files belongs to a class that the XGO firmware is known to create or rewrite at runtime.**

## Exact classification

The 63 epoch-stamped files divide as:

```text
54 emulator save-state files (*.sa0 .. *.sa3)
 5 GBA battery-save files (*.sav)
 4 frontend runtime-state/index files
---
63 total
```

There are no ordinary ROM packages, UI graphics, fonts, BIOS files, music files, or firmware binaries with this timestamp.

## The four runtime frontend files

The four `Resources` files are:

```text
Archive.sys
Falas.clk
Hisas.boa
tsmfk.tax
```

Their roles have already been statically established:

```text
Archive.sys  persisted language / TV-system / volume state
Falas.clk    favorites database
Hisas.boa    history database
tsmfk.tax    generated/sorted User ROM index
```

The XGO executable contains active write/update paths for these classes of data.

This is unusually strong corroboration that the epoch timestamp is produced by the **device-side write path**, not by the original Windows-side card-content staging process.

## Save states

All 54 epoch-stamped emulator states use the normal XGO save-state naming convention:

```text
<game>.sa0
<game>.sa1
<game>.sa2
<game>.sa3
```

They span multiple emulators/directories, including:

```text
ROMS/save
FC/save
GB/save
GBA/save
SFC/save
ARCADE/save
```

Examples include:

```text
ROMS/save/Super Mario World (USA).SMC.sa0
FC/save/Mega Man 1.zfc.sa0 .. sa3
GB/save/Batman.zgb.sa0
SFC/save/Battletoads In Battlemaniacs.zsf.sa0
ARCADE/save/dino.zip.sa0 .. sa3
ARCADE/save/mslug.zip.sa0 .. sa1
```

The common timestamp across different emulator cores strongly argues that the timestamp originates in the shared XGO/frontend filesystem environment rather than in one emulator's state serializer.

## Five GBA `.sav` files were runtime-touched

Five GBA battery-save sidecars have the same epoch timestamp instead of the dominant factory-provisioning timestamp documented separately:

```text
Megaman Zero.sav                           32768 bytes
Final Fight One.sav                         512 bytes
F-Zero - Maximum Velocity.sav             32768 bytes
Street Fighter Alpha 3 Upper.sav           8192 bytes
The King of Fighters EX2 - Howling Blood (CN).sav
                                               512 bytes
```

The other **485 of 490** GBA `.sav` files retain the common batch timestamp:

```text
2023-06-29 13:12:10
```

This strongly indicates that the five epoch-stamped save files were subsequently written/re-written by the device after the bulk save-sidecar provisioning pass.

Do not infer who caused those writes. They could reflect factory QA, distributor testing, owner gameplay, or another runtime session. The evidence identifies **device-side modification**, not the human/operator responsible.

## Why the timestamp becomes 1601

The device has no evidence of maintaining a normal wall-clock timestamp for these writes. A filesystem write with an unset/zero host-time value can surface through Windows APIs as the FILETIME epoch, `1601-01-01T00:00:00Z`.

The exact local display in the captured inventory is six hours earlier because the inventory was generated under a Central-time Windows environment:

```text
UTC 1601-01-01 00:00:00
 -> local 1600-12-31 18:00:00
```

This explains the otherwise impossible-looking year 1600 without treating it as a real historical FAT timestamp.

The underlying HC15xx/FatFs timestamp-generation implementation has not yet been traced to the exact function responsible, so the software mechanism should remain open beyond the observed zero-time behavior.

## Card archaeology implication

This gives the project a new provenance signal:

```text
normal 2022/2023 timestamp
    -> likely preserved from PC/OEM content assembly

1601 FILETIME-zero timestamp
    -> strong device-runtime write/touch marker
```

It can now be used when reading the original file listing to separate relatively static factory payload from mutable data created after the device actually ran.

This is especially useful because the card itself contains residue from several manufacturing/content-generation waves. The epoch marker identifies a different layer: **post-assembly runtime state**.

## Related filesystem chronology

Other card metadata provides additional staging context:

```text
System Volume Information                 2023-02-27 15:36:58
System Volume Information/WPSettings.dat  2023-02-27 15:36:58
System Volume Information/IndexerVolumeGuid
                                          2023-02-27 15:36:58
RECYCLER directory                         2023-08-07 11:04:36
bisrv.asd                                  2023-08-12 02:32:14
```

The `save` directories themselves generally retain older normal timestamps (for example 2022-07-13), while files later written inside them carry the epoch timestamp. That separation further supports a distinction between **pre-created directory skeleton** and **device-generated contents**.

These dates are filesystem metadata, not guaranteed source/build dates; copies can preserve or rewrite timestamps. They should be used as provenance clues rather than absolute release chronology.

## Confidence

### CONFIRMED

- exactly 63 files have the `12/31/1600 6:00 PM` timestamp in the original inventory;
- all 63 are mutable/runtime-data classes;
- breakdown is 54 save states, 5 GBA saves, and 4 frontend state/index files;
- no static ROM/resource/font/BIOS/firmware payload shares the timestamp;
- the four Resource files are known runtime-persisted/generated files;
- the five affected GBA saves are the only exceptions to the 485-file bulk provisioning timestamp pattern.

### STRONG EVIDENCE

- the timestamp is a fingerprint of XGO-side file creation or rewrite with unset/zero wall-clock time;
- the five GBA saves were touched after the OEM/bulk provisioning pass;
- save-state files carrying this marker were created or rewritten during actual device runtime.

### OPEN

- exact HCRTOS/FatFs routine that supplies the zero timestamp;
- whether every possible XGO-created file always receives this marker;
- operator/session provenance of the individual save states and five modified GBA saves;
- whether the internal SoC has an RTC path that is simply never initialized by this firmware.
