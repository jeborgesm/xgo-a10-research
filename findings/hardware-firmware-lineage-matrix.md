# XGO / SF2000-family hardware and firmware lineage matrix

Status: active archaeology map  
Updated: 2026-09-07

This matrix is the working evidence map for the platform lineage leading toward the XGO A10. It deliberately separates **product naming**, **firmware compatibility**, and **physical board evidence** because those do not map one-to-one in this ecosystem.

Legend:

- **CONFIRMED** — direct binary, PCB, card-image, or hardware evidence.
- **STRONG** — multiple independent sources or direct compatibility evidence.
- **PARTIAL** — useful evidence exists but exact revision/board identity is incomplete.
- **UNKNOWN** — active research target.
- **N/A** — not applicable or not currently useful.

| Evidence | SF2000 | Q19 | DY12 early | DY12 MY2024 | DY14 | DY19 | XGO A10 |
|---|---|---|---|---|---|---|---|
| Product class | handheld | handheld + power bank | game/power-bank family | game/power-bank family | handheld + power bank | handheld + power bank | handheld + magnetic power bank |
| CPU/platform | **CONFIRMED** HCSEMI B210 / HC15xx family | **STRONG** close B210/SF2000 family per experienced hardware owners; CPU marking removed in teardown | **PARTIAL** SF2000-like behavior on some revisions | **STRONG** owner reports DY19 multicore BIOS works | **CONFIRMED** Hichip H1512 800 MHz | **CONFIRMED** H1512-family from recovered firmware | **CONFIRMED** H1512/HC15xx family from binary archaeology |
| OS/runtime | **CONFIRMED** ALi TDS2 stock | **STRONG** SF2000-adapted firmware family | **PARTIAL** SF2000-family | **STRONG** DY19-family | **CONFIRMED** H1512/TDS2 family evidence | **CONFIRMED** H1512/TDS2 family | **CONFIRMED** H1512/TDS2 family |
| RAM | known SF2000-family DDR2 | **CONFIRMED** Hynix HY5PS1G1631C 1-Gbit DDR2 = 128 MiB | UNKNOWN | UNKNOWN | **CONFIRMED** Nanya NT5TU64M16DG-AD 1-Gbit DDR2 = 128 MiB | software implies same memory class; physical chip UNKNOWN | physical chip identity UNKNOWN |
| SPI NOR | known onboard SPI + security-register behavior | **CONFIRMED** UC25HQ40 4-Mbit / 512 KiB class; community reports same security-register copy-protection mechanism | UNKNOWN | UNKNOWN | **CONFIRMED** UC25HD40 4-Mbit / 512 KiB | physical part UNKNOWN | onboard SPI access **CONFIRMED**; physical part UNKNOWN |
| Power-management IC | N/A to lineage | **CONFIRMED** IP5219 | UNKNOWN | UNKNOWN | **CONFIRMED** IP5306 | UNKNOWN | UNKNOWN |
| Audio IC(s) | known board-level implementation | **CONFIRMED** OPA1612-marked devices in Q19 teardown | UNKNOWN | UNKNOWN | **CONFIRMED** dual 8002A amplifiers | UNKNOWN | UNKNOWN |
| PCB revision / silkscreen | available in community photos | **CONFIRMED** XYC-Q20-A-V3.0 / 2023-04-14 | UNKNOWN | UNKNOWN | teardown PCB photos available | **CRITICAL UNKNOWN** | current specimen photos exist; deeper silkscreen capture still desirable |
| Stock firmware/card | **CONFIRMED** widely preserved | no authenticated stock image recovered yet; SF2000-derived/adapted firmware use **CONFIRMED externally** | partial/community-related | DY19-compatible by owner report | stock card/application target not recovered | **CONFIRMED** owner-originated full SD image selectively extracted; Chinese-only and later English-list revisions reported | **CONFIRMED** original card/application preserved |
| Firmware interoperability | baseline | **STRONG:** adapted SF2000 firmware reported usable; stock SF2000 boots mirrored with dead controls; GB300 multicore also mismatches | SF2000 can boot on some revisions with bad/no controls | DY19 multicore BIOS reported working | H1512 family comparator | **CONFIRMED** SF2000-derived multicore works with DY19-specific bisrv | sibling firmware generally boots only with model-specific adaptation |
| Controller implementation | known stock SF2000 RF/wired behavior | physical ports visible; exact protocol unresolved | varies by revision | likely DY19-like | physical/controller paths visible; exact protocol unresolved | application differs from exact XGO scanner; model-specific input adaptation **CONFIRMED** | **CONFIRMED** B15/L0/B7 12-bit serial scanner + RF-specific paths |
| LCD/display adaptation | stock reference | different display behavior from stock SF2000; mirrored-image report | revision-dependent | likely DY19 branch | panel/FPC photographed | model-specific; direct firmware evidence | **CONFIRMED** XGO-specific display adaptation |
| External controller | stock family support | 3.5-mm AV / controller-family context | shared DY-family accessories reported | same family | supported | supported | Handle Interface present; protocol reconstructed |
| Teardown / PCB imagery | available | **COMPLETE — 16-image Steward Fu corpus archived** | target | target | **COMPLETE — Steward Fu corpus archived** | **CRITICAL MISSING LINK**; authenticated 4PDA teardown attachments known to exist | partial owner/specimen photos; deeper controlled teardown not yet performed |
| Binary application recovered | yes | no | no | no | SPI dump only / no stock application recovered | **YES** 12,477,596-byte BISRV.ASD | **YES** 12,768,452-byte BISRV.ASD |
| Direct XGO software relationship | ancestor/reference | hardware/power-bank comparator | likely early family branch | stronger DY19 branch clue | H1512 hardware comparator | **VERY STRONG — direct software/content fork evidence** | target device |
| Game-list/content ancestry | stock reference | UNKNOWN | UNKNOWN | UNKNOWN | retail emulator-family overlap | **CONFIRMED** XGO catalogs are overwhelmingly subsets of original DY19 lists | derived target |
| UART/test-pad evidence | **CONFIRMED externally** bootloader emits diagnostics over UART; HC15xx UART1 is the documented boot/debug console | PCB should be inspected for candidate pads | UNKNOWN | UNKNOWN | teardown/SPI test access documented | UNKNOWN | **STRONG platform likelihood; physical XGO pad identity UNKNOWN** |

## Current best-supported architecture model

The evidence currently supports:

```text
HCSEMI / Hichip HC15xx reference platform
              |
      SF2000 software/runtime family
        /        |          \
      X60       Q19        DY-family revisions
                  \          /
                   \        /
                     DY19
                      |
        same software/content branch
                      |
                   XGO A10
           + XGO-specific board layer
```

The diagram is **not** a literal production genealogy. It represents evidence strength and shared platform ancestry.

## Most important conclusions

