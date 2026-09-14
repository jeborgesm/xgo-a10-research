# A10 mainland OEM candidate pass — 2026-09-13

Status: active archaeology support note. The authoritative lineage conclusions remain in `findings/hardware-firmware-lineage-matrix.md`.

## Scope

This pass resumed mainland-China/OEM research with the **physical specimen's confirmed `Model number: A10`** as the primary identity. It deliberately did not restart DY19/DY12/Q19 sibling archaeology.

Exact discriminator retained throughout:

- XGO PLUS+ transparent landscape enclosure;
- model A10;
- 10000mAh nominal;
- 5800mAh / 37Wh rated;
- 22.5W wired;
- 15W magnetic wireless;
- 67 × 141 × 20 mm;
- left joystick + Select/Start + six face buttons;
- TF / TV-output / external-controller product family.

Specification similarity alone is not accepted as lineage evidence.

## Rejected 32G false lead — CONFIRMED NOT A10

A Chinese-market-style Ruten/Alibaba-derived listing initially appeared promising because a variant explicitly read approximately:

```text
32G单人粉 - 10000毫安 + 万款游戏
```

Image-level inspection rejected it as A10 evidence:

- the physical enclosure differs from the exact XGO PLUS+/A10 shell;
- the product uses built-in charging leads absent from our specimen;
- certification/product artwork identifies the device as **DY-19**;
- upstream Alibaba artwork belongs to image-owner namespace:

```text
2200580559675
```

Conclusion: **REJECT as A10 card-capacity or hardware evidence.**

This is an important control result: `32G + 10000mAh + 10000 games` is not sufficiently discriminating without exact enclosure/model evidence.

## Guangzhou Qili Electronics — CANDIDATE ONLY / NOT PROVEN

Made-in-China currently indexes:

```text
Game Console Power Bank 10000mAh 22.5W Fast Charging Magnetic Wireless Charging
Guangzhou Qili Electronics Co., Ltd.
```

Useful attributes:

- 10000mAh game-console/power-bank product class;
- 15W / 22.5W output fields;
- Guangzhou China supplier;
- OEM/ODM and private-label claims;
- listing date indexed as 2024-10-19.

However the page contains obvious generic/contradictory catalog metadata:

- `Model NO. 1`;
- `Screen Size 4.3"`;
- `Function: Power Bank with Strong Light Flashlight`;
- company profile identifies the business as a broad consumer-electronics **Trading Company** while marketing copy also claims factory-direct production.

The product image is hosted at Made-in-China under asset token:

```text
mQTeKAqypwbi
```

but the image CDN could not be retrieved during this pass. Therefore the physical enclosure could not be compared.

Conclusion: **do not identify Guangzhou Qili as an A10 OEM/supplier unless the listing image or another independent source proves the exact XGO enclosure or card/PCB relationship.**

## Shenzhen Lechong Technology — CANDIDATE ONLY / IMAGE PENDING

China wholesale indexing exposes a second source:

```text
Shenzhen Lechong Technology Co., Ltd.
Trending products 2025 new arrivals Handheld Game Console Power Bank 10,000 Mah
New year Gift PD 22.5W 10000mAh Portable Charger Built-in Handheld Game Console ...
```

Lechong's own site describes the company as an OEM/ODM portable-power manufacturer and states that a `Game Mobile Power` product series launched in 2021.

This makes Lechong organizationally plausible as a white-label game-power-bank supplier, but no exact A10 relationship is established.

Alibaba/Accio indexing exposes the product thumbnail asset:

```text
Ha68a0e682f4a49688cf5c9f9735995e7l.jpg
```

The Alibaba CDN image could not be retrieved in this environment, so the enclosure remains unverified.

Conclusion: **candidate only; no lineage confidence upgrade until exact physical-image comparison succeeds.**

## Exact-fingerprint indexed-search result

Searches combining the rare physical/product tuple:

```text
A10
5800mAh / 37Wh
67 × 141 × 20 mm
22.5W
15W
游戏 / 移动游戏电源
```

currently reproduce the already-known exact XGO/A10 marketplace-derived corpus but do not expose a second independently named mainland OEM.

This increases the relative value of the source-like native Chinese artwork layer already recovered under watermark:

```text
cn1094161006qgoae
```

That artwork includes the exact A10 parameter sheet and the exact seller comparison:

```text
10000款游戏 / 摇杆模式 / 赠送32G TF卡
500款游戏 / 方向模式 / 赠送1G TF卡
```

The legal company/store identity behind the watermark remains unknown.

## Next highest-value paths

1. Recover the physical image behind Guangzhou Qili asset `mQTeKAqypwbi` and compare enclosure.
2. Recover Lechong asset `Ha68a0e682f4a49688cf5c9f9735995e7l.jpg` and compare enclosure.
3. Continue tracing `cn1094161006qgoae` and archival item `1005008975396605` through Chinese marketplace/social mirrors.
4. Search seller-side provisioning artifacts for exact `A10（无卡无游戏）`, especially replacement/original 32G card support.
5. Treat any 32G/10000-game result without exact A10 enclosure/model proof as non-dispositive.
