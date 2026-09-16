# A10 hardware lineage — Chinese search pass 02

Date: 2026-09-16
Branch: `research-a10-hardware-lineage`

## Purpose

Continue XGO-first mainland/OEM archaeology using the physical specimen fingerprint rather than sibling-first searches. This pass concentrated on the apparent A10/DY10 naming split and on finding teardown/PCB/audio-component evidence.

## Strong new catalog evidence: A10 and DY10 coexist as retail identities

Mainland JD search results for the 芯果 brand explicitly index a product variant as:

- `A10黑`
- `10000mAh+万款游戏+磁吸充电宝`

The same indexed catalog also carries XGO 10000mAh game-console/power-bank products.

Separately, a Youzan/VBEINGS listing indexes:

- `XGO/芯果`
- `10000mAh`
- `500款游戏`
- `DY10`
- `22.5W`
- wireless magnetic charging

SMZDM editorial/product material describes the transparent cyber/industrial XGO 10000mAh game power bank as DY10 and specifies 15W wireless and 22.5W wired charging.

A Korean Coupang listing independently uses `XGO ... 10000mAh DY10` for the product family.

### Interpretation

The evidence is now strong that **A10 and DY10 are both genuine commercial identifiers in the XGO/芯果 game-power-bank ecosystem**. It is still not safe to assert `A10 == DY10` electrically. The most useful working model is:

`XGO / 芯果 -> transparent 10000mAh game-power-bank family -> A10 and DY10 commercial identities`

The next discriminator must be PCB/component evidence, not more title matching.

## Important naming caution

`DY10` is not globally unique. Searches also return unrelated power banks and optical/DLP products using DY10. Future searches must retain XGO/芯果/game-console/transparent-shell qualifiers to avoid false lineage.

## Teardown/PCB result

Exact searches combining A10 or DY10 with `拆机`, `拆解`, `主板`, `维修`, `芯片`, `功放`, and `喇叭` still did not expose a trustworthy teardown of the target A10/DY10 game board with readable IC markings.

This is a useful negative result: repeating generic `A10 拆机` searches has diminishing value because A10 is extremely noisy across unrelated electronics.

## Search strategy refinement

Future passes should pivot from model-name searches to physical and electrical fingerprints:

- `芯果 XGO 透明 游戏机充电宝 主板`
- `芯果 XGO 透明 维修`
- `游戏机充电宝 10000mAh 5800mAh 37Wh 主板`
- `游戏机充电宝 22.5W 15W 拆机`
- `XGO 机械朋克 主板`
- `XGO 功放 喇叭`
- manufacturer/address terms around 金航兆邦 / Jinhangzhaobang
- image/video sources where board silkscreen can be read even when the listing title omits A10/DY10.

Search repair/resale/second-hand ecosystems as well as formal teardown sites; damaged units and repair posts may expose the game PCB more clearly than retail material.

## Audio reverse-engineering target

No target-A10 amplifier identification was obtained in this pass. Do **not** propagate amplifier identities from older DY09 or unrelated game-power-bank products.

The desired evidence remains:

1. readable speaker marking (impedance and wattage if printed),
2. speaker connector/wiring and PCB destination,
3. amplifier IC marking,
4. amplifier supply rail,
5. input coupling/filter passives,
6. SoC/DAC/PWM source feeding the amplifier,
7. whether volume control is implemented digitally before the amplifier or through analog gain control.

This information will determine whether the future audio-improvement branch should prioritize gain staging/clipping, sample/PWM configuration, lightweight filtering/EQ, or physical amplifier/speaker constraints.

## Sources captured in this pass

- JD 芯果 catalog/search results: A10 black, 10000mAh, game library, magnetic power-bank variant.
- Youzan/VBEINGS: XGO/芯果 DY10, 10000mAh, 22.5W, wireless magnetic game power bank.
- SMZDM: transparent XGO DY10 description, 10000mAh, 15W wireless, 22.5W wired, transparent mechanical/cyber styling.
- Coupang: XGO 10000mAh DY10 commercial identity.
- Handhelds Wiki: DY10 page remains SoC-unknown and should be treated as secondary corroboration only.

## Evidence boundary

Retail-title convergence is useful for identity mapping but does not establish PCB equivalence. Physical specimen evidence and readable board/component photographs outrank retail naming.