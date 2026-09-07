# Xinguo / XGO handheld family platform map

Date: 2026-09-07

## Why this matters

The Xinguo / 芯果 product line does not appear to be one continuous firmware family. Current evidence instead shows Xinguo repeatedly combining its own retail/product identity with several different low-cost game-console platforms.

This is useful for A10 archaeology because it means sibling XGO devices can still provide:
- enclosure and product-line lineage;
- charging/power-board reuse clues;
- controller and UI conventions;
- evidence of what commodity platform Xinguo adopted in each generation.

But software similarity must be proven per-platform, not assumed from the XGO badge.

## Product/platform map

### DY09 — fixed NES/Famicom-class architecture

- 5000mAh magnetic game/power-bank
- 500-in-1
- separate power and game PCBs
- bonded/COB game processor
- Spansion S29GL128N 128-Mbit (16 MiB) parallel NOR
- 21.47727-MHz Famicom/NES-class master clock
- no public firmware/ROM dump located yet

Interpretation: simple NOAC/Famiclone-style product; product-line ancestor, not A10 firmware ancestor.

### A10 — HC15xx / SF2000-derived multi-emulator architecture

Our specimen:
- 10000mAh / 37Wh class power-bank product
- TF-based game storage
- Linux/software-emulator runtime
- SF2000/GB300/DY19-family firmware lineage established independently in this repository
- multiple filesystem-based emulator families and external-core work

Interpretation: major architectural jump from DY09.

### R350 — Xinguo-branded VT569B Linux handheld

Chinese retail catalogs explicitly sell **芯果 R350** with 8/64/128G options, thousands of games and 12 emulator families.

Independent handheld-family documentation identifies R350 as using the same **VT569B Cortex-A7** platform as the SZDiiER D-R35 Plus.

The D-R35 Plus is documented as Linux/VT569B and has:
- known teardown/PCB photography in the community;
- stock firmware references;
- a stock menu folder publicly preserved.

This makes R350 a high-value comparative target even though it is not HC15xx.

Research opportunity:
1. obtain an Xinguo R350 card image or stock firmware;
2. compare filesystem/menu resources to D-R35 Plus;
3. determine whether Xinguo merely reskins the VT569B reference platform;
4. compare Xinguo UI/resource conventions against A10.

### L35 — Xinguo-branded RK3326 / EmuELEC-class handheld

Chinese retail catalogs explicitly sell **芯果 L35**.

Independent documentation and a Chinese Xinguo L35 review identify:
- Rockchip RK3326
- 1GB RAM class
- 3.5-inch 640x480
- Linux
- EmuELEC / ArkOS-class software
- dual microSD on commonly sold variants
- 3000mAh battery

Handhelds Wiki already lists **internal images** for L35.

Interpretation: another Xinguo product built around a commodity community-supported platform, again different from A10.

## Strong new conclusion

Xinguo's modern game products span at least three distinct compute architectures:

1. DY09: Famiclone/NOAC + parallel NOR
2. A10: HC15xx/MIPS SF2000-family software platform
3. R350: VT569B Cortex-A7 Linux platform
4. L35: RK3326 Cortex-A35 Linux/EmuELEC platform

Therefore the most useful "ancestor" search is not a simple model-number timeline. We should instead search for:
- Xinguo devices using the **same board/SoC platform** as A10;
- Xinguo reskins of known OEM reference handhelds;
- OEM siblings whose firmware predates or matches the A10 resource layout.

## Gold targets

### Target A — Xinguo R350 hardware / firmware

High value because a sibling VT569B device, D-R35 Plus, already exposes both PCB photography and stock firmware references. If Xinguo R350 is a reskin, we can learn how Xinguo modifies a commodity firmware family.

### Target B — Xinguo L35 internals

High value because actual internal images are publicly indexed and the base RK3326/EmuELEC ecosystem is well documented. This can reveal whether Xinguo uses stock OEM boards unchanged.

### Target C — older Xinguo "game power bank" models

Known examples now include DY05, DY09 and first-generation 10000mAh/299-game products. These may expose recurring power-board or enclosure engineering even when the game compute subsystem differs.

### Target D — MINILOONG Pocket 1

A 2025 design patent filed by Shenzhen Qianhai Xinguo Intelligent Technology identifies a product named **MINILOONG Pocket 1**. This is direct manufacturer evidence of another handheld design and is worth tracing for retail identity, SoC, firmware and PCB photos.

## Evidence discipline

Do not equate:
- same brand with same firmware;
- same enclosure with same PCB;
- same emulator count with same SoC;
- retailer SoC claims with verified silicon.

Xinguo's R350/L35 presence actually demonstrates why board-level and firmware-level proof are required.

## Public sources

- Xinguo JD brand/catalog pages for R350/L35/A10/DY09
- Handhelds Wiki L35 and D-R35 Plus pages
- Retro Dock D-R35 Plus page
- Chinese Bilibili/YouTube Xinguo L35 review
- ChargerLAB DY09 teardown
- CN309839051S MINILOONG Pocket 1 design patent
