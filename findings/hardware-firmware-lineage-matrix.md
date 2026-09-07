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
| Stock firmware/card | **CONFIRMED** widely preserved | no authenticated stock image recovered yet; SF2000-derived/adapted firmware use **CONFIRMED externally** | partial/community-related | DY19-compatible by owner report | stock card/application target not recovered | **CONFIRMED** owner-originated full SD image selectively extracted | **CONFIRMED** original card/application preserved |
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
