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
| Product class | handheld | handheld + power bank | game/power-bank family | game/power-bank family | handheld + power bank | handheld + power bank | handheld + magnetic power bank; physical specimen label **CONFIRMS model A10** |
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
| UART/test-pad evidence | community documented | PCB should be inspected for candidate pads | UNKNOWN | UNKNOWN | teardown/SPI test access documented | UNKNOWN | high-value future hardware target |

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


## 2026-09-07 XGO-first Chinese archaeology continuation

Research priority is now explicitly **exact physical XGO specimen first**. DY19, DY12, Q19, X60, and SF2000 remain comparators and are not primary search keys.

### Exact domestic A10 identity strengthened — STRONG

Current JD indexing exposes the exact 芯果 product family with a selectable variant:

```text
A10黑〖10000mAh+万款游戏+磁吸充电宝〗
```

The same indexed family also exposes the 10000mAh XGO Marvel 500-game, dual-controller + 500-game, and 10,000-game variants. This strengthens **A10 as a Chinese domestic sales identity for the exact XGO 10000mAh family**, not merely an export/rebrand label.

Evidence class: retail/catalog identity. This is **not** yet PCB, firmware-hash, or TF-card equivalence proof.

Sources:
- JD indexed product-family pages, retrieved 2026-09-07.
- Existing exact 1688 source-art evidence for offer `754381935521`.

### TF-card modularity / seller-support search model — PARTIAL but useful

Current 芯果 retail indexing for other handheld SKUs explicitly includes a no-card variant described as:

```text
无内存卡 ... 需自备卡下载游戏
```

Combined with the exact A10 1688 variant:

```text
A10（无卡无游戏）
```

this supports a practical search hypothesis: seller-side **replacement game cards, copied cards, card-download bundles, and after-sales recovery packages** may circulate independently from the hardware.

This does **not** prove that an exact A10/DY10 stock image has been recovered. It changes search priority toward:
- 原装游戏卡 / 原装TF卡
- 补卡 / 配卡 / 换卡
- 卡丢失 / 卡坏
- 游戏卡下载 / 卡包
- 售后发卡 / 售后资料
- A10 无卡无游戏 paired with seller support material

### Manuals+ / AliExpress-derived A10 pages — CORROBORATIVE ONLY

A current Manuals+ page generated from an AliExpress item labels an exact-fingerprint device:

```text
Xinguo XGO A10
141 × 67 × 20 mm
10000mAh
5800mAh / 37Wh
22.5W wired
15W wireless
TF card package-dependent
```

A separate derived A10 page uses the Royaldraid brand and explicitly describes a 32GB TF card with 5000+ games; another uses Pogopirate.

These pages are **not accepted as OEM manuals or firmware evidence** because they appear to be synthesized retail/manual mirrors. They are useful only as:
- rebrand-name leads;
- evidence that card/no-card packaging was represented in export listings;
- image/title fingerprints to trace back to original sellers.

Do not equate Royaldraid/Pogopirate/MechZone/XGO firmware without card-image or binary comparison.

### Rejected noise reinforced

Generic searches on `10000mAh / 37Wh / 5800mAh / 15W / 22.5W` return many ordinary power banks. Those specifications alone are not identifying evidence. Exact-enclosure/control geometry, card layout, PCB, source artwork, or binary evidence is required.


### Exact 10000mAh XGO content-tier split expanded — STRONG retail evidence

A preserved JD category page exposes multiple selectable SKUs within the same exact XGO 10000mAh product family:

```text
巴萨蓝 [1万毫安 + 1000款游戏 + 无线…]
漫威联名款 [1万毫安 + 500款游戏 + …]
至尊版透明黑 [1万毫安 + 万款游戏 …]
A10黑 [10000mAh + 万款游戏 + 磁吸充电宝]
```

The same page separately lists the Marvel:
- 500-game base version;
- dual-controller + 10,000-game premium version;
- 10,000-game premium version.

This expands the already-confirmed factory bundle split. The exact 10000mAh enclosure family was sold with at least **500-, 1000-, and 10,000-game content configurations** in Chinese retail indexing.

Implication: an authenticated 500- or 1000-game card is not expected to be content-identical to the preserved 10,000-game specimen, even if the enclosure and base hardware match. Comparison should be performed at:
- `bisrv.asd` hash/size;
- `Resources` hashes;
- catalog files;
- emulator/system selection;
- physical ROM set.

Evidence class: **STRONG retail/catalog evidence**, not yet firmware-hash equivalence.

### Exact-owner/video leads — PARTIAL

