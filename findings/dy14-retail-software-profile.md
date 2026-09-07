# DY14 retail/software profile as an H1512 family comparator

Date: 2026-09-07

## New retail-level evidence

Independent retail/manual sources for DY14 consistently describe a **game-power-bank** with:

- 3.5-inch 320x240 display;
- 10,000mAh-class power-bank marketing;
- 32GB TF/microSD bundle in at least some listings;
- AV output;
- dual external gamepad/handle support;
- 10 emulator categories;
- user-downloadable/saveable games.

Examples:
- Manuals+: DY14 Game Power Bank
- Jakmall/Lobajet DY14 listing
- Blibli DY14 listing
- Joom DY14 listing

These marketing sources are noisy on physical dimensions/capacity and should not override Steward Fu's measured/spec page for the examined unit.

## Emulator-family overlap with A10

DY14 retail material repeatedly advertises:

- FC / NES
- MD / Mega Drive
- MAME / Arcade
- GBA
- GBC
- GB
- SFC / SNES
- CPS1
- CPS2
- NEOGEO

That is extremely close to the exact A10 listing's ten-family presentation:

- SFC
- FC
- MD
- GB
- GBC
- GBA
- CPS1
- CPS2
- NEO
- MORE+/Arcade-family content

This overlap is not enough to prove identical firmware, but together with the verified H1512 platform evidence it makes DY14 a high-value **software-family comparator**, not merely a hardware comparator.

## Stock-card evidence

At least one DY14 listing explicitly includes a **32GB Micro SD Game Card**.

This means the same research strategy used for SF2000/DY19/E2 should apply:

1. recover a stock DY14 TF-card image or card-file archive;
2. extract `bios/`, `Resources/`, root metadata and game-list files;
3. compare against A10/DY19/SF2000/GB300;
4. ignore bulk ROM payload unless needed to understand list records.

## Important discrepancy: retail variants vs Steward Fu specimen

Steward Fu documents the examined DY14 as:

- H1512 800MHz;
- 128MB RAM;
- 512KB flash;
- 3.5-inch 320x240;
- 3.7V 8000mA;
- 142 x 95 x 28 mm.

Retail listings commonly advertise:

- 10000mAh;
- approximately 135-160 mm x 85-88 mm x 15-25 mm;
- 32GB card;
- 10,000+ games.

This discrepancy likely reflects **marketing rounding, enclosure/battery revisions, or multiple DY14 batches under one model name**. Therefore:

- use Steward Fu for the actual teardown specimen;
- use retail listings for feature/bundle context;
- do not assume every DY14 sold online has the exact same battery or board revision.

## Why this matters to A10 archaeology

DY14 now gives us three independent layers of comparison:

1. **SoC/SDK layer:** H1512 + `h1512_gpio_pinmux_sel`.
2. **hardware layer:** archived teardown with RAM/SPI/power/audio components.
3. **product/software layer:** TF storage, AV, external controllers and near-identical emulator-family marketing.

That makes DY14 one of the strongest available sibling references for determining which parts of the A10 are:
- generic H1512 platform behavior;
- board-specific adaptation;
- Xinguo-only product integration.

## Recovery status

No public DY14 full TF-card image or `bisrv.asd` archive was located in this pass.

The public Steward Fu repository contains:
- specification;
- teardown;
- screen investigation;
- SPI dump procedure;

but not a stock card image.

That remains a high-priority recovery target.
