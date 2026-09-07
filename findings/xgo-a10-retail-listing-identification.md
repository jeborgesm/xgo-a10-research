# XGO A10 retail/listing identification and external visual evidence

Date: 2026-09-07  
Branch: `research-game-list-scanning`

## Bottom line

The physical specimen under investigation is strongly identified as the **Xinguo / 芯果 XGO A10**, a 10,000 mAh game-console/power-bank hybrid sold under the visible front marking:

`XGO PLUS+ 10000MAH`

This is not just a generic resemblance. The user-supplied specimen and multiple independent retail images share the same unusual enclosure geometry, transparent PCB-pattern shell, joystick/Start/Select cluster, six-button face cluster, screen placement, edge-port layout, and rear wireless-charging coil.

## Exact current AliExpress listing supplied by the owner

Listing title:

`NEW Game Console Power Bank Integrated 10000mAh Fast Charging Magnetic Wireless Charging Mobile Power Supply Handheld Player`

AliExpress item URL / item id:

`https://www.aliexpress.us/item/3256811871013165.html`

The AliExpress page currently redirects automated retrieval through an account/cookie gate, so the listing's own image bytes could not be archived directly from the research environment during this pass. The same product photography and specification artwork is mirrored by other retailers and reference sites listed below.

## Model identity

### Strong evidence: A10

Multiple Chinese retail results explicitly call the black 10,000 mAh / 10,000-game variant:

`A10 black [10000mAh + ten-thousand games + magnetic power bank]`

A Manuals+ retailer-derived manual also identifies the device as **Xinguo XGO A10**.

### Related name: DY10

A separate Handhelds Wiki page and older retail material use **DY10** for an XGO 10,000 mAh gaming power-bank product family. Retail material also calls the transparent XGO magnetic gaming power bank the "DY10 game magnetic power bank."

Current evidence therefore supports:

- **A10** = best match for this exact black 10,000 mAh specimen;
- **DY10** = related/earlier retail-family name that should not be substituted for A10 without package/PCB confirmation.

## Manufacturer / brand

Chinese brand name: **芯果** (Xinguo / XGO).

A Chinese market-regulator record identifies an earlier XGO game-console power bank, model DY-01, as a product of:

**深圳市前海芯果智能科技有限公司**  
(Shenzhen Qianhai Xinguo Intelligent Technology Co., Ltd.)

A 2025 Chinese design-patent filing for another handheld product likewise lists the same company as applicant, strongly tying the XGO/芯果 handheld brand to this manufacturer.

This is manufacturer-family evidence; it does not by itself prove that the A10 PCB was fabricated in-house rather than by an OEM/ODM partner.

## Retail / published specifications

Published A10 specification material reports:

| Property | Published value | Evidence status |
|---|---:|---|
| Model | A10 | strong retail/reference evidence |
| Nominal battery capacity | 10,000 mAh | corroborated by enclosure marking and listings |
| Rated capacity | 5,800 mAh / 37 Wh | published specification; important distinction from nominal cell capacity |
| Wired fast charge | up to 22.5 W | repeated across retail artwork/listings |
| Wireless magnetic charge | up to 15 W | repeated across retail artwork/listings |
| Input | USB-C 5V=3.1A, 9V=2.22A, 12V=1.67A | published A10 spec |
| Output | USB-C 5V=2A, 9V=2.22A, 12V=1.67A | published A10 spec |
| Dimensions | 141 x 67 x 20 mm | published A10 spec |
| Advertised game count | up to 10,000 | retail/package-dependent |
| Advertised emulator families | ARCADE, FC, GB, GBA, GBC, MD, SFC, others | corroborates firmware/card archaeology, but retail list is not authoritative |
| OS | Retail/community listings often label it Linux | **incorrect as an implementation description**: firmware archaeology identifies the H1512/ALi TDS2 stack, not Linux |

## Physical-layout match to our specimen

The external retail photos materially strengthen several already-known physical observations:

1. **Landscape gaming orientation.** The long 141 x 67 mm body is intended to be held horizontally: joystick + Start/Select on the left, six face buttons on the right, display centered.
2. **Transparent/cyberpunk shell is factory design.** The circuit-board pattern visible on the user's specimen is present in retail product photography, so it is not a one-off replacement shell.
3. **Rear wireless charging assembly is intentional product architecture.** Retail imagery presents magnetic wireless charging as a headline feature; our own rear photo independently shows the large copper charging coil and separate power circuitry.
4. **Bottom/edge port geometry matches the product renders.** The product art shows the same slim edge construction and port/button placement seen in our enclosure photos.
5. **The front marking is a model-family clue.** Retail images and our specimen both show `XGO PLUS+ 10000MAH`.

## Important battery interpretation

The advertised **10,000 mAh** figure is a nominal battery/cell-capacity marketing number. The published **5,800 mAh / 37 Wh rated capacity** is the more relevant usable-output rating for power-bank behavior.

37 Wh is also internally plausible for a nominal 10 Ah single-cell lithium pack around 3.7 V:

`10 Ah x 3.7 V ≈ 37 Wh`

So the 37 Wh figure is consistent with the physical battery architecture rather than contradictory. The 5,800 mAh rated output reflects conversion/output-rating conventions rather than a claim that the internal cell is only 5,800 mAh.

## External visual references located

### Product render — exact enclosure / control layout

Wekome India mirrors a high-resolution factory render of the transparent black XGO PLUS+ 10000MAH device:

`https://wekome.in/cdn/shop/files/O1CN01q7ezfT1Qk0AL2P3zU__2209861332013-0-cib_800x900_303e971e-3ad8-410e-8fd1-ea02a3c07d93.jpg?v=1721125585`

Observable value:
- exact shell/control arrangement;
- XGO PLUS+ marking;
- landscape orientation;
- edge profile.

### Charging/capacity marketing artwork

A mirrored marketplace image states 22.5W wired, 15W wireless magnetic, 10000mAh:

`https://i.ebayimg.com/images/g/oUUAAOSwJ9tmRbLO/s-l960.jpg`

Observable value:
- published power claims;
- exact enclosure match;
- port/control rendering.

### A10 dimensions/specification artwork

Handhelds Wiki indexes factory-style A10 specification art showing:
- model A10;
- 141 x 67 x 20 mm;
- 10000mAh;
- rated 5800mAh / 37Wh;
- max 15W wireless charging.

Reference page:
`https://handhelds.wiki/XGO_A10_Power_Bank_and_Game_Console`

### Independent A10 manual/reference

`https://manuals.plus/ae/1005008975396605`

Useful because it explicitly labels the unit Xinguo XGO A10 and publishes the power-bank and dimensions table.

### Chinese retail corroboration

JD search/catalog results repeatedly identify the black variant as:

`A10 black [10000mAh + ten-thousand games + magnetic power bank]`

and separately list the green 5000mAh sibling as DY09, helping distinguish the A10 10,000mAh model from the lower-capacity product.

## Relationship to our existing 39-photo corpus

The user's current physical-device photographs already preserved in `images/inbox/` are more valuable than retailer renders for physical proof. The external images should therefore be classified as **reference/context** and used to identify model/marketing lineage, while the user's own photographs remain the primary hardware evidence.

Several of the photographs supplied again on 2026-09-07 correspond directly to already-cataloged evidence:
- clean front/enclosure view;
- rear copper wireless-charging coil;
- bottom USB-C / TF / speaker edge;
- opposite edge with AV-marked jack;
- side controls;
- test-bench/controller views.

Do not duplicate those photographs under new filenames unless a materially higher-resolution source is supplied.

## Archival action / next step

Create `images/external/` for retail/reference images rather than mixing them into `images/inbox/`.

The original automated retrieval could not obtain the AliExpress image bytes. The owner subsequently supplied the exact listing images directly in the research session; see the update below.



