# XGO A10 / XGO Plus Research

Reverse engineering and documentation of the **XGO A10 / XGO Plus** handheld game console and 10,000 mAh power bank.

The device appears to belong to the **Data Frog SF2000 software/platform lineage**, but uses substantially different physical hardware. This repository documents what is known, what is inferred, and what still needs to be tested.

> **Status:** active research. Treat hypotheses as hypotheses. Do not flash SF2000 firmware onto an XGO based only on platform similarity.

## Why this repository exists

Public technical information about the XGO A10 / XGO Plus is extremely limited. Investigation of a working unit and its original microSD card revealed strong structural similarities to the SF2000 ecosystem, including the firmware container, resource naming, emulator cores, ROM databases, and Player 2 support.

The goals are to preserve reproducible findings, map the SF2000 relationship, understand the ports (especially the external controller / "Handle Interface"), document safe experiments, and investigate whether SF2000 community software can eventually be adapted to the XGO.

## Current headline findings

| Finding | Confidence |
| --- | --- |
| The microSD card is required for the tested XGO Plus to boot | **Confirmed on tested unit** |
| Card is a single FAT32 volume containing `bios`, `Resources`, ROM-system folders, etc. | **Confirmed** |
| Main firmware file is `bios/bisrv.asd` | **Strong evidence** |
| XGO `bisrv.asd` uses the SF2000-family `LCFG` firmware format | **Confirmed** |
| XGO resources and ROM databases use SF2000 filenames/formats | **Confirmed** |
| Firmware contains SF2000-era/libretro emulator code | **Confirmed by binary strings** |
| Firmware contains explicit Player 2 configuration | **Confirmed by binary strings** |
| Firmware contains USB attach/detach and filesystem handling strings | **Confirmed by binary strings** |
| Product-family documentation labels the mystery controller connector as `Handle Interface` | **Strong external evidence** |
| A generic GP2040-CE USB controller works as Player 2 | **No — tested and not working** |
| The Handle Interface necessarily implements standard USB HID | **Unknown** |
| Stock SF2000 firmware is safe to run on XGO hardware | **Unknown / do not assume** |

## Repository map

- [`docs/hardware.md`](docs/hardware.md) — known hardware and ports
- [`docs/firmware.md`](docs/firmware.md) — SD layout and firmware evidence
- [`docs/sf2000-lineage.md`](docs/sf2000-lineage.md) — evidence connecting XGO to SF2000
- [`docs/controller-research.md`](docs/controller-research.md) — Player 2 and Handle Interface investigation
- [`docs/experiments.md`](docs/experiments.md) — experiments performed on the physical unit
- [`docs/research-log.md`](docs/research-log.md) — chronological research notes
- [`findings/firmware-hashes.md`](findings/firmware-hashes.md) — hashes and specimen metadata

## Evidence labels

- **Confirmed** — directly observed in the physical device/card or reproducible binary evidence.
- **Strong evidence** — multiple independent observations point to the conclusion.
- **Hypothesis** — plausible explanation requiring further testing.
- **Unknown** — not established.

## Firmware preservation and copyright

This repository does **not** publish the original full SD image, commercial ROM collections, copyrighted BIOS archives, or the proprietary `bisrv.asd` firmware image. Instead, it records hashes, filenames, offsets, observations, tools, and eventually reproducible analysis/patching methods.

Keep an untouched raw image of your own working card before experimenting.

## Related projects

- [vonmillhausen/sf2000](https://github.com/vonmillhausen/sf2000)
- [axgdev/FrogQEMU](https://github.com/axgdev/frogqemu)
- [axgdev/UniFrog](https://github.com/axgdev/UniFrog)
- [madcock/sf2000_multicore](https://github.com/madcock/sf2000_multicore)
- [EricGoldsteinNz/tadpole](https://github.com/EricGoldsteinNz/tadpole)
- [tzlion/frogtool](https://github.com/tzlion/frogtool)

The XGO should currently be treated as a **related but distinct hardware target**.
