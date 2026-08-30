# Firmware and SD Card

## Card layout observed

The tested original 32 GB card appears in Windows Disk Management as one FAT32 primary partition. Windows Explorer shows these root directories:

```text
ARCADE/
bios/
FC/
GB/
GBA/
GBC/
MD/
RECYCLER/
Resources/
ROMS/
SFC/
```

The physical XGO does not boot normally without the microSD card.

## `bios/`

Observed files include:

```text
bisrv.asd
gba_bios.bin
neogeo.zip
neogeo1.zip
pgm.zip
```

`bisrv.asd` is the key firmware specimen. It begins with the ASCII magic `LCFG` and references `logo.m2v`, matching the application-image structure documented by SF2000 reverse-engineering projects.

Binary strings recovered from the XGO image include evidence of emulator/core code such as:

- FB Alpha v0.2.97.42
- FCEUmm
- Snes9x 2005 v1.36
- gpSP
- PicoDrive-related code/options
- libretro-style core configuration

The image also contains Unix-like filesystem paths such as `/mnt/sda1/bios/gba_bios.bin`, `/dev/rda1`, `/mnt/rda1`, and `/mnt/rda1/myfs`.

## `Resources/`

The resource directory contains intentionally misleading Windows-like filenames (`pagefile.sys`, DLL-like names, etc.). Comparison with documented SF2000 resources shows that this naming convention is inherited from that platform.

`Foldername.ini` on the tested XGO begins with `SF2000` and enumerates the system folders, providing unusually direct lineage evidence.

Many resource files have fixed framebuffer-like sizes and raw-looking binary contents. File extensions should not be trusted as indicators of their actual format.

## ROM databases

The XGO uses unusual ROM-list/database filenames also documented in the SF2000 ecosystem, including `.tax`, `.nec`, `.bvs`, and system-specific ROM extensions such as `.zfc`, `.zgb`, `.zmd`, and `.zsf`.

## Boot architecture — current model

Strong working model:

1. internal boot code initializes enough hardware to access the microSD card;
2. an SF2000-family `LCFG` application image (`bios/bisrv.asd`) is loaded;
3. the application uses the FAT32 card for resources, emulator data, ROM lists, BIOS files and games.

The exact internal bootloader and any data in pre-partition/reserved sectors remain to be examined from the preserved full-card image.
