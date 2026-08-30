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

Binary strings recovered from the XGO image include evidence of emulator/core code such as FB Alpha v0.2.97.42, FCEUmm, Snes9x 2005 v1.36, gpSP and PicoDrive-related code/options. The image also contains Unix-like filesystem paths such as `/mnt/sda1/bios/gba_bios.bin`, `/dev/rda1`, `/mnt/rda1`, and `/mnt/rda1/myfs`.

## Confirmed CPU/SDK lineage

The binary contains:

```text
h1512_gpio_pinmux_sel
get_clock_h1512() parameter error, nothing to do!!!!
Libcore version 3.6.1.1@SDK3.AB_20210616
(gcc version 3.4.4 mipssde-6.06.01-20070420)
```

This is direct evidence that the firmware targets an **H1512-family MIPS platform** using the MIPS SDE toolchain. The same Libcore/SDK/compiler identification has been independently recovered from stock SF2000 firmware.

The exact commercial marking/revision of the physical XGO SoC still deserves PCB confirmation. However, the circulated RK3566 identification is contradicted by this specimen's own firmware and should not be treated as a plausible working identification.

## Confirmed stock-like RF driver

Disassembly goes substantially beyond the previously identified `RF_IC Test Pass!` / `RF_IC Test Fail !` strings.

A real RF initialization routine appears near virtual address `0x8035deb0`, with a call site near `0x8034c7ac`. The code directly manipulates the same HC15xx GPIO words and signal masks used by the reconstructed SF2000 wireless-controller path:

```text
MMIO: 0xb8800050, 0xb8800054, 0xb8800058
      0xb8800354, 0xb8800358

DATA  = 0x08000000
CLOCK = 0x10000000
CS    = 0x20000000
```

Most importantly, the XGO performs the same RF self-test sequence documented by current UniFrog work:

```text
write reg 0x53 = 0x5a
write reg 0x53 = 0xa5
write reg 0x25 = 0xa5
read  reg 0x05
compare with 0xa5
```

Representative XGO instructions around `0x8035e0d4`:

```text
8035e0d4  addiu $5,$zero,0x5a
8035e0d8  jal   0x8035d37c
8035e0dc  addiu $4,$zero,0x53
...
8035e0e8  addiu $5,$zero,0xa5
8035e0ec  jal   0x8035d37c
8035e0f0  addiu $4,$zero,0x53
...
8035e0fc  addiu $5,$zero,0xa5
8035e100  jal   0x8035d37c
8035e104  addiu $4,$zero,0x25
...
8035e110  jal   0x8035cf74
8035e114  addiu $4,$zero,0x05
8035e118  addiu $3,$zero,0xa5
8035e11c  beq   $2,$3,0x8035e1b8
```

On success, execution continues into RF configuration including writes such as `0x3d=0x20`, `0xfc=0`, `0xe1=0`, `0xe2=0`, `0x27=0x70`, `0x39=1`, and `0x20=0x8e`, plus buffer reads from registers `0x3f` and `0x3e`.

This is **confirmed firmware-level evidence** that the XGO retained the SF2000-family RF controller protocol and bit-banged GPIO implementation. It does not by itself prove that the matching radio IC is physically populated on the XGO PCB.

An earlier literal search failed to find several whole-register shadow constants used by modern UniFrog. The disassembly explains that result: XGO dynamically manipulates the same MMIO registers and individual DATA/CLOCK/CS masks rather than embedding every reconstructed UniFrog shadow value verbatim.

See [`../findings/rf-driver.md`](../findings/rf-driver.md) for the focused evidence record.

## USB strings — revised interpretation

The previously noted strings:

```text
usb device attach
usb device detach
[FS]USB lun_num = %d
/dev/rda1
/mnt/rda1
/mnt/rda1/myfs
```

occur together in filesystem/mount code. They are therefore strong evidence for a USB **mass-storage/filesystem** path but are not useful evidence for generic HID/gamepad support.

Known H1512/SF2000 research identifies separate USB0/USB1 controller windows around virtual `0xb8844000` and `0xb8850000`. By contrast, XGO code accessing `0xb884c000` is SDIO-related; that address should not be misidentified as USB.

## Internal flash updater path

The XGO firmware contains:

```text
/mnt/sda1/UpdateFirmware/Firmware.upk
STO_SFLASH_0
NOR flash id_buf[0]=0x%08X, id_buf[1]=0x%08X, id_buf[2]=0x%08X
spi_nor_cmd_read
spi_nor_cmd_write
Update success.
Update fail.
```

This is an especially strong SF2000-family match. The documented SF2000 permanent bootloader patch uses the same SD-card path, `UpdateFirmware/Firmware.upk`, to program internal SPI NOR.

This does **not** mean an SF2000 `Firmware.upk` is safe to run on the XGO. A mismatched internal-flash image could make the device unbootable and require an external programmer for recovery. The updater is a reverse-engineering opportunity, not an installation recommendation.

## Display-driver clues

The image contains a broad vendor display-driver library with strings including:

```text
LCD_TYPE_320_240_CONFIGE
LCD_TYPE_320_240_8347B_CONFIGE
ili9341.c
lcd_ili9341_320_240_init start
lcd_ili9341_320_240_init end
```

These show linked 320x240 display support, including an ILI9341 path, but do not identify which panel driver the XGO actually selects at runtime.

## `Resources/`

The resource directory contains intentionally misleading Windows-like filenames (`pagefile.sys`, DLL-like names, etc.). Comparison with documented SF2000 resources shows that this naming convention is inherited from that platform.

`Foldername.ini` begins with `SF2000` and enumerates the system folders. Many resource files have fixed framebuffer-like sizes and raw binary contents; extensions should not be trusted as format indicators.

## ROM databases

The XGO uses unusual ROM-list/database filenames also documented in the SF2000 ecosystem, including `.tax`, `.nec`, `.bvs`, and system-specific ROM extensions such as `.zfc`, `.zgb`, `.zmd`, and `.zsf`.

## Boot architecture — current model

Strong working model:

1. internal H1512-family boot code in SPI NOR initializes enough hardware to access microSD;
2. the SF2000-family `LCFG` application image `bios/bisrv.asd` is loaded;
3. the application uses FAT32 resources, emulator data, ROM lists, BIOS files and games;
4. it retains an SF2000-like GPIO-bitbanged RF-controller driver;
5. it also contains an SD-triggered mechanism capable of rewriting internal SPI NOR using `UpdateFirmware/Firmware.upk`.

The exact internal bootloader contents and the XGO-specific board wiring remain to be recovered.