1. **Retail model number is not a sufficient hardware identifier.**
   DY12 has revision-dependent compatibility and DY19 itself has second-generation/upgraded listings.

2. **PCB revision + firmware hash outrank model name.**
   Every future hardware record should capture enclosure revision, PCB silkscreen, firmware SHA-256, and card layout together.

3. **DY19 is currently the closest software/content sibling to XGO.**
   Direct recovery proves common H1512 SDK/compiler lineage, large binary reuse, shared resources, and an overwhelmingly subset-derived XGO game catalog.

4. **Q19 is currently the strongest physical power-bank-board bridge.**
   It documents a close SF2000-family implementation in the same unusual handheld/power-bank product category.

5. **The missing DY19 PCB is the single highest-value hardware target.**
   It would connect the known DY19 application to a known physical board and allow direct Q19 -> DY19 -> XGO hardware comparison.

## Priority unknowns

### Tier 1 — likely to change XGO engineering decisions

- DY19 PCB silkscreen and component-side photographs.
- DY19 RAM and SPI NOR identities.
- DY19 controller/handle routing.
- DY19 RF presence/absence.
- XGO A10 RAM, SPI NOR, PMIC, and PCB revision.
- XGO debug UART/test-pad identification.

### Tier 2 — lineage reconstruction

- authenticated Q19 stock `bisrv.asd` / SD image.
- DY12 MY2024 PCB + firmware hash.
- early DY12 PCB + firmware hash.
- DY14 stock `bisrv.asd`.
- component/PCB identifier reuse across OEM siblings.

### Tier 3 — supporting historical evidence

- manufacturer/OEM catalogs;
- archived repair listings;
- replacement-board sellers;
- certification photographs;
- Wayback/cache recovery of forum attachments.

## Evidence discipline

Do not convert a row marked STRONG or PARTIAL into a hardware fact without direct board or firmware evidence. In particular:

- same shell does not mean same PCB;
- same model number does not guarantee same revision;
- identical filesystem layout does not guarantee identical GPIO;
- a firmware that boots is not proof of controller/display compatibility;
- seller battery capacity is not equivalent to measured cell capacity.


## 2026-09-07 search update

A targeted search for the exact Q19 PCB identifier `XYC-Q20-A-V3.0` and component combination did **not** locate another indexed board, repair listing, factory document, or firmware package. At present Steward Fu's teardown appears to be the uniquely indexed source for that exact PCB marking.

This increases the preservation value of the archived Q19 image corpus and makes Q19 stock-card recovery the most useful next step for that branch.


## Revision identity rule

For this family, a useful archived specimen should be identified by the tuple:

```text
retail model
+ enclosure revision
+ PCB silkscreen/revision
+ bootloader/SPI state
+ bisrv.asd SHA-256
+ Resources hash set
+ card-image provenance
```

This is now necessary because DY12 and DY19 both have evidence of revision-dependent software behavior, and Q19 demonstrates that even a platform-compatible application can boot with unusable display/input adaptation.



## 2026-09-07 continuation update — X60 debug comparator and revision signals

The post-Q19 search produced a new engineering-relevant comparator rather than another retail-name match.

### X60 is now a strong debug-interface comparator

4PDA contributor `bnister`, who owned and modified X60 hardware, reports:

- X60 uses the **same underlying platform** as SF2000;
- X60 omits the SF2000 `XN297` wireless-controller IC;
- X60 uses a **different LCD**;
- X60 scans buttons through a **different GPIO/pin**;
- the board exposes **many test pads**;
- he physically brought out a **UART / serial debug port** for development;
- at least **two X60 hardware revisions** exist, including display-init differences between units.

This materially strengthens the working rule that HC15xx-family products share the runtime/platform while moving display, controller and radio adaptation into product-specific board-support code.

Engineering consequence for XGO:

> X60 is now the best documented sibling precedent for a factory/debug UART on a close HC15xx-family board. XGO test-pad identification should prioritize clusters geometrically/electrically analogous to X60 UART/test pads before attempting blind probing.

Evidence:
- https://4pda.to/forum/index.php?showtopic=1067862&st=380
- https://4pda.to/forum/index.php?showtopic=1067862&st=640
- https://4pda.to/forum/index.php?showtopic=1067862

### DY19 display specification disagreement is preserved as a revision clue

Two maintained/community records disagree:

- 4PDA DY19 header: **3.25 inch, 640x480**;
- Handhelds Wiki: **3.2 inch, 320x240**.

Do **not** collapse this to one value yet. DY19 already has revision-dependent firmware evidence, and X60 independently demonstrates multiple display revisions on the same retail model family. The disagreement is therefore retained as a possible DY19 panel/board-revision signal.

Evidence:
- https://4pda.to/forum/index.php?showtopic=1090810
- https://handhelds.wiki/DY19_Power_Bank_and_Game_Console

### PGP AIO Union X35 / X60 naming needs revision-aware handling

The X35/X60 trail is useful but must remain **PARTIAL** because retail naming is inconsistent.

Evidence recovered:

- a 2023 SF2000 thread initially identified Russian-market PGP AIO Union X35 with X60;
- `bnister` first corrected a C35/X35 mix-up, then concluded that the actual X35 appears to be X60 on the same chip/platform;
- a later owner with PGP AIO Union X35 reported firmware similar but not identical to the Q19-class unit;
- stock SF2000 firmware booted on both that Q19-class unit and PGP X35 with the **same mirrored-image + dead-controls** failure mode.

This is useful as board-support-layer evidence, but **PGP AIO Union X35 must not be treated as a single immutable hardware identity** until PCB silkscreen + firmware hash are recovered.

Evidence:
- https://4pda.to/forum/index.php?showtopic=1067862&st=640
- https://4pda.to/forum/index.php?showtopic=1090810&st=20
- https://4pda.to/forum/index.php?showtopic=1060903&st=160

### DY19 teardown recovery status

The authenticated 4PDA teardown post by `{{XENON}}` is still indexed and confirms:

- the unit was opened and photographed internally;
- the processor marking had been deliberately removed;
- the installed cell was physically judged to be about **4000 mAh**, despite 6000 mAh retail claims.

However, direct attachment-object URLs/IDs were **not recovered** in this pass. Search-engine image retrieval did not surface the actual 4PDA PCB photographs. The DY19 PCB therefore remains the critical missing physical link.

Evidence:
- https://4pda.to/forum/index.php?showtopic=1090810&st=0

## Supplemental comparator matrix — X60 / PGP X35

