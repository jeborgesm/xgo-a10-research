# XGO vs SF2000 1.71 — Build Fingerprint and Layout Comparison

Status: **new binary-comparison evidence**.

## Exact embedded SDK/libcore build fingerprint

The preserved XGO `bios/bisrv.asd` contains this exact build string:

```text
Libcore version 3.6.1.1@SDK3.AB_20210616(gcc version 3.4.4 mipssde-6.06.01-20070420)(Administrator@ 2021年07月15日 17:08:57)
```

The same exact string has independently been reported from official Data Frog SF2000 firmware 1.71, together with the same emulator-core/version strings that occur in XGO (`TGB Dual v0.8.3 9be31d3`, gpSP `v0.91 261b2db`, Snes9x 2005 `v1.36`, PicoDrive `1.91 cbc93b6`, and the same FBA option strings).

This is substantially stronger lineage evidence than a shared filename or resource format. XGO and stock SF2000 firmware were built around the same HC15xx vendor SDK/libcore generation and carry the same inherited emulator payload fingerprints.

It does **not** mean the complete application firmware is identical.

## Firmware size differs materially

```text
XGO bisrv.asd             12,768,452 bytes
stock SF2000 1.71         12,624,628 bytes
XGO excess                   143,824 bytes
```

The stock SF2000 1.71 size and CRC32 (`33B9FB14`) are published with the preserved vanilla firmware release. XGO has a different size and previously recorded hash, so it is not merely stock 1.71 with renamed SD resources.

## Stock firmware-signature landmarks shifted in XGO

Von Millhausen's SF2000 firmware checker identifies several stable stock-firmware landmarks. Searching the XGO image for those same byte/string anchors gives:

```text
landmark                         stock vicinity     XGO offset
button-map preamble              ~0x8D6200          0x8DDC34
bad_exception / boot-logo block  ~0x9B3520          0x9BB090
SNES tuning preamble             ~0xC0A170          0xC2D400
```

The XGO therefore preserves multiple deep structural landmarks from the stock SF2000 image while moving them because the application image has diverged.

The stock battery/power-curve search signature used by the public firmware checker:

```text
11 05 00 02 24
```

is not present in the XGO image. This is consistent with the already reconstructed XGO-specific battery ADC / power-level implementation rather than evidence against lineage.

## Interpretation

The evidence now supports a more precise software-family model:

```text
HC15xx vendor SDK/libcore + inherited emulator payloads
                    |
                    +-- stock Data Frog SF2000 application line
                    |
                    +-- XGO/OEM application fork
                         - larger application image
                         - different controller GPIO/RF behavior
                         - different power/battery path
                         - expanded/repeated Arcade menu configuration
                         - renamed resources/persistent files
                         - retained but altered SF2000 structural landmarks
```

This is stronger than describing XGO merely as "SF2000-like". It is an application-level fork built from the same underlying vendor software generation, with hardware-specific and frontend-specific divergence layered around inherited core code/data.

## External corroboration

A 2025 SF2000 community firmware analysis posted the exact same libcore/compiler timestamp from official SF2000 1.71. The same community documentation attributes the official SF2000 frontend to Shenzhen biikoo Co., Ltd.; that attribution is useful provenance context but should remain community-sourced unless independently corroborated.

## Confidence

### CONFIRMED from binary / preserved release metadata

- XGO contains the exact `Libcore version 3.6.1.1@SDK3.AB_20210616` build/compiler timestamp also observed in SF2000 1.71.
- XGO contains the same major emulator version fingerprints.
- XGO `bisrv.asd` is 143,824 bytes larger than stock SF2000 1.71.
- multiple stock SF2000 firmware-checker landmarks are present at shifted offsets in XGO.
- the stock SF2000 power-curve signature used by the public checker is absent from XGO.

### STRONG EVIDENCE

- XGO is a genuine application fork of the same HC15xx vendor software generation used by SF2000, not simply a device that happens to understand SF2000 resource formats.
- substantial divergence occurs in hardware-facing/application code while large inherited emulator/data regions remain recognizable.

### NEXT HIGH-VALUE COMPARISON

Obtain a stock SF2000 1.71 `bisrv.asd` locally and perform block-level similarity / function-level diffing against XGO. This should separate inherited byte-identical regions from XGO-specific insertions and replacements and may expose the exact boundaries of the OEM hardware adaptation layer.
