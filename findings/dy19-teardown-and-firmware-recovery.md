# DY19 teardown and firmware-recovery evidence

Date: 2026-09-07

## Public DY19 teardown exists

A 4PDA owner, {{XENON}}, opened a DY19 and published photographs of the internals on 2024-09-19.

The owner reports two directly observable/physical findings:

- the installed battery is approximately **4000mAh**, despite retail advertising around 6000mAh;
- the main processor marking was intentionally/physically removed ("spiliв все надписи" / markings ground off).

The post explicitly says that photographs of the internals were attached.

Source:
https://4pda.to/forum/index.php?showtopic=1090810&st=0
post #12

### Evidence status

The existence of the teardown and the owner's battery/marking observations are confirmed from the indexed 4PDA post text.

The actual attachment image bytes have **not yet been recovered into this repository**. They remain a priority archival target.

Do not infer the hidden processor identity from the scraped package. DY19's software ancestry is independently established through firmware/runtime evidence.

## Stock DY19 firmware is unusually recoverable

The same 4PDA thread records several firmware artifacts:

- seller-supplied stock firmware;
- password `1234` for one original Chinese share;
- attached `DY19 TF card files.torrent` (74.75KB);
- `multicore_DY19.zip` (~4.4MB) containing a DY19-specific BIOS/application replacement;
- `dy19_13menu.rar` (92.93MB), a later 13-menu modified build.

Most importantly, a 2025 owner reports that the nominal **~30GB Chinese stock image contains only about 40MB of actual files**: principally BIOS/application data and directory layout, with games absent.

That makes the firmware payload far easier to preserve and compare than the nominal image size suggests.

Source:
https://4pda.to/forum/index.php?showtopic=1090810&st=20

## Stock-card behavior is directly relevant to XGO game-list archaeology

A DY19 owner reports that simply copying ROMs into the ordinary system folders does not make them appear in the stock frontend. Tadpole/frogtool-style tooling is used to register games and artwork; arbitrary files remain accessible through the Download folder.

This is the same broad architecture class now established for XGO:

```text
ROM file
  + list/database record
  + artwork/package metadata
  -> visible stock-menu game
```

Therefore a recovered DY19 stock or 13-menu build can be compared directly with XGO's synchronized catalog/list-triplet implementation.

## Bootloader / board adaptation warning

The thread also contains a strong hardware-adaptation lesson:

- related SF2000/GB300 boot-fix procedures can boot DY19-family devices;
- nevertheless the correct DY19 `bisrv.asd`/BIOS is needed for working controls;
- one owner reports stock-like firmware booting but no controls until replacing BIOS.

This supports the repository's existing subsystem-compatibility model: H1512-family boot/application structure is shared while display/input/power GPIO adaptation remains board specific.

## Immediate recovery targets

Priority order:

1. recover the 4PDA teardown attachment images;
2. recover `multicore_DY19.zip` or its `bisrv.asd`;
3. recover the small stock BIOS/resources payload rather than the ROM-heavy nominal image;
4. recover `dy19_13menu.rar`;
5. compare the later 13-menu resource/list implementation to XGO's current game-list scanner work.

## Why DY19 remains especially valuable

Unlike DY14, DY19 already has software evidence extremely close to the XGO resource/frontend branch. Unlike E2, there are multiple small DY19 firmware artifacts known by exact filename.

A genuine DY19 `bisrv.asd` plus teardown photos would provide both sides of the comparison:
- software/function lineage;
- hardware adaptation.