| Evidence | X60 | PGP AIO Union X35 |
|---|---|---|
| HC15xx/SF2000-family platform | **CONFIRMED externally** by hardware owner | **STRONG/PARTIAL**; naming/revision ambiguity remains |
| LCD adaptation | **CONFIRMED** different from SF2000; multiple display revisions reported | **STRONG** SF2000 boot can produce mirrored output |
| Controller GPIO adaptation | **CONFIRMED** different button-scan pin from SF2000 | **STRONG** stock SF2000 can boot with dead controls |
| XN297 wireless-controller IC | **CONFIRMED absent** on X60 comparator board | UNKNOWN |
| UART/debug | **CONFIRMED externally** UART physically broken out for development; many test pads | UNKNOWN |
| Firmware/card preservation | community BIOS/Resources and conversion packages exist | **CONFIRMED externally** full 7.5-GB card dump posted in 2026 |
| Revision risk | **CONFIRMED** at least two hardware/display revisions | **HIGH**; retail naming overlaps X60/X35/C35 discussions |
| Value to XGO archaeology | **HIGH — debug-pad and board-support comparator** | **MEDIUM — additional firmware/display/input comparator** |

## Priority adjustment after this pass

The search order is now:

1. **DY19 teardown attachment recovery** remains the highest-value missing physical bridge.
2. **X60 UART/test-pad geometry recovery** is promoted: recover the exact teardown frames or board photos showing the pads used by `bnister`.
3. **Authentic Q19 stock card / bisrv.asd** remains the best way to bind the complete Q19 PCB corpus to software.
4. **DY12 MY2024 exact PCB + firmware** remains necessary to separate it from early DY12.
5. **DY14 stock application** remains necessary to connect its known H1512 board to software.
6. **PGP AIO Union X35 card dump** is now a useful secondary binary comparator, but only if accompanied by specimen/revision provenance.




## 2026-09-07 continuation update — UART is a platform bring-up/recovery interface, not merely logging

Further X60/SF2000 evidence materially increases the engineering value of the serial-debug trail.

### Same researcher physically cross-compared SF2000, X60 and Q19

In the same 4PDA hardware discussion, `bnister` explicitly states that his own **SF2000, X60 and Q19** all survived full-card imaging operations, and that he had even repurposed the weak original X60 card for Q19.

That matters because the earlier X60 statements are therefore not based on visual similarity alone; they come from a researcher who physically possessed and modified all three relevant sibling devices.

The same discussion records:

- X60 has many test pads;
- a UART was physically wired out for development;
- the **stock bootloader prints the contents of the `bios` directory over UART** while booting;
- SF2000 and X60 share the same bootloader bug;
- X60 can run the SF2000 shell/emulators after replacing `bios/bisrv.asd` with an X60-specific adaptation;
- stock SF2000 bootloader code can remain usable on X60 even after accidental replacement, further separating boot ROM/SPI behavior from application-level board adaptation.

Evidence:
- https://4pda.to/forum/index.php?showtopic=1067862&st=380
- https://4pda.to/forum/index.php?showtopic=1067862&st=400

### HCSEMI B210 documentation confirms serial boot capability

The recovered HCSEMI B210 brief datasheet lists:

- UART interfaces;
- multiple boot modes;
- **boot program download and execution over a serial port**.

This changes the risk/reward model for XGO test-pad work.

The serial pads on a close sibling may expose one or both of:

1. a normal boot/debug console used by the stock loader/application;
2. a lower-level ROM/boot-program download interface capable of executing a recovery payload.

Do **not** assume that the first discovered XGO UART automatically exposes the B210 serial-download mode. Pinmux, strap state, SPI boot state and board routing may differ. But it is now a documented SoC capability rather than speculation.

Evidence:
- HCSEMI B210 Brief Datasheet, section 2.12:
  https://manuals.plus/m/dc4b1fc0287fee839b3a965d9a5fdd8f0383539748b6e10e04ab5c755a9046da

### Open-source HC15xx work identifies the likely debug UART instance

Current HC15xx/SF2000 emulation and board-configuration work independently identifies two UART blocks and describes **UART1 as the boot/debug console**.

Recovered addresses from the open-source HC15xx model:

```text
UART0  physical 0x18818300
UART1  physical 0x18818600  <- boot/debug console
```

The SF2000 hcRTOS board configuration further maps the enabled UART1 to HC15xx pinmux entries:

```text
PINPAD_R05
PINPAD_R08
```

This is software-side evidence only; it does not identify physical XGO pads yet. It does, however, give a concrete register/pinmux target for correlating XGO binary initialization with eventual board probing.

Evidence:
- https://github.com/axgdev/frogqemu/blob/main/docs/SF2000.md
- https://deepwiki.com/bnister/sf2000_hcrtos/3-hardware-configuration

## Updated debug-interface hypothesis

The current best-supported chain is now:

```text
HCSEMI B210 / HC15xx SoC
  -> documented UART + serial boot/download capability
  -> SF2000 bootloader emits boot diagnostics over UART
  -> X60 physically exposes usable UART through board test pads
  -> X60 and SF2000 share loader/platform behavior despite LCD/GPIO differences
  -> XGO uses the same HC15xx/H1512 runtime family
```

Therefore:

> A UART/debug interface on XGO is now **STRONG**, not merely a generic possibility. Its physical pad location remains UNKNOWN.

The next controlled XGO hardware investigation should identify likely GND/TX/RX pads with a high-impedance instrument first, then compare observed boot traffic against the known HC15xx UART initialization. No voltage should be injected until pad function and I/O level are established.

## Matrix confidence adjustment — UART/test-pad evidence

- **SF2000:** raise to **CONFIRMED externally** for boot UART behavior.
- **X60:** **CONFIRMED externally** for physically broken-out UART and abundant test pads.
- **Q19:** remains physically inspectable but exact UART pads unresolved.
- **DY19:** still UNKNOWN.
- **XGO A10:** raise conceptual likelihood to **STRONG**, while physical pad identity remains UNKNOWN.




## 2026-09-07 continuation update — Chinese-language modding and recovery ecosystem

A dedicated Chinese-language search track has now produced a coherent modification/recovery cluster around the same power-bank handheld family.

This materially changes the research strategy: Chinese Bilibili/forum sources are not merely product reviews. They contain firmware recovery, cross-model flashing, display adaptation, system-package replacement and game-library tooling that independently overlap several XGO archaeology results.

### DY19 recovery firmware and unbrick workflow — CONFIRMED externally

Bilibili creator `Sesn` published:

```text
DY-19充电宝掌机救砖固件及软件分享
"DY-19 power-bank handheld unbrick firmware and software sharing"
```

The post explicitly says:

- no ready-made DY19 unbrick tutorial was available to the author;
- the recovery method was worked out with guidance from a more experienced expert;
- the video provides the required **software and firmware package**;
- the package was shared through Tianyi Cloud;
- another Bilibili creator, `炒鸡大帅比9961`, had produced an **optimized firmware package** for the same device family.

The same recovery post was independently mirrored/discussed on the Chinese emulator forum `bbs.xqemu.cn`, preserving the cloud package link and Bilibili video ID.

