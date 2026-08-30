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

Direct firmware evidence identifies the application as MIPS/H1512-family code and strongly ties it to the SF2000 platform. The exact commercial marking/revision of the physical SoC still deserves confirmation from PCB photography or teardown.

A previously circulated RK3566 claim is contradicted by the actual firmware specimen and should not be used for this unit.

## USB capability inherited from the H1512 platform

Current FrogQEMU/HCRTOS reverse engineering documents **two HC15xx USB controller blocks**, USB0 and USB1, that are host/peripheral capable. The DB-B210-V1.1 reference schematic wires a micro-USB connector to USB0 and USB-A to USB1.

This is reference-platform evidence, not an XGO pinout. Still, it materially changes the Handle Interface hypothesis: a micro-USB-shaped controller connector on an H1512 derivative can plausibly be wired to a native USB controller rather than merely using a USB shell for an unrelated serial/GPIO protocol.

The XGO application image has not yet yielded convincing HID-class strings or an obvious direct USB0/USB1 MMIO implementation. Its visible USB strings cluster around filesystem/LUN handling. Therefore the current position is:

- native USB signaling at the Handle Interface is plausible;
- generic USB HID controller support is **not** established;
- a narrow vendor-specific USB controller protocol remains plausible;
- a non-USB protocol over the connector also remains possible until the XGO wiring is traced.

## Transparent-case PCB observation — revised

The transparent enclosure does **not** expose the whole gaming PCB equally well.

The clearest rear photograph shows the wireless-charging coil feeding into a compact lower PCB region dominated by power-electronics features, including a large `2R2` inductor and nearby switching/power components. That region is therefore more likely to be primarily the **power-bank / wireless-charging subsystem** than the main H1512 gaming section.

This matters because the earlier observation of an unpopulated QFN-like footprint in that rear region should **not** be treated as a strong RF candidate. It may belong to the power subsystem. The H1512 and any controller-RF circuitry may instead be on the larger front-side board, much of which is visually obscured by the LCD, button membranes, and enclosure structure.

From the available transparent-case photos:

- no obvious 2.4 GHz antenna is confidently identifiable;
- no populated XN297L-family device is confidently identifiable;
- absence of visible RF hardware in the rear power-board region does **not** rule out RF hardware elsewhere on the main gaming board.

A future straight-on macro view of the front PCB edges around the LCD and the area adjacent to the micro-USB Handle Interface will be more useful than concentrating on the rear power board.

## Important unknowns

The exact RAM configuration, LCD controller/panel, physical RF population, XGO-specific USB/Handle-Interface wiring, GPIO mapping, and external-controller electrical/protocol details are not yet fully established.

## Safety

Do not assume pin compatibility with an SF2000 merely because the firmware and RF software are closely related. The XGO contains a substantially different battery/power subsystem and physical board design.
