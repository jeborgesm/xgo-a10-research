# Hardware and Ports

## Tested device

Branding: **XGO PLUS+ 10000mAh** / "Power to the Whole New World".

The device combines a retro handheld with a power bank and magnetic wireless charging hardware.

## Externally observed interfaces

| Interface | Current interpretation | Confidence |
| --- | --- | --- |
| microSD / TF | Boot-critical storage, firmware/resources/ROMs | Confirmed |
| USB-C marked IN/OUT | Power-bank charging/output | Strong evidence |
| 3.5 mm jack | Analog A/V output | Strong evidence |
| micro-USB-style connector | External controller / "Handle Interface" | Strong evidence; protocol unknown |
| Rear coil | Magnetic wireless charging | Confirmed by product design/documentation |

The unit also has built-in controls, speakers, display, and power controls.

## SoC/software-platform evidence

Direct firmware evidence now identifies the application as MIPS/H1512-family code and strongly ties it to the SF2000 platform. The exact commercial marking/revision of the physical SoC still deserves confirmation from PCB photography or teardown.

A previously circulated RK3566 claim is contradicted by the actual firmware specimen and should not be used for this unit.

## Transparent-case PCB observation

The user's rear photograph gives a useful partial view of the PCB through the transparent enclosure.

Visible observations:

- no obvious large PCB meander antenna or separate antenna wire can be identified in the photographed region;
- no clearly identifiable populated 2.4 GHz radio IC is visible at the available resolution;
- a **small unpopulated square QFN-like footprint** is visible near the lower-board component cluster;
- the footprint appears plausibly in the size/pad-count class of a small QFN20 device, but the image is not sufficient for a reliable pad-count or net-level identification.

This is interesting because the Panchip XN297L used in SF2000-family wireless-controller work is available in a 3 x 3 mm QFN20 package. **Package compatibility alone is not identification.** The empty footprint could belong to an unrelated IC, and the required crystal/RF matching/antenna network has not been traced from the photograph.

Current hardware hypothesis worth testing later:

> XGO may have retained the complete SF2000 RF controller software while omitting some or all of the RF hardware on this board revision.

The transparent-case photo is consistent with that possibility but does not prove it.

A sharper, straight-on macro photograph of both PCB sides — especially the unpopulated QFN area and any trace leading toward an antenna-shaped structure — could settle much of this without destructive disassembly.

## Important unknowns

The exact RAM configuration, LCD controller/panel, physical RF population, USB/Handle-Interface implementation, GPIO mapping, and external-controller electrical/protocol details are not yet fully established.

## Safety

Do not assume pin compatibility with an SF2000 merely because the firmware and RF software are closely related. The XGO contains a substantially different battery/power subsystem and physical board design.