Evidence:
- https://www.bilibili.com/video/BV1Td8ceJEA8/
- https://bbs.xqemu.cn/thread-2184-1-1.html

Preserved package locator from the public post:

```text
https://cloud.189.cn/t/7V3mu2MJnUBf
access code: 9fma
```

Package contents have **not yet been recovered or hashed** in this repository. Treat the existence/provenance as confirmed external evidence; treat internal binary identity as pending.

### Independent Chinese SF2000 -> DY19 adaptation — STRONG

A separate Bilibili creator, `叶落听风者`, published:

```text
充电宝游戏机刷机sf2000（时趣DY-19）
"Flash SF2000 on a power-bank game console (Shiqu DY-19)"
```

and a follow-up:

```text
充电宝游戏机刷机sf2000（时趣DY-19）2：汉化游戏导入
"... part 2: Chinese localization / game import"
```

This is independent Chinese-side confirmation of the same architectural split already recovered from 4PDA and our binaries:

```text
common SF2000/HC15xx software base
+ DY19-specific display/input adaptation
```

The use of `时趣` (Shiqu) with DY19 is also a useful OEM/retail alias for future Chinese searches.

Evidence:
- https://www.bilibili.com/video/BV15GX7YVENt/
- Bilibili SF2000 search currently indexes the follow-up title above.

### One Chinese creator spans DY19, DY12 and generic power-bank-console customization

The creator `炒鸡大帅比9961`, already named by the DY19 recovery author as the source of an optimized DY19 firmware package, now appears repeatedly in power-bank-console modification searches.

Indexed titles include:

```text
充电宝游戏机新系统包介绍
"Power-bank game console new system package introduction"

DY-12变色翻转问题成功修复
"DY-12 color-change / flipped-display problem successfully fixed"

充电宝游戏机 自定义添加游戏工具
"Power-bank game console custom add-games tool"

什么？充电宝游戏机可以玩伏魔记？
"What? A power-bank game console can play Fumo Ji?"

充电宝游戏机怎么播放视频？
"How can the power-bank game console play video?"
```

This is important because it identifies a **cross-device modifier**, not a one-off repair post.

Current evidence supports:

- DY19 firmware optimization activity;
- DY12 display-orientation/color adaptation work;
- replacement system packaging;
- user-facing game-library modification tooling;
- expansion of software/content capabilities.

Evidence:
- https://www.bilibili.com/video/BV1jxt4ztEyy/
- Bilibili search indices for the DY12 display-fix and custom-add-games titles.

### Direct comparison with XGO archaeology

| Chinese community result | Independent XGO archaeology result | Relationship |
|---|---|---|
| DY19 unbrick firmware/software package | XGO/DY19 `bisrv.asd` recovery and boot-chain analysis | **Strong corroboration that firmware recovery/replacement is practical in-family** |
| SF2000 flashed onto Shiqu DY19 with DY19-specific follow-up | SF2000 common runtime + model-specific display/controller adaptation | **Direct independent corroboration** |
| DY12 flipped/color display fix | revision-dependent LCD init/display adaptation already inferred from DY12/X60/DY19 evidence | **Strong corroboration of panel/board-revision sensitivity** |
| new power-bank-console system package | XGO monolithic application + Resources architecture | **Potential sibling distribution package; binary recovery needed** |
| custom add-games tool | XGO stable-merge/catalog regeneration archaeology and SF2000 FROGTOOL lineage | **Potential independent validation of exact list formats; tool binary/source needed** |
| game import/localization follow-up for DY19 | XGO three-catalog filename/title/search metadata model | **Potential exact metadata-format match; not yet proven** |

### Important caution on the custom add-games tool

The title alone is **not proof** that the Chinese tool uses the exact XGO/SF2000 triplet transform we recovered.

However, the wider family already uses the known catalog files:

```text
rdbui.tax
fhcfg.nec
nethn.bvs
...
```

and SF2000/GB300 community tools such as FROGTOOL rebuild those synchronized lists.

Therefore the Chinese custom-add-games utility is now a high-value artifact target. Recovering it could answer:

1. Does it modify the same `count + offsets + NUL strings` catalogs?
2. Does it preserve existing indices or perform a full rebuild?
3. Does it generate Chinese/pinyin/search metadata or duplicate filename text?
4. Does it support DY12/DY19-specific folder mappings?
5. Does it patch `bisrv.asd` or only Resource files?
6. Does its supported-device list expose additional OEM aliases useful for XGO lineage?

### Chinese ecosystem search vocabulary now retained

Future searches should combine retail/OEM/model identifiers with activity terms:

```text
拆机 / 拆解       teardown
主板              PCB / motherboard
刷机              flash firmware
固件 / 原厂固件   firmware / factory firmware
救砖              unbrick / recovery
改机 / 改装       modification
串口 / UART       serial
调试口            debug port
测试点            test point
烧录              programming/flashing
固件提取          firmware extraction
主控              main SoC/controller
芯片型号          chip marking/model
屏幕翻转          flipped display
变色              color corruption/change
导入游戏          game import
添加游戏          add games
系统包            system package
```

High-value aliases currently include:

```text
DY-19 / DY19
时趣 DY-19
DY-12 / DY12
Q19
X60
X35
H1512
HC15xx
B210
充电宝游戏机
```

### Research priority adjustment

Add a permanent high-priority track:

> **Chinese ecosystem archaeology — firmware packages, modding tools, repair workflows, cross-model modifiers, Bilibili creators, emulator forums, Xianyu/Taobao parts trails, Baidu-image/cache trails and Chinese PCB/component identifiers.**

Immediate artifact targets:

1. recover and hash the DY19 Tianyi unbrick package;
2. recover `炒鸡大帅比9961` optimized DY19/system package;
3. recover the custom add-games tool and compare its transforms byte-for-byte with our catalog model;
4. recover the DY12 display-fix package and identify exactly which LCD init/config bytes changed;
5. search `时趣 DY-19` as a separate OEM alias for PCB photos, repair listings and factory firmware;
6. follow the people, not only the product names: creators who modify multiple HC15xx power-bank handhelds are now first-class evidence sources.


### DY19 `时趣` / Shiqu alias strengthened by retail evidence

The `时趣 DY-19` naming used by the Chinese SF2000-flashing videos is not an isolated uploader nickname.

Current Chinese-market-indexed accessory listings independently describe:

```text
DY19钢化膜
时趣掌上游戏机充电宝二合一
```

("DY19 tempered glass / Shiqu handheld game-console + power-bank 2-in-1").

This raises `时趣 / Shiqu` to a **STRONG retail/OEM search alias** for DY19. Future Chinese searches should include it even when `DY19` is omitted from the title.

Evidence:
- Chinese-market product results indexed through Shopee for `时趣 DY19`;
- Bilibili creator `叶落听风者` explicitly labels the flashed specimen `时趣 DY-19`.

