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

## Newly confirmed CPU/SDK lineage

A deeper string pass over the XGO `bisrv.asd` produced direct platform evidence that was not recorded in the initial research foundation.

The binary contains:

```text
h1512_gpio_pinmux_sel
get_clock_h1512() parameter error, nothing to do!!!!
```

and the SDK/compiler identification string:

```text
Libcore version 3.6.1.1@SDK3.AB_20210616
(gcc version 3.4.4 mipssde-6.06.01-20070420)
```

This materially strengthens the hardware identification:

- the firmware was built for an **H1512-family platform**;
- the software is compiled for **MIPS** using the MIPS SDE toolchain;
- the same Libcore/SDK/compiler string has been independently recovered from stock SF2000 firmware.

This is substantially stronger evidence than reseller specifications or the previously circulated RK3566 claim. The XGO firmware itself is a MIPS/H1512-targeted image and is therefore in the same SoC/software family as the SF2000.

The exact commercial marking/revision of the physical XGO SoC still deserves confirmation from PCB photography before documenting a specific package marking as fact. However, **RK3566 is now contradicted by direct firmware evidence** and should not be treated as a plausible working identification for this specimen.

## RF/controller code evidence

The same binary also contains explicit platform-level RF test strings:

```text
RF_IC Test Fail !
RF_IC Test Pass!
```

These strings are separate from emulator Player 2 option text and therefore show that the XGO image includes code intended to initialize or test an RF integrated circuit at the system layer.

This is important because stock SF2000 hardware uses a 2.4 GHz RF receiver for its external controllers. It raises a new question: did the XGO retain an RF-controller implementation in firmware even if the XGO enclosure exposes a wired `Handle Interface`, or does the XGO board contain both mechanisms?

An initial search for several exact GPIO shadow constants currently used by UniFrog's reconstructed SF2000 RF sequence did **not** find those constants verbatim in the XGO image. This negative result is useful but not decisive: the XGO code may use a different SDK routine, compiler-generated register programming, another RF implementation, or different board initialization values.

## Internal flash updater path

The XGO firmware contains a complete-looking internal flash update path, including these strings:

```text
/mnt/sda1/UpdateFirmware/Firmware.upk
STO_SFLASH_0
NOR flash id_buf[0]=0x%08X, id_buf[1]=0x%08X, id_buf[2]=0x%08X
spi_nor_cmd_read
spi_nor_cmd_write
Update success.
Update fail.
```

This is an especially strong SF2000-family match. The documented SF2000 permanent bootloader patch uses the **same** SD-card path: `UpdateFirmware/Firmware.upk`. In other words, the XGO's application firmware appears to retain the same mechanism used by SF2000 firmware to program internal SPI NOR flash.

This does **not** mean that an SF2000 `Firmware.upk` is safe to run on the XGO. The update mechanism may be shared while the contents of internal flash differ by board revision. A mismatched update could make the device unbootable and require an external SPI programmer for recovery.

For now the updater should be treated as a reverse-engineering opportunity, not an installation method. Useful future work includes:

1. documenting the `Firmware.upk` container format;
2. determining which NOR regions the XGO updater writes;
3. comparing a known SF2000 bootloader patch with the XGO updater's expectations;
4. identifying the XGO SPI NOR chip and obtaining a hardware backup before any write experiment.

## Display-driver clues

The image contains a broad vendor display-driver library with strings including:

```text
LCD_TYPE_320_240_CONFIGE
LCD_TYPE_320_240_8347B_CONFIGE
ili9341.c
lcd_ili9341_320_240_init start
lcd_ili9341_320_240_init end
```

These strings show that the linked SDK contains 320x240 display support, including an ILI9341 path, but they do **not** yet identify which panel driver the XGO actually selects at runtime. The library also contains many unrelated panel definitions, so runtime/PCB evidence is required before assigning an LCD controller model.

## `Resources/`

The resource directory contains intentionally misleading Windows-like filenames (`pagefile.sys`, DLL-like names, etc.). Comparison with documented SF2000 resources shows that this naming convention is inherited from that platform.

`Foldername.ini` on the tested XGO begins with `SF2000` and enumerates the system folders, providing unusually direct lineage evidence.

Many resource files have fixed framebuffer-like sizes and raw-looking binary contents. File extensions should not be trusted as indicators of their actual format.

## ROM databases

The XGO uses unusual ROM-list/database filenames also documented in the SF2000 ecosystem, including `.tax`, `.nec`, `.bvs`, and system-specific ROM extensions such as `.zfc`, `.zgb`, `.zmd`, and `.zsf`.

## Boot architecture — current model

Strong working model:

1. internal boot code in SPI NOR initializes enough hardware to access the microSD card;
2. an SF2000-family `LCFG` application image (`bios/bisrv.asd`) is loaded;
3. the application uses the FAT32 card for resources, emulator data, ROM lists, BIOS files and games;
4. the application also contains an SD-triggered mechanism capable of rewriting internal SPI NOR using `UpdateFirmware/Firmware.upk`.

The exact internal bootloader contents remain to be recovered from the XGO hardware. The preserved full-card image can still answer questions about the card's partition/reserved-sector layout, but the strongest current evidence indicates that the bootloader itself lives in internal flash rather than on the microSD card.