Bilibili indexing contains exact-product short videos, including:
- `芯果 XGO 磁吸充电宝游戏机！1万毫安 + 万款街机游戏…`
- `芯果XGO游戏机充电宝MagSafe无线磁吸…22.5W快充掌机…`

These are useful account-level/search-graph leads for owner questions, TF-card replacement, and after-sales material. No exact teardown, firmware package, or card image has yet been recovered from these indexed clips.

### Exact specialist-reseller lead — PARTIAL

Vietnamese retro-handheld specialist Game Tâm An indexes an `XGO A10` with the exact unusual emulator set:
```text
FC / SFC / GBA / GBC / GB / Megadrive
IGS / CPS1 / CPS2 / NEOGEO
```
and the 10000mAh / 22.5W product identity.

This is not OEM evidence and does not prove firmware equivalence. It is retained as a potentially useful surviving-stock / replacement-card lead because the seller specializes in retro handhelds rather than generic electronics.


### Second exact Alibaba asset-owner namespace recovered — STRONG

Visual-fingerprint tracing of the exact XGO PLUS+ 10000MAH enclosure recovered a coherent nine-image upstream Alibaba-style artwork set mirrored by Wekome India.

All nine images carry the same Alibaba/Taobao asset-owner namespace:

```text
2209861332013
```

Example original-style filename:

```text
O1CN01q7ezfT1Qk0AL2P3zU__2209861332013-0-cib
```

The artwork set is exact-product evidence rather than specification-only similarity. It includes:
- the exact transparent landscape XGO PLUS+ 10000MAH enclosure;
- 141 × 67 × 20 mm dimensional artwork;
- 10000mAh / 22.5W / 15W marketing artwork;
- joystick/control closeups;
- wireless-charge imagery;
- AV/external-display usage imagery.

This namespace is distinct from the previously recovered exact-source namespace:

```text
2213313290698
```

Interpretation:
- **STRONG:** a second Alibaba source/seller account distributed the exact XGO artwork/product family.
- **UNKNOWN:** the legal company/supplier identity behind `2209861332013`.
- **NOT PROVEN:** that `2209861332013` and `2213313290698` are the same supplier, factory, or organization.
- Wekome is retained only as an exact retail mirror that preserved the upstream filenames; it is not treated as the OEM.

This provides a new supplier-tracing key independent of model-name search.

### Live official XGO Douyin enterprise-shop path — CONFIRMED corporate path / exact A10 PARTIAL

A current Douyin related-video graph identifies an uploader/account as:

```text
深圳市前海芯果智能科技有限公司企业店
```

This matches the independently established XGO brand-operation organization.

The account is therefore a high-value current Chinese-platform path for:
- seller after-sales material;
- replacement TF-card support;
- archived product clips;
- owner questions/comments;
- repair or recovery instructions.

Current indexed results around the account include 芯果 游戏机充电宝 material and 10000mAh product-family content, but an exact A10/DY10 firmware/card/teardown post has **not yet** been authenticated.

Do not interpret a mixed Douyin topic page titled `芯果游戏机充电宝怎么刷机` as proof that exact A10 flashing firmware is publicly available; visible indexed results include other XGO models.

### Rejected synthesized A10 manual mismatch

A current third-party generated “ZUIDID A10” manual/listing was rejected as an exact-XGO source because its dimensions/display/platform claims conflict materially with the authenticated XGO/A10 physical fingerprint. It is retained as naming noise only.


### MechZone A10 original Banggood SKU recovered — STRONG provenance key

A surviving coupon/price-tracker outbound link preserves the now-dead original Banggood product URL for the exact MechZone A10:

```text
MechZone-A10-Fast-Handheld-Charging-Game-Machine-Power-Bank-22_5W-37Wh-10000mAh-Built-in-10000+-Games-External-Battery-Power-Supply-Gaming-Console-p-2017036.html
?ID=6287830
&cur_warehouse=CN
```

Recovered identifiers:

```text
Banggood product ID: 2017036
Banggood option/variant ID: 6287830
warehouse: CN
```

Contemporary product mirrors reproduce the exact physical/spec fingerprint:
- model A10;
- 67 × 141 × 20 mm;
- 10000mAh nominal;
- 5800mAh / 37Wh rated;
- 22.5W wired;
- 15W wireless;
- 10000+ games.

The preserved package-description mirror lists the A10, Type-C cable, and user manual but does not separately enumerate a TF card. This is **not sufficient** to conclude that no TF card was supplied because a preinstalled card may have been treated as part of the device.

The numerical Banggood IDs are retained as high-value archival/search keys for:
- Wayback/cache recovery;
- old buyer reviews/questions;
- CDN/image mirrors;
- reseller databases;
- surviving stock.

