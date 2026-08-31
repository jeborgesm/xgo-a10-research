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
- Corrected interpretation of generic USB attach/detach strings: they are strong filesystem/mass-storage evidence but not proof of USB HID support on the Handle Interface.

## 2026-08-30 — Local controller / Handle Interface deep pass

- Confirmed two parallel active-low serial controller data channels in executable MIPS code: B15 and L0, with shared clock B7.
- Confirmed both local channels are scanned periodically and unconditionally.
- Reconstructed the host-driven load phase: firmware drives both data lines low for roughly 4 us, returns them to input, then clocks twelve button positions with roughly 2 us low clock pulses.
- Confirmed twelve-bit order: R, Y, X, L, A, B, SELECT, START, UP, DOWN, LEFT, RIGHT.
- Confirmed local slot 0 OR RF slot 0 -> P1 and local slot 1 OR RF slot 1 -> P2.
- Found no separate application-level P2-present gate or USB-attach gate controlling the local serial scanner.
- Found no convincing controller-side HID class path in the static application analysis.
- Established the strongest hardware interpretation as one local serial channel for built-in P1 and the other for the external Handle Interface/P2, while keeping exact B15/L0-to-connector routing unconfirmed.

## 2026-08-30 — OTG/non-OTG differential experiments

- Empty micro-USB OTG adapter inserted into the powered Handle Interface immediately freezes built-in controls.
- Removing the OTG adapter restores normal controls.
- A normal/non-OTG micro-USB connection does not disturb built-in controls.
- Fine-needle resistance probing of the OTG adapter produced a ground-related reading on micro-USB pin 4, consistent with the conventional OTG ID-to-ground connection. Treat as qualitative rather than precision resistance evidence.
- Through a non-OTG converter, tested three active USB controllers:
  - generic USB SNES-style controller;
  - inexpensive PS-shaped USB gamepad;
  - GP2040-CE.
- None of those controllers was recognized by the XGO.
- None froze or disturbed the XGO built-in controls.
- Therefore the original GP2040 freeze is no longer attributable to GP2040 USB activity itself; the OTG adapter/path is sufficient to trigger it.
- This sharply lowers generic USB HID as an explanation for the Handle Interface.
- The leading physical discriminator is now the micro-USB ID contact: open on non-OTG wiring versus grounded on the OTG adapter.
- Strongest current hypothesis: pin 4 is repurposed or electrically coupled to the external/P2 active-low serial DATA path, so grounding it forces the continuously scanned signal into an asserted state.
- Alternate lower-confidence possibility: pin 4 triggers a lower-level USB/pinmux mode not visible in the reconstructed application-level controller code.

## Current conclusions

- H1512/MIPS SF2000-family lineage is supported by direct executable-code evidence, not only resources/strings.
- The XGO firmware retains the stock SF2000-family wireless-controller protocol path essentially intact, including radio tables, channels, receive behavior and P1/P2 decoding.
- The firmware also implements a distinct two-channel local synchronous controller bus.
- One local channel is a strong candidate for the built-in controls and the second for the external Handle Interface.
- Three generic USB controller implementations fail cleanly through a non-OTG path, while an empty OTG adapter alone freezes controls.
- Generic USB HID is therefore the weakest current Handle Interface model.
- Proprietary synchronous serial over the micro-USB shell is the strongest current model.
- Micro-USB pin 4 / ID is now the highest-value physical signal to map.

## Next research targets

- Establish a reproducible way to launch `Resources/Test.zsf` and observe P1/P2 state while inserting the bare OTG adapter.
- Map Handle Interface contacts to B15/L0/B7 using passive continuity, voltage measurement, or existing logic-analysis equipment if available.
- Determine connector voltage and idle bias before attempting any custom controller interface.
- Investigate whether micro-USB pin 4 is directly connected or coupled to the external serial data line.
- Produce a reproducible binary comparison against known SF2000 firmware specimens.
- Inspect MBR, FAT32 reserved sectors, and pre-partition area from a small extract of the preserved raw card image.
