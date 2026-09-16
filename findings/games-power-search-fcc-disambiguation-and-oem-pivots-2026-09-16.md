# Games Power search — FCC disambiguation and OEM pivots

Date: 2026-09-16
Branch: `research-a10-hardware-lineage`

## Scope

Continued hardware archaeology using the product-category identity rather than relying on `XGO A10` alone:

- `10000mAh game power bank`
- `Games Power`
- `Power Bank Game Console 2 in 1`
- `game power bank 22.5W 15W 37Wh`
- Chinese `游戏机充电宝`, `游戏充电宝`, `磁吸游戏充电宝` plus teardown/repair/PCB terms
- reseller aliases and regional service channels

## FCC 2AUZ9-A10 status

The FCC lead remains quarantined behind an identity gate. The filing is for East Sky Industry Co., Limited, model A10, described as a magnetic wireless charging power bank. Public exhibit identifiers previously recovered are:

- 7989625 external photographs
- 7989626 internal photographs
- 7989627 user manual

The overlap of `A10` and magnetic power-bank functionality is interesting but insufficient. The Games Power/XGO specimen is unusual enough that a matching enclosure, display/game board, control PCB geometry, or other distinctive physical evidence should be obvious if the FCC photos are actually our product.

Until the photographs are recovered and matched, record this as `candidate naming collision / unresolved` rather than lineage evidence.

## OEM/manufacturing search direction

Generic game-power-bank searches continue to expose manufacturers and product families where the game subsystem and charging/wireless subsystem are physically separate boards. This architecture is now established as a recurring design pattern in the product category and in older XGO-family material, but it is not sufficient to identify the A10 board designer.

The useful next-level fingerprints are therefore:

1. PCB silkscreen prefixes and revision/date strings.
2. Display FPC markings and dimensions.
3. Charging-board layout around the large inductor and USB-C interface.
4. Game-board microSD/display/control connector placement.
5. Processor package style (including bonded/epoxy-covered implementations).
6. Speaker/amplifier path and board-to-board power/audio wiring.

## Marketplace archaeology

Search engines continue to recover the exact physical product under aliases that omit XGO. This supports a marketplace-asset strategy:

- old Banggood/affiliate mirrors
- Amazon ASIN mirrors
- regional sellers
- customer Q&A
- broken/used/parts-only listings
- cached review images
- repair/service listings

The most valuable artifact is no longer another intact-product photograph. Priority is any image showing the enclosure open, TF card removed, display ribbon exposed, PCB markings, charging board, or a repair diagnosis.

## Firmware-community archaeology

Expanded generic-name searches combined with known firmware fingerprints (`bisrv.asd`, `Archive.sys`, `KeyMapInfo.kmp`, WQW) still have not exposed an independent indexed A10 firmware project.

This strengthens the case for person/community-first searching: follow SF2000/GB300 researchers, old GitHub issues, Discord references, gists, forks, Telegram mirrors, and comments rather than expecting an A10-named repository.

## Current evidence threshold

Do not promote any candidate to exact A10 hardware identity unless at least one of the following is obtained:

- unmistakably matching internal/external photographs;
- readable PCB silkscreen from an exact enclosure;
- exact stock TF-card/firmware archive independently sourced from a matching device;
- manufacturer/service documentation tying a board identifier to the Games Power/A10 enclosure.

## Next pivots

- keep attacking FCC exhibit recovery by document ID and alternate storage/cache routes;
- search generic Games Power product imagery for open/broken units;
- search Chinese second-hand/repair vocabulary, especially motherboard and no-power faults;
- search MechZone/SMARTBERRY and other regional aliases for service material and user photos;
- pivot through SF2000-family researcher handles and historical community references;
- preserve all exact board/FPC/firmware identifiers found, even when their product identity is initially unknown.
