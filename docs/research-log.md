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
- Recovered explicit Player 2 and USB attach/detach strings.
- Connected earlier controller experiments with product-family documentation calling the mystery port `Handle Interface`.
- Identified `Resources/Test.zsf` as a likely explanation for the previously observed controller diagnostic screen.
- Located active open-source SF2000-family work (particularly UniFrog) as a potential reference architecture for an eventual XGO-specific target.

## 2026-08-30 — H1512/RF deep pass

- Confirmed `h1512_gpio_pinmux_sel` and MIPS SDE compiler/SDK strings in the XGO firmware.
- Identified the shared SF2000-style `UpdateFirmware/Firmware.upk` internal SPI-NOR update path.
- Disassembled the XGO RF routines as little-endian MIPS.
- Confirmed the stock-style H1512 GPIO-bitbang RF bus at `0xb8800050/+54/+58/+354/+358` with DATA/CLOCK/CS masks `0x08000000`, `0x10000000`, and `0x20000000`.
- Confirmed the RF self-test sequence `0x53=0x5a`, `0x53=0xa5`, `0x25=0xa5`, read `0x05`, expect `0xa5`.
- Confirmed RF packet receive from status register `0x07` and two-byte payload register `0x61`.
- Confirmed status bit `0x02` selects one of two controller slots, matching SF2000 P1=`0x40`, P2=`0x42` behavior.
- Found exact stock SF2000 RF configuration/address tables in the XGO image:
  - `0a 6d 67 9c 46`
  - `f6 37 5d`
  - `dc a8 f3 6b 74`
  - `b2 9d 59 4f e3`
- Found the exact stock four-channel sequence `04 1d 31 4f`.
- Reviewed the transparent-case PCB photo. No obvious antenna or populated radio is identifiable at current resolution, while one small unpopulated QFN-like footprint is visible. Because XN297L exists as QFN20 3x3 mm, this is a useful future inspection target but is not yet an IC identification.
- Corrected interpretation of generic USB attach/detach strings: they are strong filesystem/mass-storage evidence but not proof of USB HID support on the Handle Interface.

## Current conclusions

- H1512/MIPS SF2000-family lineage is now supported by direct executable-code evidence, not only resources/strings.
- The XGO firmware retains the stock SF2000-family wireless-controller protocol path essentially intact, including radio tables, channels, receive behavior and P1/P2 decoding.
- Whether the RF hardware is actually populated remains an independent physical question.
- If radio hardware is present, stock-compatible SF2000/SF900 controllers are strong candidates for direct compatibility.
- The wired Handle Interface remains unresolved and should now be treated as a separate input path rather than assuming it implements the confirmed RF protocol.

## Next research targets

- Trace the wired Handle Interface independently: look for distinct polling, USB class/HID, UART, or GPIO-style input paths.
- Compare the visible unpopulated PCB footprint and neighboring components with XN297L-family reference layouts when sharper board images are available.
- Produce a reproducible binary comparison against known SF2000 firmware specimens.
- Inspect MBR, FAT32 reserved sectors, and pre-partition area from a small extract of the preserved raw card image.
- Determine a reproducible way to launch `Test.zsf` and test P2 state.
