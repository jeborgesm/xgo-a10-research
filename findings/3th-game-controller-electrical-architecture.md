# 3TH GAME dedicated controller-port architecture

## Status
Comparative hardware evidence. This finding documents a predecessor/related game-console + power-bank design and does **not** claim that XGO or DY19 use an electrically identical circuit.

## Source
Charging Head Network (充电头网), 2020 teardown of the Chongqing Sanshi Technology `3th game` game-console/power-bank.

Source URL:
https://www.chongdiantou.com/archives/48095.html

## Confirmed from teardown
The photographed device combines game-console and power-bank functions and exposes several physically distinct interfaces.

The teardown labels a dedicated **手柄接口** (controller/handle interface) separately from the USB-A power-output connector.

The same teardown states that the USB-A connector's D+ and D- contacts are shorted together. This is consistent with a charging-port identification arrangement and means that connector is not functioning as a conventional USB host data port in the photographed unit.

The teardown therefore provides direct precedent inside this unusual game-console/power-bank product category for:

- familiar USB-family connectors being used primarily for power;
- a separate dedicated controller/handle interface;
- multiplayer-controller support not implying generic USB HID support.

## Relationship to DY19
A public DY19 package photograph includes a wired controller and a paper/manual carrying `3TH-GAME` branding. This creates a useful historical/product-line lead connecting DY19 research to the earlier `3th game` ecosystem.

This is **not sufficient evidence** to identify Chongqing Sanshi Technology as the DY19 manufacturer or to prove identical electronics.

## Relationship to XGO Handle Interface
XGO firmware independently exposes a two-stream synchronous serial controller scanner, while physical experiments show that generic USB controllers are not accepted as Player 2.

The 3TH GAME teardown therefore strengthens a narrower architectural interpretation: the term **Handle Interface** in these products can plausibly mean a dedicated controller electrical interface rather than a conventional USB HID host port.

It does not prove the XGO connector pinout or protocol.

## Confidence
### Confirmed
- 3TH GAME teardown has a separately identified controller/handle interface.
- Its USB-A power connector has D+ and D- shorted in the photographed hardware.
- The product combines gaming and power-bank functionality.

### Strong comparative relevance
- Controller support in this product ecosystem need not mean generic USB HID.
- DY19's `3TH-GAME` material makes the earlier platform/product family worth tracing for controller accessories and connector documentation.

### Unknown
- Whether XGO, DY19 and 3TH GAME share a manufacturer.
- Whether their controller protocols are electrically compatible.
- Whether XGO micro-USB ID is used as controller DATA.
- Exact controller plug/pinout for DY19 or 3TH GAME.

## Next research target
Locate high-resolution photographs, listings, manuals, teardown images, replacement controllers, or PCB photographs for `3TH GAME`, DY19, and related Sanshi/三十/叁拾 products. Priority is a clear view of the controller plug and console-side connector, followed by any controller PCB that can expose the serialization circuit.