Chinese retail search also continues to index Q19-class power-bank game consoles, indicating that this hardware category remains sufficiently active for recent repair/modification content to still surface rather than being purely historical.



## 2026-09-07 correction — China search must be XGO-first, not sibling-first

The Chinese-language search track is now explicitly re-centered on the physical specimen under investigation.

The target identity tuple is:

```text
brand: 芯果 / Xinguo / XGO
manufacturer: 深圳市前海芯果智能科技有限公司
model: A10
front marking: XGO PLUS+ 10000MAH
product class: 10000mAh magnetic wireless-charging game-console power bank
dimensions: approx. 141 x 67 x 20 mm
controls: analog-style digital joystick + Select/Start + six face buttons
ports/features: TF, USB-C, AV, external handle/controller interface
software: H1512 / HC15xx / ALi TDS2 family
related retail-family alias: DY10 (do not equate without PCB/package evidence)
```

Chinese searches must therefore begin with the **manufacturer, brand, exact enclosure and product characteristics**, then use DY19/DY12/Q19/X60 only as comparators.

### Chinese target vocabulary for the actual specimen

Primary identity searches:

```text
芯果 A10
芯果 A10 游戏充电宝
芯果 A10 10000毫安
芯果 A10 磁吸充电宝
芯果 游戏机 10000mAh
芯果 PLUS+ 10000MAH
XGO A10 充电宝游戏机
XGO PLUS 充电宝游戏机
前海芯果 游戏机
深圳市前海芯果智能科技 游戏机
```

Repair/modification combinations:

```text
芯果 A10 拆机 / 拆解
芯果 A10 维修
芯果 A10 刷机
芯果 A10 固件
芯果 A10 救砖
芯果 A10 改机 / 改装
芯果 A10 主板
芯果 A10 屏幕
芯果 A10 电池
芯果 A10 摇杆
芯果 A10 按键
芯果 A10 TF卡
芯果 A10 添加游戏 / 导入游戏
芯果 A10 系统包
芯果 A10 串口 / UART
芯果 A10 测试点 / 调试口
芯果 A10 SPI / 烧录
芯果 A10 H1512
芯果 A10 主控
```

Characteristic-first searches for listings/posts that omit A10:

```text
芯果 10000毫安 磁吸 无线充 游戏机
芯果 22.5W 15W 游戏充电宝
10000毫安 磁吸 游戏机 充电宝 六按键
充电宝 游戏机 磁吸无线充 TF AV 手柄接口
H1512 磁吸充电宝 游戏机
```

### Why this matters

Chinese repair/modding posts may never mention the export label `XGO A10`. They may instead use:

- the domestic brand `芯果`;
- manufacturer name `前海芯果`;
- a distributor/OEM model such as `DY10`;
- generic category `充电宝游戏机`;
- battery/power characteristics;
- a PCB silkscreen;
- the SoC family;
- or simply a photograph of the enclosure.

Therefore an exact-model search that depends on the English string `XGO A10` has poor recall.

### Existing exact-XGO Chinese anchor

The earlier ChargerLAB / 充电头网 teardown of **芯果 DY09** remains manufacturer-family evidence only. It proves that Chinese teardown media has covered Xinguo game/power-bank hardware at PCB/component level, but the photographed DY09 is visibly not the A10 and no DY09 component may be projected onto A10.

This makes ChargerLAB, the 芯果 manufacturer trail, Chinese repair posts and image-based enclosure matching especially valuable targets for the A10 search.

### Search discipline

For every newly found Chinese candidate, compare against the archived A10 specimen using:

```text
front control geometry
six-button layout
joystick position
XGO PLUS+ 10000MAH marking
transparent PCB-pattern enclosure
141 x 67 x 20 mm class
rear magnetic wireless coil
USB-C / TF / speaker edge
AV jack
external handle interface
battery/power claims
PCB silkscreen if visible
H1512/HC15xx evidence if available
```

Only after this physical match should sibling firmware similarities be used to strengthen lineage.




## 2026-09-07 continuation update — DY10 emerges as the strongest Chinese domestic identity for the exact XGO enclosure

The XGO-first Chinese search has now produced the strongest domestic identity match yet.

### Exact-enclosure Chinese retail listing explicitly calls the device DY10

A Chinese Youzan/VBEINGS retail page is titled:

```text
XGO/芯果 充电宝游戏机 10000mAh 500款游戏 DY10
游戏机充电宝 22.5W 无线磁吸 ...
```

The product photographs show the **same long transparent enclosure geometry** as the preserved XGO A10 specimen family: centered landscape screen, left joystick + Select/Start cluster, six face buttons, transparent circuit-pattern shell and the same overall proportions.

This is substantially stronger than a generic family association.

Evidence:
- https://detail.youzan.com/show/goods?alias=2xe3gpow94qpagp&from_source=gbox_seo

### Independent Chinese article also names the transparent XGO as DY10

A 什么值得买 / SMZDM article describes:

```text
芯果XGO透明游戏机充电宝
10000mAh
15W无线充
22.5W有线充
1000+款游戏
全透明外壳 / 机械朋克设计
```

and explicitly calls it:

```text
DY10游戏磁吸充电宝
```

This independently links `DY10` to the same transparent 10,000mAh XGO gaming-power-bank design.

Evidence:
- https://post.smzdm.com/p/akkv85dk/

### JD variant naming independently connects A10 and the same product family

JD currently indexes the Xinguo gaming-power-bank listing with selectable variants including:

```text
DY09绿 [5000mAh + 500 games]
A10黑  [10000mAh + ten-thousand games + magnetic power bank]
```

JD also lists a transparent-black premium XGO 10,000mAh / ten-thousand-game variant and a Marvel co-branded 10,000mAh variant.

This gives the current naming model:

```text
DY10 = strong Chinese domestic/product-family identity for the transparent 10,000mAh XGO design
A10   = strong black/premium retail variant identity for the same enclosure family
```

Do **not** yet assume every DY10 and A10 package is firmware-identical. Chinese listings show at least 500-game, 1000+-game and 10,000-game bundles in visually matching hardware, so card content and possibly firmware revision remain package-dependent.

Evidence:
- JD 芯果 product listings indexed under `A10黑`, transparent-black premium and Marvel variants
- Youzan DY10 listing
- SMZDM DY10 article

### Additional domestic-market evidence: the product was a named new Xinguo release

Bilibili's `国产游戏掌机周报 NO.64` (2023-10-15) explicitly lists:

```text
芯果发售新款游戏充电宝
"Xinguo releases a new game power bank"
```

This timestamp is consistent with the appearance of the transparent 10,000mAh generation in Chinese retail channels.

Evidence:
- https://www.bilibili.com/video/BV1Wu411T7md/

### Why this changes the Chinese search strategy

Future exact-device Chinese searches should now prioritize:

```text
芯果 DY10
XGO DY10
DY10 游戏机充电宝
DY10 磁吸游戏充电宝
DY10 透明游戏机
DY10 赛博黄
DY10 透明黑
DY10 维修 / 拆机 / 固件 / 救砖 / 刷机
DY10 添加游戏 / 导入游戏 / TF卡
DY10 主板 / 屏幕 / 摇杆 / 按键
DY10 H1512 / 串口 / 测试点 / SPI
```

while retaining `A10黑` and `芯果 A10` as parallel aliases.

### Current identity confidence

```text
Exact physical specimen:
  Xinguo / 芯果 XGO transparent 10000mAh gaming power bank

Retail/export identity:
  A10 — STRONG

Chinese domestic/product-family identity:
  DY10 — now STRONG

Firmware equivalence across all A10/DY10 bundles:
  UNKNOWN / revision-dependent until hashes are compared
```

This is the most useful Chinese identity advance from the current search pass.



## 2026-09-07 continuation update — XGO / 芯果 organizational lineage through 晶科泰 / Jncota

The XGO-first Chinese search has now recovered a manufacturer/brand-development chain that helps explain the firmware architecture already observed independently.

### Official archived XGO company material ties 芯果 directly to 晶科泰集团

An archived official XGO / 芯果 company page states that:

- **深圳市前海芯果智能科技有限公司** was established as the **brand-operation division of 晶科泰集团**;
- it was responsible for operating the 芯果 / XGO brand;
- XGO maintained product-development capability while also working in **deep cooperation with domestic and overseas solution-technology companies**;
- company marketing claimed a new-product development cycle of roughly **45–60 days**.

This is organizational evidence, not PCB authorship evidence. It does **not** prove that Jncota/XGO designed every logic board in-house.

However, it is unusually consistent with the software archaeology:

```text
common HC15xx / H1512 solution platform
+ reusable TDS2/frontend/runtime base
+ fast product-specific LCD/input/power adaptation
+ retail/model-specific Resources/card bundles
```

Evidence:
- archived official XGO page:
  https://web.archive.org/web/20180821165434/http://www.szxgo.com/zjxg/zjxgs.html

### Jncota was already a game-hardware manufacturer long before DY10/A10

An archived 晶科泰 / Jncota site from 2010 advertises game-console manufacturing, including:

- game consoles;
- 8-bit and 16-bit TV-game products;
- cartridges;
- controllers;
- game accessories;
- handheld products.

This materially changes the interpretation of the XGO product line:

> XGO is not best modeled as a generic power-bank vendor that later added an emulator. It sits inside a Shenzhen game-hardware manufacturing lineage that subsequently combined game hardware with charging/power-bank products.

Evidence:
- https://web.archive.org/web/20100323034309/http://www.jncota.com/

### The hybrid “game-console power bank” product category is documented at Jncota by 2019

A 2019 Beijing gifts/trade-show electronic catalog lists:

```text
深圳市晶科泰科技有限公司
booth 3F09
website: www.jncom.cn
product description: 游戏机充电宝
```

`游戏机充电宝` translates directly to **game-console power bank**.

This provides a dated manufacturer-level anchor for the product category several years before the transparent DY10/A10 generation surfaced in 2023-era Chinese retail material.

Evidence:
- 2019 Beijing Gifts electronic catalogue:
  https://www.giftsbeijing.com/content/dam/sitebuilder/rxch/bjgifits/download/2019Electronic-catalogue.pdf

### 2015 Chinese company history independently supports the XGO-brand timeline

Chinese business/marketing material from 2015 describes:

- 晶科泰 as an established game-console/tablet R&D and manufacturing company;
- registration/development of the 芯果 / XGO brand;
- creation of the Qianhai XGO company as the brand-promotion/operation vehicle.

Evidence:
- https://www.nsw88.com/Article/zhinengshoubiaoxinpi_1.html

### Current best organizational/product model

```text
晶科泰 / Jncota
long-running Shenzhen game-hardware manufacturer
             |
             +-- controllers / Famicom-derived and other game hardware
             |
             +-- "游戏机充电宝" product category documented by 2019
             |
             +-- 芯果 / XGO brand-operation organization
                       |
                       +-- external solution-company collaboration
                       |
                       +-- DY-series game/power-bank products
                              |
                         DY05 / DY09 / DY10-era evolution
                                      |
                            transparent 10000mAh DY10/A10 family
                                      |
                         exact XGO A10 research specimen
```

The model above is a **product/organizational lineage**, not a literal PCB genealogy.

### Engineering significance

The official description of outside `方案技术企业` ("solution technology companies") is especially important.

Chinese electronics manufacturing commonly uses `方案` to describe a reusable technical solution/reference platform that an OEM adapts into multiple retail products. Without identifying the specific solution vendor, the wording already provides a plausible organizational mechanism for the exact pattern observed across SF2000/Q19/DY19/X60/XGO:

```text
shared SoC/SDK/runtime architecture
+ differing LCD init
+ differing controller GPIO/scanner
+ differing RF/power hardware
+ product-specific bisrv.asd
+ heavily reused Resources/content structures
```

This does **not** prove that the HC15xx solution vendor was the unnamed partner in the archived XGO page. That remains an open identification target.

### New Chinese/OEM search priority

Search the manufacturer and its historical commerce footprint directly:

```text
晶科泰 DY10
晶科泰 游戏机充电宝
晶科泰 10000mAh 游戏机
晶科泰 磁吸 游戏机充电宝
晶科泰 XGO
晶科泰 H1512
晶科泰 主板 游戏机
晶科泰 固件
Jncota game power bank
Games Power DY10
前海芯果 DY10
```

Historical domains / commerce identities:

```text
jncota.com
jncom.cn
szxgo.com
shop1e98r80786960.1688.com
```

Highest-value artifacts now include:

1. historical Jncota/XGO product catalogs that identify DY10/A10 internal or OEM aliases;
2. factory/1688 product pages with PCB, replacement-card or component photographs;
3. support/download files linked from archived Jncota/XGO sites;
4. replacement TF cards for 500/1000/10000-game DY10/A10 variants;
5. broken/parts-only DY10/A10 units on Xianyu exposing board photographs;
6. any named `方案商` / solution provider attached to the product family.




## 2026-09-07 continuation update — XGO game-power-bank product evolution and DY10/A10 bundle separation

The XGO-first Chinese pass recovered a longer internal product history and stronger evidence that retail software bundles must be separated from hardware identity.

### XGO marketed numbered generations of game-console power banks by 2020

A 2020 Chinese article describes **four generations** of 芯果 game-console power banks:

- first generation: classic handheld form, 10000mAh, 299 games;
- second generation: controller-like form, 10000mAh, optional wireless charging, ~300 games;
- third generation: smaller rounded controller-like form, 5000mAh, 108 games;
- fourth generation: folding/mirror form, 5000mAh, ~400 games.