## 2026-09-07 image-corpus and teardown-search update

### Exact A10 AliExpress image corpus captured in the research session

The owner manually captured and supplied **21 images from the exact AliExpress A10 listing** (item 3256811871013165). The source image files are present in the research session and were SHA-256 hashed before archival work.

The set includes: clean front/product views; the A10 141 x 67 x 20 mm specification card; 10000mAh/22.5W marketing art; advertised emulator matrix; exposed rear wireless coil/power-board render; wireless-charging examples; joystick/button details; USB-C/TF/speaker close-up; complete function-key/port diagram; alternate 14.2 x 6.6 x 2.5 cm dimension art; package contents; and a near-orthographic multi-side plus rear-internal view.

Marketing labels and composited internal renders remain retail claims until corroborated against the physical specimen.

### Advertised emulator matrix

The exact-A10 artwork explicitly labels SFC, FC, MD, GB, GBC, GBA, CPS1, CPS2, NEO and MORE+. This corroborates the firmware/game-list archaeology but is not authoritative proof of implementation or compatibility.

### Exact A10 controls and ports

The listing diagram identifies/depicts the directional joystick, Select, Start, simultaneous Start+Select return behavior, six face/function buttons, volume +/-, on/off, mobile-power switch, USB Type-C, TF card, loudspeaker, AV connection and a separately labeled handle/controller interface. This closely matches the physical specimen.

### Packaging evidence

The listing depicts console x1, user manual x1, TF card x1 (illustrated as 32 GB), charging cable x1 and retail box x1. Treat card capacity as bundle-specific until independently verified.

## DY09 teardown: corrected classification

A ChargerLAB / 充电头网 teardown at https://www.chongdiantou.com/archives/160933.html was investigated. It is **NOT an A10 teardown**. It documents a visibly different Xinguo/芯果 **DY09 5000mAh** magnetic wireless-charging game/power-bank. Three teardown photographs were captured for comparative manufacturer-family evidence.

No DY09 component identification may be projected onto the A10 without independent A10 evidence. Findings involving IP5356, IP6829, XB7608, S29GL128N, the 21.47727-MHz crystal, COB/bonded game processor or DY09 board architecture are **DY09-only facts**.

## Search for a public teardown of the exact A10

Targeted English and Chinese searches used XGO A10 / 芯果 A10, 拆解 / 拆机, PCB/mainboard/motherboard, 10000mAh, Games Power and exact-enclosure imagery.

**Current result: no verified public teardown of the exact XGO A10 was located.** ChargerLAB material found for Xinguo is the DY09 rather than A10. Exact-A10 material located elsewhere is retail/reference imagery, manuals/listing mirrors and videos rather than a documented PCB-level disassembly.

This negative result is important: do not cite the DY09 teardown as documentation of A10 internals.

## Future controlled A10 hardware archaeology

If deeper inspection is eventually undertaken on the working development specimen: photograph every stage before moving parts; record screw/cable/ribbon orientation; photograph both PCB sides; capture silkscreens/revisions and readable IC/crystal markings; capture battery/LCD markings; avoid destructive adhesive/bonded-assembly removal unless justified; then reassemble and verify the golden runtime.

Until then, software archaeology and the owner's physical A10 photographs remain authoritative for A10 internals.


## OS classification correction — 2026-09-07

Earlier retail/reference material was recorded as calling A10 "Linux." That label is now explicitly rejected as a technical description of the preserved specimen.

The A10 application binary and the wider H1512/SF2000 reverse-engineering record identify the platform as an **ALi TDS2 / H1512 MIPS embedded stack**. Repository symbol work includes TDS scheduler/OSAL functions, and the application image carries the same H1512 SDK/compiler lineage as SF2000. Community SF2000 documentation likewise identifies official firmware as ALi TDS2 and states that Linux is not the stock operating environment on this processor family.

Treat "Linux" on Handhelds Wiki/retail pages as catalog metadata, not firmware evidence.
