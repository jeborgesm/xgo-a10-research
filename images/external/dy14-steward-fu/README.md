# DY14 external comparator corpus — Steward Fu

Source repository: `a18project/steward-fu`, branch `gh-pages`  
Source site: https://steward-fu.github.io/website/  
Captured: 2026-09-07

## Scope

This directory preserves **19 third-party research images** for the DY14 H1512 game/power-bank handheld:

- `teardown-01.jpg` through `teardown-17.jpg`
- `spi-dump-01.jpg` and `spi-dump-02.jpg`

The files were copied byte-for-byte from the public Steward Fu GitHub repository. Because Git blob SHA-1 is content-addressed, each archived image has the **same Git blob SHA as the upstream source**, providing a direct integrity/provenance check.

## Why DY14 matters

DY14 is not the XGO A10 enclosure, but it is a direct **Hichip H1512** platform comparator with a published teardown and SPI-dump procedure. That makes this corpus far more relevant to A10 low-level archaeology than a generic Xinguo product-family teardown.

Steward Fu reports:

- Hichip H1512 @ 800 MHz
- 128 MB RAM
- 512 KB SPI flash
- 3.5-inch 320x240 display
- microSD
- external gamepad support
- 3.7 V 8000 mAh battery

The teardown identifies:

- Nanya `NT5TU64M16DG-AD` 1-Gbit DDR2 SDRAM (128 MiB)
- `UC25HD40` 4-Mbit / 512-KB SPI NOR
- `IP5306` power-bank management IC
- `XB4908`
- two `8002A` audio amplifiers
- several deliberately/physically unmarked or marking-removed ICs

The SPI dump contains strings:

`H1512--0.1.0`  
`h1512_gpio_pinmux_sel`

The latter independently occurs in the preserved XGO A10 application image.

## Image map

- 01–06: enclosure/external angles and ports
- 07–09: opened enclosure, battery and internal layout
- 10–12: PCB/control/front-shell construction
- 13–15: LCD/FPC details
- 16–17: PCB/component views; image 17 is the key annotated/readable component view
- SPI 01–02: physical SPI-flash connection and dump setup

## Evidence discipline

DY14 proves platform/SDK kinship, not exact A10 board equivalence. Component reuse is plausible but must be verified on A10 hardware before being asserted.

Copyright remains with the original photographer/publisher. These copies are preserved strictly as research/reference evidence with source provenance.
