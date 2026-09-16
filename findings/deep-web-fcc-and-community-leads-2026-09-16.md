# Deep web / FCC / community hardware search — 2026-09-16

Status: research leads; preserve distinctions between exact A10 evidence, family evidence, and naming collisions.

## FCC lead 2AUZ9-A10

FCC ID `2AUZ9-A10` is a 2025 filing by East Sky Industry Co., Limited for a product marketed as `Magnetic Wireless Charging Power Bank`, model A10. The filing has short-term-confidential exhibits released 2025-07-17: internal photos (document 7989626), external photos (7989625), user manual (7989627), and test setup photos (7989624). It also lists permanently confidential / metadata-only block diagram, schematic and operational-description exhibits.

This remains a lead, NOT an identification of the XGO A10. The applicant differs from the Jinhangzhaobang manufacturer identity recovered from the user's shipping documentation, and the FCC marketing description does not mention the game-console function. The public internal/external photo PDFs need to be acquired and visually compared before the lead is promoted. FCC filing page: https://fccid.io/2AUZ9-A10

Important regulatory detail: the application describes itself as original equipment, non-modular, non-composite, Part 15C low-power transmitter for the wireless-power function, 113.78–206.41 kHz. The form also notes that an FCC applicant need not itself be the actual manufacturer, so the East Sky applicant name alone cannot either prove or disprove an OEM relationship.

## Exact-family Chinese teardown remains DY09, not A10

Charging Head Network's XGO/芯果 DY09 teardown is still the strongest public naked-PCB evidence from the exact XGO game-power-bank lineage. It explicitly shows a two-PCBA architecture: an upper power-bank/wireless-charge board and a lower game-console board, connected for power. The power side uses Injoinic IP5356 and IP6829. This is family architecture evidence only, not proof of A10 component identity.

A 2026 Charging Head Network index still lists the XGO/芯果 5000mAh magnetic wireless game-power-bank teardown as the only CGO/XGO teardown in its >700-power-bank teardown catalog. That negative search result is useful: this major Chinese teardown archive does not currently expose an A10/DY10 teardown under the XGO/芯果 brand.

## Chinese video-community lead

Bilibili's indexed search currently exposes a 2026 short video titled `芯果XGO游戏机充电宝MagSafe无线磁吸便携移动电源苹果安卓大容量225W快充掌机怀旧经典街机`, posted by `ayu_yu鱼c`. It appears product-oriented rather than a teardown, but confirms the exact product family is circulating in Chinese video/social channels under descriptive terms rather than consistently under A10/DY10 model numbers. Future searches should therefore include the full descriptive product phrase and not rely only on model identifiers.

## Community reverse-engineering search

Searches for XGO A10 combined with the family fingerprints `bisrv.asd`, `WQW`, `Archive.sys`, `KeyMapInfo.kmp`, SF2000, Data Frog, HC15/H1512 did not locate a second public XGO-specific reverse-engineering project outside our repository in the indexed web.

The same fingerprints strongly recover the established SF2000/GB300 community: vonmillhausen's SF2000 documentation, frogtool, GB300/SF2000 Tool, and related Retro Handhelds Discord references. This reaffirms that the XGO firmware lineage is technically connected to a heavily reverse-engineered family, but it is not evidence that someone has already published an A10-specific teardown or firmware map.

The SF2000 documentation explicitly points to non-web-indexed community work in the Retro Handhelds Discord (`data_frog_sf2000`) and credits individual researchers such as bnister, notv37, taizou, adcockm, and others for discoveries around `bisrv.asd`, Archive.sys, key maps, ROM lists and emulator behavior. Those names/channels are high-value pivots for finding unpublished discussion or knowledge of later XGO-family derivatives.

## Exact XGO A10 public documentation state

Handhelds Wiki still lists the XGO A10 with SoC unknown, screen resolution unknown and firmware `?`, despite listing the correct horizontal form factor, Linux, 10000mAh battery and 141x67x20 mm dimensions. This is useful negative evidence: the broader handheld documentation community has not yet consolidated an A10 hardware identification or firmware archive.

## Next pivots

1. Acquire FCC documents 7989625/7989626/7989627 from FCC.gov or a mirror and visually fingerprint enclosure, coil, PCB shape, connector placement and labels. If mismatch is obvious, close 2AUZ9-A10 as a naming collision. If it matches, pursue confidential schematic/block-diagram provenance and East Sky supply-chain relationships.
2. Search Chinese social/video/community sources by descriptive phrase: `芯果 游戏机充电宝`, `磁吸无线充移动电源游戏机`, `游戏机充电宝`, plus repair terms `拆机`, `维修`, `主板`, `换屏`, `不开机`, `改装`, `刷机`, `固件` rather than model number alone.
3. Pivot through Retro Handhelds Discord / SF2000 researcher names for references to XGO, DY10, A10 or other HC15xx derivatives that never became indexed webpages.
4. Search second-hand/repair marketplaces and cached listings for broken A10/DY10 units; sellers often expose internal PCB photos unintentionally.
5. Keep exact-XGO evidence separate from SF2000/GB300 family inference and from unrelated products also named A10.
