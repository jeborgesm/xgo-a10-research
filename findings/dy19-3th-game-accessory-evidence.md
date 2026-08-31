# DY19 / 3TH-GAME packaged controller evidence

## Status
Comparative physical/product evidence. This finding does not yet establish the DY19 controller connector pinout or electrical compatibility with XGO.

## DY19 package photograph
Handhelds Wiki preserves a DY19 package photograph showing:

- DY19 handheld/power-bank console;
- a wired second-player controller;
- AV cable;
- USB charging cable;
- interchangeable thumb caps;
- a paper manual visibly branded `3TH-GAME` / `PRODUCT DESCRIPTION`.

Source:
https://handhelds.wiki/DY19_Power_Bank_and_Game_Console

The photograph is useful because it proves a wired controller was supplied with at least one DY19 retail package rather than two-player support being only generic marketing text.

## Product-line clue
The `3TH-GAME` marking is unusually specific and independently resembles the earlier `3th game` game-console/power-bank model documented in a 2020 Charging Head Network teardown.

The older unit is labeled:

- model: `3th game`;
- manufacturer: Chongqing Sanshi Technology Co., Ltd. (`重庆叁拾科技有限公司`);
- game-console + power-bank architecture;
- dedicated `手柄接口` (controller/handle interface);
- separate TV interface;
- separate Micro USB power input and USB-A power output.

The older hardware is not the same generation as DY19: it uses a bonded processor plus Samsung K5L2731CAA-D770 MCP and only 300 built-in games. Therefore the shared branding should be treated as a product/OEM lineage lead, not evidence of an identical PCB or protocol.

## Relevance to XGO
The XGO documentation also calls its mystery connector a `Handle Interface`, and firmware contains a dedicated synchronous controller scanner rather than evidence that generic USB HID is the expected P2 path.

The combination of:

1. an older `3th game` product with a separately named controller/handle interface;
2. a DY19 retail package with `3TH-GAME` manual and supplied wired controller;
3. XGO documentation using the same `Handle Interface` terminology;
4. XGO firmware implementing a two-stream active-low synchronous controller bus;

makes the `3TH-GAME` product/OEM trail a high-value source for identifying the physical accessory and connector convention.

## Important negative result
Chinese-language searches for `3TH GAME`, `重庆叁拾科技`, `手柄`, `手柄接口`, DY19 teardown/controller combinations have not yet produced a standalone replacement-controller listing or a clear controller-PCB teardown. Search results currently collapse heavily onto mirrors of the 2020 teardown.

This negative result is useful operationally: future searches should emphasize image hashes, marketplace archives, manual scans, and model-family aliases rather than repeating generic text searches.

## Confidence
### Confirmed
- A DY19 package photograph contains a wired controller.
- The same photograph contains a manual visibly marked `3TH-GAME`.
- An older game-console/power-bank exists with model `3th game` and manufacturer label `重庆叁拾科技有限公司`.
- That older product explicitly has a dedicated `手柄接口`.

### Strong lead
- `3TH-GAME` may represent an OEM/product-family lineage that continued into DY19 packaging.
- Historical controller accessories from this lineage may reveal connector conventions useful for XGO.

### Not established
- DY19 manufacturer identity.
- XGO manufacturer identity.
- Electrical compatibility among 3th game, DY19 and XGO controllers.
- Exact DY19 controller plug type from the currently available package photograph.

## Next targets
- recover original/high-resolution copy of the DY19 package photograph by its image hash/name;
- locate DY19 controller-only marketplace listings;
- search Chinese marketplace/archive indexes for `3TH-GAME` rather than only `DY19`;
- locate DY19 teardown photographs from the 4PDA thread;
- obtain DY19 stock `bisrv.asd` and test against the preserved XGO scanner fingerprints.