No authenticated MechZone TF-card image or `bisrv.asd` has yet been recovered.

### Exact JD transparent-black seller/item pair recovered — STRONG retail provenance

The exact transparent-black 10000mAh/10000-game XGO SKU is directly exposed at:

```text
JD item: 10101813502820
seller: 鲸零数码专营店
variant wording: 至尊版透明黑〖1万毫安+万款游戏+磁吸充电宝〗
```

The item is categorized by JD as a 芯果 游戏机充电宝 product and currently has a substantial review corpus indexed at the category level.

Why this matters:
- it provides a concrete Chinese seller attached to an exact physical/content SKU;
- seller after-sales is a plausible location for replacement-card/recovery material;
- the product/item ID is an exact search key for archived reviews, owner complaints, and mirrors.

Current indexed searches did **not** expose a public TF-card replacement package or seller support download from 鲸零数码专营店. Keep the seller as an after-sales lead; do not infer card contents without direct evidence.


### Shenzhen Moka / 墨咔 1688 supply-chain lead — PARTIAL, exact A10 bridge not yet proven

A corporate/contact pivot produced a potentially important current wholesale lead:

```text
深圳市墨咔科技有限公司
1688 shop: szmkkj.1688.com
landline: 0755-27929877
```

Two independent indexed wholesale mirrors associate 深圳市墨咔科技有限公司 with that landline and game-hardware sales. One current indexed snapshot also exposes a product title for a `DY09私模游戏机充电宝磁吸无线快充便携移动电源`.

The landline is notable because `0755-27929877` is also independently documented for:
- 深圳市前海芯果智能科技有限公司 historical corporate profiles;
- 深圳市晶科泰科技有限公司 / Jncota factory/contact profiles.

This creates a **PARTIAL organizational/supply-chain relationship clue** around the same unusual game-console/power-bank category.

Evidence discipline:
- **NOT PROVEN:** 深圳市墨咔科技有限公司 manufactured or sold the exact A10/DY10 specimen.
- **NOT PROVEN:** `szmkkj.1688.com` is the seller behind exact 1688 offer `754381935521`.
- **NOT PROVEN:** either Alibaba media-owner namespace `2213313290698` or `2209861332013` belongs to 墨咔.
- Exact searches combining 墨咔 / `szmkkj` with A10, DY10, offer `754381935521`, and both image-owner IDs did not produce an indexed exact-enclosure bridge.

Why retain the lead:
- the shared landline is independently reproduced across XGO/Jncota and the current game-hardware wholesale identity;
- 墨咔 currently occupies the same specialized game-hardware / game-power-bank sales channel;
- the 1688 shop handle is a concrete source to inspect for historical listings, archived media, replacement cards, and after-sales material.

Promote confidence only if an exact A10/DY10 enclosure, card package, offer ID, image-owner ID, PCB, or firmware artifact is tied directly to this shop/company.


### Physical specimen rear label confirms A10 — CONFIRMED

Reinspection of the preserved exact-device photographs resolves the rear regulatory/specification label sufficiently to read:

```text
Model number: A10
Rated capacity: 5800mAh
Battery capacity: 10000mAh
Wireless charge max: 15W
Battery: Polymer lithium-ion battery
MADE IN CHINA
```

The label also carries the expected multi-voltage Type-C input/output ratings.

This is **direct physical-specimen evidence**. A10 is therefore no longer merely a retail/OEM/rebrand inference for this unit: the exact XGO specimen itself is labeled A10.

The transparent rear window additionally exposes a distinct power/wireless-board topology:
- large copper Qi coil;
- segmented circular magnetic ring;
- two square controller ICs;
- large shielded inductor;
- visible `ESD` silkscreen/test marking.

These physical features are useful future image-search/teardown fingerprints. Component identities are not inferred from the photograph alone.

### Exact A10 32GB / 10,000-game TF-card configuration — STRONG

A surviving 2024 Shopee Malaysia listing for the exact physical XGO PLUS+ A10 enclosure preserves a nine-image Chinese marketing set.

Within the same coherent exact-device image set:
- the hero calls it `10000mAh 移动游戏电源` and advertises `无线磁吸 / 万款游戏 / 22.5W`;
- another image says `内置10000款经典游戏，10大游戏模拟器于一身`;
- a bundle image shows the exact XGO PLUS+ device next to a TF card explicitly marked `32GB` with `Free Games`;
- the retail box is labeled `GAME POWER BANK`, `22.5W`, and `10000mAh`.

Evidence level: **STRONG exact retail/card-bundle evidence**.

