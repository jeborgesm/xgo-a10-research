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

