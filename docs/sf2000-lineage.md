# SF2000 Lineage

The evidence indicates that the XGO software is not merely visually similar to an SF2000. It belongs to the same firmware/software lineage.

## High-confidence evidence

### `LCFG` firmware image

The XGO `bios/bisrv.asd` begins with `LCFG` and contains `logo.m2v` metadata. SF2000 reverse engineering independently documents this application-image structure.

### `Foldername.ini`

The tested XGO contains a `Resources/Foldername.ini` whose first line is literally:

```text
SF2000
```

It then enumerates the ROM-system directories used by the device.

### Resource filenames

The XGO carries the same deliberately odd resource naming scheme documented for stock SF2000 firmware. These include Windows-looking filenames whose contents are actually UI graphics, sounds or other embedded resources.

### ROM database filenames

The XGO uses the same unusual per-system database naming conventions documented by SF2000 tools such as Frogtool.

### Emulator code

Strings in the XGO `bisrv.asd` identify emulator/core code also associated with the SF2000 software stack, including FB Alpha, FCEUmm, Snes9x 2005 and gpSP.

## Firmware branch hypothesis

File timestamps and resource characteristics suggest the XGO firmware may have forked from an **SF2000 v1.6-era (August 2023) codebase**. This remains a hypothesis until a reproducible binary comparison against known stock images establishes common regions and divergence points.

## What lineage does NOT prove

It does not establish that:

- the XGO PCB is electrically compatible with an SF2000;
- the XGO uses every component used by an SF2000;
- stock SF2000 firmware will safely initialize the XGO display, controls or power hardware;
- an SF2000 firmware update can safely be copied over the XGO firmware;
- every inherited firmware feature is wired to functional XGO hardware.

The correct research strategy is therefore to treat known SF2000 work as a reference implementation and compare it against the working XGO firmware/hardware.

## Particularly useful upstream work

- vonmillhausen's SF2000 technical documentation
- FrogQEMU's firmware/architecture reverse engineering
- UniFrog's open-source hardware abstraction and input work
- SF2000 Multicore
- Tadpole
- Frogtool

UniFrog is especially interesting because it already abstracts multiple SF2000-family boards. A future research goal could be an explicit XGO board target rather than forcing the XGO to masquerade as an SF2000.
