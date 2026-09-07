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
| OS | Linux | Handhelds Wiki family entry; consistent with our firmware archaeology |

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

During this pass the research environment could inspect and cite remote product images but could not obtain their binary bytes for a GitHub image commit. The direct source URLs above are preserved so the images can be archived byte-for-byte once retrieved or supplied locally.

