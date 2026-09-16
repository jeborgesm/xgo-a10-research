# A10 hardware-lineage Chinese search — focused pass 01

Status: research lead map; no A10 PCB identification claimed unless explicitly stated.

## Strong new identity corroboration

Chinese JD indexing now explicitly exposes listings for `芯果 ... A10` described as a 10000mAh magnetic wireless game-console/power-bank. This independently ties the **芯果 / XGO product family**, **A10 model string**, **10000mAh capacity**, and the same game-console/power-bank product concept together in the mainland retail ecosystem.

This is useful identity evidence, but a retail listing is not evidence of the internal SoC or PCB.

## DY10 retail lineage

Chinese retail/editorial indexing also identifies the transparent XGO 10000mAh / 15W wireless / 22.5W wired product as **DY10**. The visible description emphasizes transparent construction and the same magnetic game-power-bank concept. DY10 therefore remains a strong commercial-lineage/search alias for the transparent specimen, but it must not be treated as electrically identical to A10 until PCB evidence closes that gap.

## Older XGO DY09 teardown — architecture precedent, not A10 equivalence

The 2022 ChargerLAB/充电头网 teardown of XGO/芯果 DY09 is still the best high-resolution internal precedent found so far. It establishes that an earlier XGO game-power-bank was physically split into:

- power-bank/wireless-charge PCBA;
- game PCBA;
- display and button daughterboard/flex connections;
- speaker on the game side.

Identified DY09 power components include:

- Injoinic IP5356 power-bank SoC;
- Injoinic IP6829 wireless-charge transmitter SoC;
- two XB7608 battery-protection devices;
- 2.2 uH boost/buck inductor;
- 0.4 uF / 100 V wireless resonant capacitor.

Its game board is clearly an older, simpler design: bonded game/display processor, Spansion S29GL128N 128-Mbit flash, 21.47727 MHz crystal, regulator marking `BE=A1D`, and an onboard speaker. Therefore it is useful for XGO design lineage and physical architecture, **not** as evidence for the A10 game SoC.

## Important negative result

This search pass did **not** locate a trustworthy teardown explicitly labelled XGO A10 or DY10 with readable game-PCB IC markings. Exact searches for A10 + 游戏机充电宝 + 拆解/主板/芯片 and the supply-chain SKU did not expose such a teardown in indexed results.

That negative result narrows the next search: stop treating generic `A10` as a sufficient discriminator. Search by physical/product fingerprints and mainland aliases instead.

## Search graph for next pass

High-value aliases/fingerprints:

- 芯果 / XGO / XGO PLUS+
- A10
- DY10
- 透明游戏机充电宝
- 游戏机充电宝
- 10000mAh / 5800mAh 37Wh
- 22.5W wired / 15W magnetic wireless
- 透明 / 机械朋克
- 主板 / PCBA / 拆机 / 拆解 / 维修 / 芯片 / 丝印 / 功放 / 喇叭
- manufacturer lead: 深圳市金航兆邦科技有限公司 / Jinhangzhaobang
- supply-chain SKU: 050005600-J01

## Audio-specific objective

For the planned audio-improvement work, the most valuable A10/DY10 board photographs are those showing:

1. speaker markings (impedance and wattage if printed);
2. traces/wires from speaker back to game PCB;
3. any small SOP/QFN audio amplifier near the speaker connector;
4. coupling capacitors / RC network / ferrites around the audio path;
5. SoC markings and nearby audio-output pins if identifiable;
6. whether speaker drive is direct, single-ended, or bridge-tied through an amplifier.

Do not infer the A10 amplifier from the DY09 or unrelated game-power-bank designs.

## Current evidentiary boundary

Physical specimen/manual evidence remains primary for A10 identity. Mainland retail indexing strengthens the A10 <-> 芯果/XGO connection. DY10 is a strong commercial-lineage alias. A readable matching A10/DY10 PCB remains the missing hardware bridge.

## Web sources used in this pass

- 充电头网 DY09 teardown: https://www.chongdiantou.com/archives/160933.html
- JD 芯果 handheld/game-power-bank search index exposing A10 listings: https://www.jd.com/sptopic/670411b79248cf309c2.html?brand=%E8%8A%AF%E6%9E%9C&electedExtAttrSet=&extAttrValue=expand_name%2C&sort_type=sort_default
- 什么值得买 article/index describing transparent XGO DY10 10000mAh / 15W / 22.5W product: https://post.smzdm.com/p/akkv85dk/
