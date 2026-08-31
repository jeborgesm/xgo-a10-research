# 3th game power-bank/controller lineage clue

Status: **comparative product-line evidence; manufacturer continuity not yet proven**.

## Discovery

A DY19 product photograph preserved by Handhelds Wiki shows the console together with its wired second-player controller, AV cable and manual. The manual cover is visibly branded:

```text
3TH-GAME
PRODUCT DESCRIPTION
```

This is notable because an independent 2020 teardown by ChargerLAB / Chongdiantou documents an earlier game-console/power-bank product whose printed model is literally `3th game`.

The older unit is attributed on its product label to:

```text
重庆叁拾科技有限公司
Chongqing Sanshi Technology Co., Ltd.
```

The teardown describes a 10,000 mAh game-console power bank with a dedicated controller/handle port and TV-output port.

## Why this matters to XGO/DY19

The DY19 is another game-console/power-bank product and public product photos show its supplied wired controller alongside a `3TH-GAME` manual. This creates a plausible product-line/ODM continuity trail from the older `3th game` hardware to the later DY19 family.

This is especially relevant to the XGO Handle Interface investigation because the older teardown makes an important architectural distinction:

- the device has a dedicated **controller/handle interface** (`手柄接口`);
- it separately has a USB-A power-bank output;
- the teardown explicitly reports the USB-A receptacle's **data pins are shorted together**;
- therefore that USB-A connector is power-bank infrastructure, not a normal USB host controller port;
- the dedicated controller connector is mounted separately on the game PCB.

That product architecture is conceptually consistent with the XGO evidence: a connector that physically resembles a common USB-family connector can still be a proprietary controller interface rather than ordinary USB HID.

## DY19 controller evidence

The preserved DY19 accessory photo is particularly useful because it shows that the advertised two-player support is not merely generic marketing text: a dedicated wired controller is physically supplied with at least one DY19 package variant.

Retail listings independently advertise:

- external gamepad support;
- two-player mode;
- TV output;
- the combined game-console/power-bank role.

One secondary retail source labels the external controller interface `USB 2.0`; that wording is **not accepted as proof of USB HID or USB electrical signaling**. Cheap OEM listings frequently describe connector form factors loosely, and the XGO experiments already demonstrate why connector shape must not be confused with protocol.

## Confidence

### CONFIRMED

- a preserved DY19 package photograph shows a wired controller supplied with the console;
- the manual visible in that photograph is marked `3TH-GAME`;
- a 2020 teardown documents an earlier game-console/power-bank whose model is `3th game`;
- that older product label names Chongqing Sanshi Technology Co., Ltd.;
- the older product has a dedicated controller/handle connector distinct from its USB-A power-bank output;
- the older product's USB-A data pins were reported shorted together by the teardown.

### STRONG / USEFUL COMPARATIVE EVIDENCE

- `3TH-GAME` branding on the DY19 manual likely reflects continuity in the game-power-bank OEM/product ecosystem rather than an unrelated coincidence;
- dedicated non-HID controller interfaces have precedent in this exact game-console/power-bank product class;
- DY19's supplied controller is now a high-value candidate accessory for electrical/protocol comparison with XGO.

### NOT YET CONFIRMED

- that Chongqing Sanshi Technology manufactured the DY19;
- that the 2020 `3th game` controller protocol survived into DY19;
- that DY19 and XGO use the same controller connector pinout;
- that the DY19 controller uses USB signaling despite some retail descriptions saying `USB 2.0`;
- that the older controller connector has the same physical form factor as XGO's micro-USB-shaped Handle Interface.

## Research consequences

1. Search `3TH-GAME`, `3th game`, `重庆叁拾科技有限公司`, and related Chinese product terminology in addition to `DY19` when hunting controller manuals/accessories.
2. Locate high-resolution photos of the DY19 controller plug and console controller receptacle.
3. Locate the 2020 `3th game` controller accessory and determine connector pin count/form factor.
4. If a DY19 controller can be sourced, characterize it passively before connecting it to XGO.
5. Preserve the distinction between connector form factor and electrical protocol throughout the Handle Interface work.

## Sources

- ChargerLAB / Chongdiantou, `拆解报告：10000mAh 游戏机移动电源3th game`, 2020-04-05.
- Baidu-hosted reproduction of the same teardown with detailed component/connector captions.
- Handhelds Wiki, `DY19 Power Bank and Game Console`, preserved product/accessory photograph.
- Current DY19 retail listings advertising external gamepad/two-player support.