This predates DY09 and the transparent DY10/A10 generation and demonstrates that "游戏机充电宝" was an evolving XGO/Jncota product line rather than a one-off design.

Evidence:
- https://k.sina.cn/article_6404153475_17db7a08302000mc7w.html

### XGO used model families outside the DY numbering scheme

Lenovo/Lecoo historical catalog pages preserve:

```text
芯果-G16 GAMEMAX游戏机充电宝
```

in multiple colors.

This proves that domestic/internal retail naming was not consistently `DYxx`. Future searches must therefore not assume the transparent specimen has only A10/DY10 aliases.

Evidence:
- https://item.lenovo.com.cn/product/1007926.html
- https://item.lenovo.com.cn/product/1007923.html
- https://item.lenovo.com.cn/product/1007925.html

### Exact 10000mAh XGO family is sold with materially different software/card bundles

Current Chinese JD indexing shows the 10000mAh game-power-bank family in multiple content configurations, including:

- standard transparent-black / premium 10000-game bundle;
- Marvel co-branded 10000mAh version with **500 games**;
- Marvel co-branded 10000mAh version with **10000 games / arcade support**;
- controller-bundled variants of the same retail family.

This reinforces a critical evidence rule:

> enclosure/model identity, firmware identity, and TF-card/Resources content identity must be recorded separately.

A visually matching A10/DY10 is **not** sufficient to assume the same `bisrv.asd`, Resources set or game catalogs.

Evidence:
- https://www.jd.com/brand/1320a9c3f4a8c43f30ca.html
- https://www.jd.com/sptopic/670411b79248cf309c2.html

### Highest-value exact-device artifact now: alternate domestic stock TF card

A domestic **500-game 10000mAh XGO card** is potentially more valuable for software-lineage comparison than another generic sibling firmware.

Comparing it with the preserved XGO 10000-game specimen can determine whether XGO shipped:

1. identical `bisrv.asd` with different Resources/ROM content;
2. variant-specific frontend applications;
3. different catalog mappings or emulator subsets;
4. different card capacities/layouts;
5. model/revision-specific board-support binaries.

Priority acquisition/search strings:

```text
芯果 DY10 游戏卡
芯果 DY10 TF卡
DY10 500款游戏 TF卡
DY10 1000款游戏 TF卡
A10黑 游戏卡
芯果 XGO 万款游戏 内存卡
芯果 漫威联名 500游戏 TF卡
芯果 游戏机充电宝 原装卡
```

### Chinese review/owner evidence status

Current JD pages confirm a live owner base with hundreds of reviews on the exact XGO 10000mAh family, but public search indexing does not expose useful review bodies for card failures, repairs or game-import questions.

Therefore owner archaeology should move toward:

- direct marketplace review pages where accessible;
- Bilibili/Douyin exact-product comments;
- Xianyu broken-unit/parts listings;
- seller support screenshots;
- replacement-card listings;
- Chinese image search for bare boards and LCD assemblies.

Do not infer failure modes from review counts alone.



## 2026-09-07 continuation update — exact A10 OEM/rebrand and independent catalog evidence

The XGO-first Chinese/OEM search has now produced three unusually strong exact-device anchors.

### MechZone A10 is a STRONG exact-hardware rebrand candidate

Multiple export-market sources sell a `MechZone A10` with the same unusually specific hardware fingerprint as the preserved XGO A10 specimen:

```text
model                 A10
dimensions            141 x 67 x 20 mm
nominal battery       10000mAh
rated capacity        5800mAh / 37Wh
wired output          22.5W
wireless charging     15W
controls              joystick + six face buttons
content claim         10 emulators / 10000+ games
video output          supported
```

Published product photography is visually consistent with the same transparent landscape enclosure.

This should be treated as a **rebrand/OEM identity**, not proof of firmware equality.

Evidence:
- https://www.notebookcheck.com/Mechzone-A10-Gaming-Handheld-ist-gleichzeitig-eine-Powerbank-und-unterstuetzt-drahtlose-Ladung.881770.0.html
- https://www.tvboxaustralia.com.au/product/mechzone-a10-fast-handheld-charging-game-machine-power-bank-22-5w-37wh-10000mah-built-in-10000-games-external-battery-power-supply-gaming-console/
- https://couponsfromchina.com/mechzone-a10-charging-game-console-power-bank-22-5w-37wh-10000mah/

Engineering value:

> A MechZone A10 stock TF card or `bisrv.asd` is now a high-value exact-board comparison artifact. If hashes differ, it may expose another factory bundle or board-support revision of the same enclosure.

### Original mainland wholesale offer recovered: 1688 offer 754381935521

A Taiwanese Ruten mirror of the product contains Alibaba-hosted `cbu01.alicdn.com` images and a factory-style description. Searching an exact sentence from that listing recovers the originating 1688 product ID through a public 1688 mirror:

```text
1688 offer ID: 754381935521
canonical form:
https://detail.1688.com/offer/754381935521.html
```

The copied supplier text states:

- factory-direct 8/16/32-bit game consoles;
- OEM customization;
- bulk shipment;
- main export markets in Southeast Asia;
- exact A10 platform specifications;
- selectable configuration `A10（无卡无游戏）` — **A10 with no card / no games**.

The product-detail imagery is definitive for the exact enclosure. It visibly carries:

```text
XGO PLUS+ 10000MAH
```

and gives:

```text
model             A10
battery           10000mAh
rated             5800mAh 37Wh
wireless          MAX 15W
games             10000
size              67 x 141 x 20 mm
Type-C input      5V=3.1A | 9V=2.22A | 12V=1.67A
Type-C output     5V=2A   | 9V=2.22A | 12V=1.67A
battery type      polymer
```

Evidence:
- 1688 mirror index:
  https://1688.ru/product/754381935521
- live copied retail page with Alibaba image assets:
  https://www.ruten.com.tw/item/22631283549308/
- original image CDN objects are under `cbu01.alicdn.com` and encode Alibaba seller/image object ID `2213313290698`.

### Significance of `A10（无卡无游戏）`

This is the strongest external evidence yet that the **A10 hardware is sold independently of its TF-card/game bundle**.

That independently corroborates the architecture recovered from the preserved specimen:

```text
A10 hardware
  + boot/platform firmware
  + removable TF card
      + bisrv.asd / Resources
      + catalogs
      + ROM payload
```

Do not infer that a no-card unit is usable without provisioning. The listing only proves a bare hardware SKU exists.

### Independently published A10 game list maps directly onto XGO stock resources

A 221-page Scribd document titled `A10 Gam..st` publishes categorized English filenames and Chinese titles for an A10 game set.

The document is not merely generically similar. Distinctive sequences match the preserved XGO catalogs directly.

#### GBC byte/order-level sequence match

