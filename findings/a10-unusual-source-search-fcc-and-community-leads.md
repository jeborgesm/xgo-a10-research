# A10 unusual-source hardware search — FCC and community leads

Date: 2026-09-15
Branch: `research-a10-hardware-lineage`
Status: **active research; identity gates preserved**

## Search scope

Expanded beyond ordinary product pages into Chinese teardown/repair terminology, Bilibili/Tieba/52pojie/NGA/Zhihu indexing, Reddit/SBCGaming, firmware/modding terms, FCC certification mirrors, white-label identities, and exact physical/spec fingerprints.

## Strong known comparator reconfirmed: XGO DY09 teardown

The 2022 ChargerLAB/充电头网 DY09 teardown remains the strongest published XGO-family internal-hardware reference. It proves an XGO/芯果 game-power-bank design using physically separate power/wireless and game PCBAs connected for power. The power board uses INJOINIC IP5356 and IP6829; the game board uses a bonded processor, Spansion S29GL128N 128-Mbit flash, a 21.47727-MHz crystal, regulator marking `BE=A1D`, display/button FFCs, and a board-mounted speaker.

This remains **family architecture evidence only**, not proof of A10 component identity.

## New community lead: actual XGO A10 firmware discussion

A 2025/2026 r/SBCGaming thread is specifically titled around an XGO A10 with a missing stock card. The original poster claimed `RK3566 + RK817`, but another participant explicitly disputed RK3566. More valuable than the disputed chip claim is a June 2026 response describing the device as an `sf2000 clone but not the same`, saying an SF2000-prepared card can be combined with original XGO content and noting that key mapping, screen orientation, and ROM list are integrated in XGO-specific files.

Treat all statements as community reports, not verified hardware identification. The thread is nevertheless useful evidence that other users are independently reverse-engineering this exact XGO A10 software family.

## New regulatory lead: FCC ID 2AUZ9-A10

FCC records expose a 2025 certification for model `A10`, marketed as a `Magnetic Wireless Charging Power Bank`, applicant East Sky Industry Co., Limited, FCC ID `2AUZ9-A10`.

Most importantly, the short-term-confidential exhibits became public on 2025-07-17 and include:

- internal photographs (839 kB);
- external photographs (929 kB);
- user manual (2.5 MB);
- test setup photographs;
- antenna specification;
- block diagram;
- schematic;
- operational description;
- model statement.

The FCC application covers wireless charging at 113.78–206.41 kHz.

### Identity warning

There is **not yet enough evidence to identify FCC 2AUZ9-A10 as the XGO/芯果 game-power-bank A10**. `A10` is generic, the applicant differs from the Jinhangzhaobang manufacturer identity recovered from the user's shipping label, and the FCC marketing description omits the game-console function. It is therefore a lead requiring visual comparison of the external/internal exhibits before any component or schematic data can be transferred to the XGO graph.

If the external photos match the transparent XGO enclosure and the internal photos match visible A10 board geometry, this becomes potentially the highest-value hardware source found so far because the filing includes both internal photos and a schematic. If they do not match, discard it as a naming collision.

## Exact-model public documentation remains sparse

Handhelds Wiki still lists the XGO A10 as Linux, 10000 mAh, 141x67x20 mm, with video output, but leaves SoC and firmware unknown. This confirms that even the specialist handheld catalog has not closed the board identity.

Chinese retail indexing independently continues to distinguish A10 and DY10. JD indexes `A10 black — 10000mAh + ten-thousand games + magnetic power bank`; Youzan indexes DY10 as an XGO/芯果 10000mAh 22.5W/ wireless magnetic game-power-bank. This supports family relationship but not A10=DY10.

## Next research targets

1. Retrieve and visually inspect FCC 2AUZ9-A10 external and internal photo exhibits. Reject or promote based on enclosure/PCB geometry, not model name.
2. If identity matches, extract schematic/block-diagram component designators, power ICs, wireless controller, battery topology, and board interconnects.
3. Mine the r/SBCGaming A10 participant trail and linked media for photographs or firmware copies; verify any claimed SoC against executable evidence before recording it.
4. Continue Chinese searches using repair/failure language rather than product language: `A10 游戏充电宝 维修`, `芯果 A10 拆机`, `DY10 主板`, `游戏充电宝 主板`, `不开机`, `换屏`, `喇叭`, `功放`, `尾插`, `电池`, `拆壳`.
5. Search second-hand/parts channels for damaged A10/DY10 boards, because repair listings often expose PCB photographs that normal product listings do not.
6. Preserve the existing physical-teardown plan for the user's broken original unit as the definitive identity gate if public sources remain incomplete.
