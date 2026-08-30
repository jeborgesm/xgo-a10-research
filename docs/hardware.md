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

## Important unknowns

The exact SoC, RAM configuration, USB controller implementation, GPIO mapping, LCD controller/panel, and external-controller electrical/protocol details have **not** yet been established for the tested XGO unit.

An online claim that an XGO A10 uses RK3566 exists, but it is disputed and conflicts with the very strong SF2000 software lineage. Do not record RK3566 as established hardware without direct board/chip evidence.

## Safety

Do not assume pin compatibility with an SF2000 merely because the firmware format is related. The XGO contains a substantially different battery/power subsystem and physical board design.