The public A10 document begins its GBC section with the same ordering found in XGO `Resources/pnpui.tax`, including distinctive filenames such as:

```text
10-Pin Bowling.zgb
4x4 World Trophy.zgb
720 Degrees.zgb
A Bug's Life.zgb
Action Man - Search for Base X.zgb
...
ARK OF THE WOLVES Colour 2003 (Cn).zgb
...
Atelier Elie- Salberg no Renkinjutsushi (Cn).zgb
...
Austin Powers - Oh, Behave!.zgb
Azure Dreams (Cn).zgb
...
Bakuhashi Senki Metal Walker - Kkoute No Yuujyou (Cn).zgb
...
Billy Bob's Huntin' 'n' Fishin'.zgb
BioHazard 3 - last escape (Cn).zgb
```

The preserved XGO GBC filename catalog:

```text
pnpui.tax = 958 entries
```

contains these unusual strings in the same sequence.

#### Other system starts also map directly

Public A10 sections align with the preserved XGO catalog organization:

```text
FC   -> rdbui.tax
SFC  -> urefs.tax
MD   -> scksp.tax
GB   -> vdsdc.tax
GBC  -> pnpui.tax
GBA  -> vfnet.tax
```

The A10 Arcade sections also reproduce the same curated CPS1/CPS2/NeoGeo-family title organization seen in the XGO resources.

Evidence:
- https://www.scribd.com/document/881855797/A10-Gam-st

### Important divergence: the public A10 catalog exposes entries missing from our preserved FC list

The public A10 FC section begins exactly like the preserved XGO list through the Contra, Adventure Island, Double Dragon, HotBlood and Mega Man groups, but then includes:

```text
Donkey Kong
Donkey Kong JR
Donkey Kong 3
Bomber Man 1
Bomber Man 2
```

before continuing into Ninja Turtles / Ninja Gaiden / 1942 / 1943 / 1945.

Our preserved XGO `rdbui.tax` has 744 entries and at that point contains:

```text
Mega Man 6
Bomber Man 1
Ninja Turtles 1
...
```

The three Donkey Kong entries and `Bomber Man 2` are absent from that catalog.

Crucially, earlier independent game-list archaeology already proved that the user's stock card physically contains:

```text
D:\FC\Bomber Man 2.zfc
```

even though it is omitted from `rdbui.tax`.

Therefore the public A10 list is likely evidence of a **different factory catalog/content revision**, not merely a transcription of our exact card.

This is highly significant:

> At least one A10 content bundle appears to expose a game that physically exists but is hidden by the preserved specimen's catalog.

That independently supports the stable-merge scanner work and shows that OEM catalog variants can differ even within the exact A10 product line.

### Updated exact-device artifact priority

1. **Recover 1688 offer 754381935521 supplier identity and original shop page.**
2. **Locate a stock card from the no-card/500-game/alternate A10 bundle family.**
3. **Locate a MechZone A10 TF card or firmware.**
4. **Preserve/download the published A10 game-list document if provenance permits and compare every system list programmatically.**
5. **Search the alternate A10 catalog for all entries absent from the preserved XGO catalogs and check whether those ROMs physically exist on the user's card.**
6. **Use those differences as historical evidence for OEM catalog-generation behavior.**



## 2026-09-07 continuation update — alternate A10 catalog counts validated against the preserved physical card

The independently published 221-page A10 game-list document can now be counted reliably after accounting for its inconsistent Scribd rendering.

Important correction:

- FC and SFC are rendered as English filename + Chinese title on the same line.
- MD, GB, GBC and GBA are rendered as an English filename block followed by a separate Chinese-title block marked `&H2`..`&H5`.

Therefore raw section-line counts would double-count several systems. The corrected alternate-A10 catalog counts are:

| System | Published alternate A10 list | Preserved XGO filename catalog | Difference |
|---|---:|---:|---:|
| FC | **868** | 744 | **+124** |
| SFC | **1167** | 929 | **+238** |
| MD | **912** | 788 | **+124** |
| GB | **1142** | 885 | **+257** |
| GBC | **1112** | 958 | **+154** |
| GBA | **762** | 626 | **+136** |
| **Total** | **5963** | **4930** | **+1033** |

These counts come directly from the document's block boundaries:

```text
FC   lines 436..1303
SFC  lines 1305..2471
MD   English 2473..3384; Chinese mirror begins &H2 at 3385
GB   English 4299..5440; Chinese mirror begins &H3 at 5441
GBC  English 6585..7696; Chinese mirror begins &H4 at 7697
GBA  English 8811..9572; Chinese mirror begins &H5 at 9573
```

Source:
- https://www.scribd.com/document/881855797/A10-Gam-st

### Comparison with the preserved XGO card's physical ROM payload

The archived original-card file inventory independently contains:

| Folder | Physical files on preserved card | Visible XGO catalog | Physical minus visible |
|---|---:|---:|---:|
| FC | 773 | 744 | **29** |
| SFC | 1080 | 929 | **151** |
| MD | 834 | 788 | **46** |
| GB | 976 | 885 | **91** |
| GBC | 974 | 958 | **16** |
| GBA | 1149 | 626 | **523** |

This is an important three-layer result:

```text
retail A10/DY10 hardware identity
        !=
physical ROM payload on TF card
        !=
visible synchronized game catalogs
```

The alternate published A10 list is also **not** simply "our physical ROM directories fully indexed":

- for FC/SFC/MD/GB/GBC, the alternate list is larger than both our visible catalog and, in several cases, our physical folder payload;
- for GBA, our preserved card physically contains far more files (1149) than either our visible catalog (626) or the alternate A10 list (762).

Therefore at least two materially different A10/DY10 content assemblies existed, and neither can be modeled as merely "same ROM set, different menu count."

### Strong concrete example remains Bomber Man 2

The alternate A10 FC list exposes `Bomber Man 2`.

The preserved XGO card physically contains:

```text
D:\FC\Bomber Man 2.zfc
```

but the stock 744-entry XGO FC filename catalog omits it.

This is now a proven instance where:

```text
alternate A10 catalog = visible
preserved XGO physical card = present
preserved XGO catalog = hidden
```

That gives the alternate A10 list direct engineering value for the on-device refresh/stable-merge project.

### New high-value comparison task

Recover the source spreadsheet/text behind the 221-page public document and classify each alternate-A10 entry into:

```text
A. visible in preserved XGO catalog
B. absent from catalog but physically present on preserved XGO card
C. absent from both catalog and preserved physical card
D. present on preserved card/catalog but absent from alternate A10 list
```

Class B is especially valuable: it can reveal OEM-intended entries that our particular factory catalog revision accidentally or deliberately hid.

Do not interpret the retail "10000 games" claim as a literal catalog count from this document. The validated six-system portion totals 5963 before its curated Arcade sections, and marketing totals may count bundle variants or other content differently.
