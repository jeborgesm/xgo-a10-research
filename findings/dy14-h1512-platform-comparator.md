# DY14 as an H1512 Platform Comparator

Status: **external platform-lineage evidence; controller-protocol equivalence not yet established**.

## Why DY14 matters

The DY14 is a physically different handheld/game-power-bank product, but public reverse-engineering material from Steward Fu provides direct evidence that it belongs to the same H1512 SoC/SDK ecosystem seen in the XGO firmware.

Steward Fu's SPI-dump notes show the following strings in the DY14 flash image:

```text
H1512--0.1.0
h1512_gpio_pinmux_sel
```

The preserved XGO `bios/bisrv.asd` independently contains:

```text
h1512_gpio_pinmux_sel
```

This makes DY14 a useful comparator for low-level GPIO, display, controller, and boot/storage research even though the enclosure, PCB layout, and product design differ substantially.

## External-controller relevance

Public DY14 product/manual material describes dedicated external `Handle` / gamepad ports and multiplayer support. That feature overlap is interesting because the XGO also exposes a connector marketed as a `Handle Interface` while its firmware contains a two-channel synchronous serial controller scanner.

At present, however, this is only architectural/product-family context. No DY14 controller-task disassembly or connector pinout has yet been obtained that can be compared directly against the XGO B15/L0/B7 serial scanner.

## What is confirmed

- A publicly dumped DY14 SPI image identifies itself with `H1512--0.1.0`.
- The DY14 dump contains `h1512_gpio_pinmux_sel`.
- The XGO `bisrv.asd` also contains `h1512_gpio_pinmux_sel`.
- DY14 is marketed/documented with external handle/gamepad connectivity.
- DY14 is therefore a legitimate H1512-era comparison target for XGO reverse engineering.

## What is not yet established

- that DY14 and XGO use the same application firmware;
- that DY14 uses the same B15/L0/B7 GPIO assignment;
- that DY14 external controllers use the same 12-bit active-low synchronous serial protocol;
- that DY14 controllers are electrically compatible with the XGO Handle Interface;
- that either device is a simple stock-SF2000 hardware derivative.

## Highest-value next step

Obtain or locate a DY14 application/firmware dump that includes the controller task, then search for the XGO scanner signature:

```text
B15 data input
L0  data input
B7  shared clock
host drives both data lines low for load/reset
~4 us load delay
12 parallel active-low samples
~2 us clock-low delay
```

A matching routine would materially strengthen the case for a reusable H1512 accessory-controller protocol and could point toward a real compatible controller source. A non-matching routine would still be useful by showing how much of this behavior is board/vendor-specific.

## Evidence source

- Steward Fu, DY14 `Dump SPI` research page (`handheld/dy14_dump_spi.htm`), showing the two H1512 strings from `spi.bin`.
- Preserved XGO `bios/bisrv.asd`, locally examined specimen already documented in this repository.

## Confidence

**CONFIRMED:** DY14 is an H1512 platform comparator.

**STRONG RELEVANCE:** DY14 is worth examining for external-controller implementation because it combines the same SoC family with marketed external handle support.

**UNKNOWN:** protocol/electrical compatibility with the XGO Handle Interface.


## 2026-09-07 deeper teardown recovery

The public Steward Fu repository was inspected directly rather than relying only on indexed search snippets. This produced a materially stronger DY14 comparator.

### Exact published platform specification

Steward Fu's DY14 specification page identifies:

```text
CPU      Hichip H1512 800MHz
MEMORY   RAM 128MB
         Flash 512KB
DISPLAY  3.5" 320x240
INPUT    GamePad
SLOT     MicroSD
PORT     MicroUSB x2
         USB-C
         3.5mm jack
BATTERY  3.7V 8000mA
```

This is direct evidence of an H1512 implementation with **128 MiB RAM and the same 512-KB SPI-boot-flash capacity class used by SF2000-family systems**.

### Teardown component identities

The published teardown explicitly identifies:

- two `8002A` audio amplifiers;
- Nanya `NT5TU64M16DG-AD`;
- `UC25HD40`;
- `IP5306`;
- `XB4908`;
- several ICs whose markings have been removed/obscured.

The Nanya part is a **1-Gbit DDR2 SDRAM organized 64M x16**, therefore 128 MiB, independently agreeing with the published DY14 RAM specification.

The UC25HD40 is a **4-Mbit SPI NOR**, i.e. 512 KiB, independently agreeing with the published flash specification.

### SPI boot evidence

Steward Fu provides an actual physical SPI-dump wiring/setup and reports these strings from `spi.bin`:

```text
H1512--0.1.0
h1512_gpio_pinmux_sel
```

This is stronger than a retail similarity. DY14 demonstrably boots through the same H1512 platform/SDK vocabulary found in XGO.

### Complete image corpus archived

The complete public DY14 teardown image sequence plus the two SPI-dump setup photographs has now been preserved byte-for-byte under:

`images/external/dy14-steward-fu/`

19 images total.

The copied images retain the exact upstream Git blob SHA values, proving byte-for-byte identity with their public source.

### New priority

DY14 is now one of the **highest-value hardware comparators in the entire project**.

A future A10 PCB photograph should explicitly test for:

1. H1512 package/board location;
2. DDR2 part and organization;
3. 4-Mbit SPI NOR identity;
4. IP5306 or another power-bank SoC;
5. 8002A-family audio amplifiers;
6. common PCB layout motifs or FPC/display wiring;
7. external-controller connector routing.

A match in the compute-side RAM/SPI topology would materially narrow the A10 board ancestry. A match only in power components would instead indicate commodity power-bank reuse.
