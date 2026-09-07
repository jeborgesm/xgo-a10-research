# DY19 hardware-lineage marketplace sweep

Date: 2026-09-07

## New lineage evidence

A current JD marketplace index exposes a particularly useful family listing whose title groups **DY12, DY14 and DY19** together as arcade-game-console / power-bank products:

`DY12DY14DY19街机游戏机充电宝游戏机移动电源GAMEPOWEBANK`

The same indexed listing exposes variants including DY12 and DY14. This is stronger commercial-family evidence than isolated reseller keyword overlap: these model numbers are being sold within one product family/variation context.

A current Ruten index independently exposes controller/accessory compatibility across the same family:

`DY13DY17時光遊戲機配件手柄DY12DY19六鍵搖杆雙人Micro安卓口`

This groups DY13, DY17, DY12 and DY19 around a six-button / two-player Micro-USB controller accessory. It suggests that at least part of the external controller interface was intentionally shared across several DY-family products.

Ruten also indexes a **DY-19 second-generation/upgraded** product (`DY-19二代升級...`). This is important when interpreting photographs or firmware: not every device sold as DY19 should be assumed to have one PCB revision.

## Replacement-parts evidence

Shopee Malaysia currently indexes a listing explicitly titled `DY19配件` (DY19 accessories) with 12 product images and three variations. Another Shopee seller indexes a DY19-compatible/parts product. These are promising image-recovery targets because accessory sellers may expose controller, shell, display, cable or board-level components not shown by ordinary retail listings.

No indexed text yet proves that any of those 12 images is a bare mainboard. Preserve that distinction until the actual image bytes can be inspected.

## Firmware-modder trail

Bilibili's DY-19 recovery video by `Sesn` explicitly says another uploader, `炒鸡大帅比9961`, created an optimized DY19 firmware package. Searches confirm that this uploader remains indexed on Bilibili, but the current public search index does not expose the DY19 optimization video itself. The identity remains a high-value recovery lead.

## Teardown search status

Chinese and English image searches for DY19 mainboard/teardown terms still do not yield a provenance-safe internal PCB image. Do not ingest visually similar generic power-bank/game-console boards as DY19.

## Interpretation for XGO archaeology

The marketplace evidence strengthens a working model of a broader DY hardware/product family rather than isolated look-alike products:

- DY12 / DY14 / DY19 appear together in a commercial GAMEPOWEBANK family listing;
- DY12 / DY13 / DY17 / DY19 share at least a marketed controller/accessory interface;
- DY19 has an indexed second-generation/upgraded variant;
- therefore PCB and firmware comparisons must track exact model/revision and should not assume all DY19 photographs are identical internally.

This makes authenticated DY14/DY12/DY17 teardowns potentially useful as *comparators*, while DY19-specific teardown evidence remains the target needed for direct hardware correlation with the recovered DY19 firmware.

## Sources

- JD family index: https://www.jd.com/jiage/6728f3c282b30bc793e5.html
- Ruten DY19 search index: https://www.ruten.com.tw/find/?q=dy19
- Shopee DY19 accessories listing: https://shopee.com.my/%E3%80%90DY19%E9%85%8D%E4%BB%B6%E3%80%91%E6%8E%8C%E4%B8%8A%E6%B8%B8%E6%88%8F%E6%9C%BA%E5%85%85%E7%94%B5%E5%AE%9D%E4%BA%8C%E5%90%88%E4%B8%80%E4%BE%BF%E6%90%BA%E5%BC%8F%E8%87%AA%E5%B8%A6%E7%BA%BF%E7%A7%BB%E5%8A%A8%E7%94%B5%E6%BA%90%E6%B8%B8%E6%88%8F%E6%9C%BA3.21%E3%80%90DY19-Accessories%E3%80%91Portable-Game-Console-Power-Bank-2-in-1-with-Built-in-Cable-Mobile-Power-Supply-Game-Console-3.2-i.1770977679.43779403260
- Bilibili recovery video: https://www.bilibili.com/video/BV1Td8ceJEA8/


## Stronger firmware-revision evidence: DY12 MY2024

A retrospective SBCGaming DY19/DY12 owner thread contains an unusually important revision report.

One owner reports a DY12 "version without D-Pad" that would boot SF2000 vanilla firmware but had no working buttons, and whose original `bisrv.asd` could not simply be substituted into SF2000 firmware.

A follow-up then reports:

`DY12 MY2024 is the same as DY19, so multicore BIOS from DY19 works on my DY12`.

This is stronger than marketplace-family naming. It indicates that **DY12 itself changed architecture across revisions**, and that a MY2024 DY12 revision crossed into the DY19 firmware-compatibility branch.

Source:
https://www.reddit.com/r/SBCGaming/comments/1bf6vzv/

### Consequence

Do not model the lineage as a simple model-number progression:

`DY12 -> DY13 -> DY14 -> DY17 -> DY19`

A better working model is a **revision graph**, where a later DY12 can be firmware-closer to DY19 than to an earlier DY12.

This also explains why community claims such as "DY12 is the same as SF2000" can be simultaneously directionally useful and technically false for a particular unit.

## DY17 evidence

Multiple current reseller mirrors consistently identify DY17 as:

- 10000 mAh game-console power bank;
- 500 built-in games;
- TV output through a dedicated AV interface;
- external controller / two-player support;
- Simplified Chinese + English;
- multiple appearance/color batches.

At least one listing explicitly warns that appearance, color and printed text can vary by batch.

This makes DY17 a useful **physical/product-family comparator**, but current indexed evidence does not establish the H1512/multicore firmware relationship that we have for DY19 and some DY12 revisions.

## DY13 evidence

A current manufacturer listing from Guangzhou Sundi Electronics identifies DY13 as a 2.8-inch, 10000 mAh, 500+ game power-bank handheld, 135 x 88 x 25 mm. This establishes DY13 as a genuine commercial model in the same unusual console/power-bank product class, but no current evidence ties its firmware directly to H1512.

## DY14 rated-capacity clue

Independent DY14 reseller documentation lists both:

- advertised battery capacity: **10000 mAh / 37 Wh**
- **rated capacity: 4000 mAh**

This is important when comparing the ~4000 mAh figure reported from XENON's opened DY19. A reseller's lower "rated capacity" can describe usable output capacity after voltage conversion rather than the physical cell's nominal 3.7-V capacity. Therefore XENON's wording and any eventual battery-label photograph must be checked carefully before concluding that the DY19's advertised cell capacity is fraudulent.

The DY14 documentation also independently reproduces the same ten-emulator family:
NES/FC, MD, MAME, GBA, GBC, GB, SFC, CPS1, CPS2, NEOGEO.

## Revised hardware-archaeology model

Current evidence supports three overlapping layers:

1. **Product lineage** — DY12/DY13/DY14/DY17/DY19 share console/power-bank concepts and accessories.
2. **Firmware lineage** — SF2000-related early DY12, later DY12 MY2024/DY19 compatibility, direct recovered DY19 H1512 application, and XGO's proven DY19-family software ancestry.
3. **Revision lineage** — model labels are not sufficient. DY12 and DY19 both have evidence of materially different batches/revisions.

Future teardown-image matching must therefore capture **model + exterior revision + PCB silkscreen + firmware hash** whenever possible.