What this establishes:
- an exact A10 10,000-game configuration was sold with a 32GB TF card;
- `32G / 32GB` is now a high-value exact-device search term for stock-card recovery.

What it does **not** establish:
- that every A10/DY10/XGO 10,000-game unit used 32GB;
- that the preserved user's card has the same capacity;
- that the 32GB card's `bisrv.asd`, Resources, catalogs, ROM set, or emulator selection match the preserved specimen.

New high-value search keys:
```text
A10 32G 游戏卡
A10 32GB 原装卡
A10 32G TF卡
A10 游戏磁吸充电宝 32G
10000mAh 移动游戏电源 32G
GAME POWER BANK A10 32GB
```


### Alternate A10 / Smartberry-Royaldraid-Pogopirate branch — HOLD SEPARATE

A Southeast-Asian/export search seam exposes several products sold under `A10` and brands including Smartberry, Royaldraid, and Pogopirate. Indexed descriptions commonly cluster around:
- 32GB TF card;
- ~5000 games;
- 20W wired charging;
- dimensions around 14.2 × 6.6 × 2.5 cm.

These values materially differ from the **confirmed physical XGO specimen**:
- 141 × 67 × 20 mm;
- 22.5W wired;
- 15W wireless;
- 10000mAh / 5800mAh rated;
- exact XGO PLUS+ enclosure;
- physical rear label `Model number: A10`.

Therefore this export branch is **not merged into the exact XGO A10 lineage**. It may represent:
1. a related A10 shell/revision;
2. seller-generated inaccurate specifications;
3. a repack/rebrand with a different card/content tier;
4. unrelated A10 naming collision.

Promotion requires exact enclosure imagery plus one of: matching rear label, exact 141×67×20 dimensions/22.5W ratings, card/binary comparison, or PCB evidence.

This is also a warning that `A10 + 32GB` alone is not a sufficient exact-device search key.


### 2023 crowdfunding card capacity converges with exact A10 retail bundle — STRONG continuity clue

The exact A10 32GB retail-card evidence now converges with an **independent earlier XGO launch-generation source** already preserved in `findings/xgo-dy10-a10-direct-lineage.md`:

The 2023 XGO crowdfunding campaign advertised:
- 10000mAh;
- 15W magnetic wireless charging;
- 22.5W wired charging;
- TV output;
- 10 emulator families;
- **32GB TF card**;
- 6000+ games.

The later exact A10 marketplace image set independently shows:
- the same XGO PLUS+ physical enclosure;
- 10000mAh / 22.5W / 15W;
- 10 emulator families / 10,000 games;
- **32GB TF card**.

This is stronger than either source alone. It supports continuity of a **32GB removable-card provisioning model from the 2023 XGO/DY10 launch generation into the later A10-branded exact enclosure**.

It still does not prove identical `bisrv.asd` or Resources. The game-count change (6000+ -> 10000) is consistent with card/catalog-content evolution and must be tested by binary/card comparison.

High-value target is now specifically:
```text
XGO DY10 32GB original TF image
XGO crowdfunding 32GB card backup
A10 32GB original TF image
```


### Search-direction refinement: return to mainland China using confirmed A10 — 2026-09-07

The physical specimen now directly confirms `Model number: A10`. Search priority is therefore tightened again around **A10 as the primary Chinese/OEM identifier**, with DY10/XGO used as supporting aliases rather than the starting point.

Primary mainland search strings:
```text
A10 游戏机充电宝
A10 游戏磁吸充电宝
A10 移动游戏电源
A10 10000毫安 游戏机
A10 10000mAh 移动游戏电源
A10 32G 游戏卡
A10 32GB 原装卡
A10 原装TF卡
A10 游戏卡 备份
A10 游戏卡 镜像
A10 补卡
A10 换卡
A10 扩容
A10 卡坏
A10 无卡无游戏
A10 系统包
A10 固件
A10 刷机
A10 拆机
A10 主板
A10 维修
A10 花屏
A10 白屏
A10 H1512
```

Disambiguation rule: reject generic A10 products and the mismatched 20W/~142×66×25 mm/5000-game export branch unless exact XGO PLUS+ enclosure, 141×67×20 dimensions, 22.5W/15W ratings, card/binary evidence, or PCB evidence establishes a relationship.

Highest-value Chinese targets:
1. original 32GB A10 game card / copied-card image;
2. `A10（无卡无游戏）` seller after-sales provisioning;
3. broken/parts A10 listings exposing PCB/FPC;
4. Chinese owner videos/comments showing TF-card contents;
5. original 1688/Taobao listing ancestry and seller identity.
