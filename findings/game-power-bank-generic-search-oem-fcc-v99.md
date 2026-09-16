# Generic “game power bank” search: OEM / FCC / marketplace leads

Date: 2026-09-16
Branch: `research-a10-hardware-lineage`
Status: research lead matrix; comparator evidence only unless explicitly marked

## Search pivot

The strongest search term is not necessarily `XGO`, `A10`, or `DY10`. The product family is routinely described as:

- `10000mAh game power bank`
- `game power bank`
- `power bank game console 2-in-1`
- `magnetic wireless game power bank`
- `游戏机充电宝`
- `游戏机移动电源`
- `磁吸无线充移动电源游戏机`

This follows the physical/manual branding (`Games Power`) and exposes OEM/white-label material hidden by model-name searches.

## Exact-A10 marketplace identifiers recovered

Generic marketplace mirrors preserve at least two Amazon-origin identifiers for the transparent 10000mAh / 15W wireless / 22.5W wired / 10000-games product family:

- ASIN `B0D46LRR32` — mirrored as `Power Bank Game Console 2-in-1, Retro Game Handheld Console, Game Power Bank, Pre-Loaded 10000 Classic Games, Support Wireless Wired Charging`; Ubuy mirror attributes the listing to seller/manufacturer string `KWHEUKJL`; dimensions 5.5 × 2.6 × 0.8 in (approximately 140 × 66 × 20 mm).
- ASIN `B0D476D4PJ` — UK-origin mirror title adds `Transparent Portable Charger`; weight about 270 g.

These are search pivots, not trusted manufacturer identities. `KWHEUKJL` appears to be a generic marketplace brand/seller token used on unrelated products.

## Shenzhen Lechong Technology: important adjacent OEM ecosystem

Alibaba indexing exposes Shenzhen Lechong Technology Co., Ltd. selling multiple `game power bank` / magnetic-wireless handheld products as an OEM/ODM supplier. Its own site says it specializes in wireless chargers, gaming power banks and portable power banks, offers OEM/ODM, and launched a Game Mobile Power series in 2021.

This does **not** establish Lechong as the XGO A10 manufacturer. It does establish a concrete Shenzhen OEM ecosystem producing the same unusual combined product category for white-label export.

### FCC V99 teardown

Lechong certified a `Game Magnetic Wireless Charging Power Bank`, model V99, FCC ID `2A93X-V99`, in 2025. Unlike the unresolved A10 FCC naming collision, the V99 filing has directly accessible internal photographs.

FCC internal-photo attachment ID: `8606454`.

The teardown photographs show:

- a separate black power/wireless PCB and a green game-control PCB;
- wireless charging coil;
- Li-poly cell;
- microSD slot on game PCB;
- display FPC connector;
- D-pad and XYBA contact geometry;
- separate game and power electronics, reinforcing the split-board architecture seen in XGO DY09.

Visible game-PCB silkscreen:

`FX-V99-G16B`
`V2.1 20241010 DFY21`
`T=0.8mm`

Visible power-PCB silkscreen:

`FX-V99-V60`
`241202`

These `FX-*` board identifiers are valuable future search pivots for the board house/design lineage. No indexed independent hit was found in the first pass.

### Why V99 matters but is not A10 evidence

The V99 is a later/different product: its physical layout and battery differ from the A10. It must remain a comparator. Its value is that it demonstrates a current Shenzhen game-power-bank OEM using the same split-board architecture and provides PCB naming conventions that may reveal upstream design/manufacturing relationships.

## Wekome false-positive warning

An Indian Wekome reseller page uses promotional imagery of the exact transparent XGO PLUS+ 10000MAH A10 while its generic text simply calls the item `Gaming Console 15W 10000 mAh Magnetic Wireless Power Bank`.

Do **not** infer that the A10 is a Wekome product from this page. Wekome's actual `WP-29` is a different 110 × 68 × 17 mm, 171 g power bank with decorative game-console styling and no equivalent A10 game hardware. This is useful evidence that reseller images/titles are frequently recycled and that generic category searches can expose exact A10 imagery under unrelated storefront branding.

## Older architecture precedent

The 2020 `3th game` 10000mAh Game Box Power teardown remains a separate predecessor/comparator. It used a two-PCB arrangement, Samsung K5L2731CAA-D770 MCP (128 MB NOR + 32 MB RAM), and LM4890S 1 W audio amplifier. These components must not be attributed to A10 without direct evidence.

The 2022 XGO DY09 teardown is stronger family evidence: it independently establishes XGO use of separate power/wireless and game PCBs and 15W wireless + 22.5W wired charging in this product lineage.

## Next searches

1. Search the exact Amazon ASINs (`B0D46LRR32`, `B0D476D4PJ`) across archived Amazon pages, review mirrors, YouTube, social posts and image caches for user photos or seller identity.
2. Search board strings from FCC V99 (`FX-V99-G16B`, `FX-V99-V60`, `DFY21`) and progressively reduce them (`FX-V99`, `FX-*`) to identify the board designer/factory naming convention.
3. Search Alibaba/1688/Made-in-China suppliers for the exact A10 physical fingerprint rather than model name; record supplier company names and historical product dates.
4. Search Chinese repair/damaged-sale terms around `游戏机充电宝`, `游戏机移动电源`, `磁吸游戏充电宝`, adding `拆机`, `维修`, `主板`, `不开机`, `换屏`, `喇叭`, and `功放`.
5. Search marketplace customer images and second-hand listings for exposed PCBs and screen-ribbon/silkscreen markings.
6. Continue FCC attachment recovery for the separate `2AUZ9-A10` lead; only visual match can establish relevance.
