# Research Log

## 2026-08-30 — Initial forensic pass

- Confirmed tested XGO requires its microSD card to boot.
- Windows Disk Management sees the 32 GB card as a single FAT32 primary partition.
- Inventoried 6,558 filesystem entries.
- Preserved `bios/`, `Resources/`, and filesystem inventory for analysis.
- Identified `bios/bisrv.asd` as an `LCFG` application image.
- Found `SF2000` literal in `Resources/Foldername.ini`.
- Matched XGO resource/database naming conventions to documented SF2000 formats.
- Recovered emulator/core identification strings from `bisrv.asd`.
- Connected controller experiments with product-family documentation calling the mystery port `Handle Interface`.
- Identified `Resources/Test.zsf` as a likely explanation for the previously observed controller diagnostic screen.

## 2026-08-30 — H1512 / RF-driver pass

- Recovered `h1512_gpio_pinmux_sel`, `get_clock_h1512()` and MIPS SDE compiler strings from the XGO firmware.
- Confirmed firmware targets the H1512/MIPS software family; the circulated RK3566 identification is contradicted for this specimen.
- Recovered the shared `UpdateFirmware/Firmware.upk` internal SPI-NOR update path.
- Disassembled a real RF initialization routine near `0x8035deb0` and identified a caller near `0x8034c7ac`.
- Confirmed direct access to the same HC15xx GPIO MMIO words and DATA/CLOCK/CS bit masks used by the SF2000 wireless-controller path.
- Confirmed the XGO performs the stock-style RF self-test: `0x53=0x5a`, `0x53=0xa5`, `0x25=0xa5`, read `0x05`, expect `0xa5`.
- Reclassified generic `usb device attach/detach` strings as mass-storage/filesystem evidence because they occur with LUN and mount-path code; they are not evidence of generic USB HID controller support.
- Confirmed `0xb884c000` accesses belong to SDIO. Known H1512 USB windows are separate (`0xb8844000` and `0xb8850000`).

## Next research targets

- Trace the XGO RF receive/poll routine and locate P1/P2 status/pipe decoding.
- Determine whether the RF IC is physically populated and whether an SF2000/SF900 controller can pair with the XGO.
- Search separately for genuine USB HID/class-3 code and Handle Interface-specific routines.
- Produce a reproducible binary comparison against known SF2000 firmware specimens.
- Inspect MBR, FAT32 reserved sectors, and pre-partition area from a small extract of the preserved raw card image.
- Characterize the Handle Interface electrically/protocol-wise.
- Find photographs/listings/manuals for the original external XGO controller accessory.
- Determine a reproducible way to launch `Test.zsf` and test P2 state.
