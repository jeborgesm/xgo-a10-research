# XGO A10 / XGO Plus Research

Reverse engineering and documentation of the **XGO A10 / XGO Plus** handheld game console and 10,000 mAh power bank.

The device belongs to the **Data Frog SF2000 software/firmware lineage**, but uses substantially different physical hardware. This repository documents what is known, what is inferred, and what still needs to be tested.

> **Status:** active research. Treat hypotheses as hypotheses. Do not flash SF2000 firmware onto an XGO based only on software similarity.

## Why this repository exists

Public technical information about the XGO A10 / XGO Plus is extremely limited. Investigation of a working unit and its original microSD card revealed structural and now commit-level similarities to the SF2000 ecosystem, including the firmware container, resource naming, emulator cores, ROM databases, save-state architecture, and Player 2 support.

The goals are to preserve reproducible findings, map the SF2000 relationship, understand the ports (especially the external controller / "Handle Interface"), document safe experiments, and investigate whether SF2000 community software can eventually be adapted to the XGO.

## Current headline findings

| Finding | Confidence |
| --- | --- |
| The microSD card is required for the tested XGO Plus to boot | **Confirmed on tested unit** |
| Card is a single FAT32 volume containing `bios`, `Resources`, ROM-system folders, etc. | **Confirmed** |
| Main firmware file is `bios/bisrv.asd` | **Confirmed** |
| XGO `bisrv.asd` uses the SF2000-family `LCFG` firmware format | **Confirmed** |
| XGO resources and ROM databases use SF2000 filenames/formats | **Confirmed** |
| Firmware statically links the same six identifiable emulator revisions documented for SF2000 | **Confirmed** |
| Five embedded cores retain exact upstream Git commit IDs; Snes9x retains the matching v1.36 interface fingerprint | **Confirmed** |
| The stock frontend services only three libretro core-option keys, all tied to NTSC/PAL | **Confirmed** |
| Firmware contains explicit Player 2 configuration | **Confirmed** |
| XGO Player 2 uses a GPIO synchronous serial bus related to the SF2000 keypad path, not USB HID | **Confirmed by static analysis and bench tests** |
| A generic GP2040-CE USB controller works as Player 2 | **No — tested and not working** |
| Stock SF2000 firmware is safe to run on XGO hardware | **Unknown / do not assume** |

## Repository map

- [`docs/hardware.md`](docs/hardware.md) — known hardware and ports
- [`docs/firmware.md`](docs/firmware.md) — SD layout and firmware evidence
- [`docs/sf2000-lineage.md`](docs/sf2000-lineage.md) — evidence connecting XGO to SF2000
- [`docs/controller-research.md`](docs/controller-research.md) — Player 2 and Handle Interface investigation
- [`docs/experiments.md`](docs/experiments.md) — experiments performed on the physical unit
- [`docs/research-log.md`](docs/research-log.md) — chronological research notes
- [`findings/software-architecture-and-keymaps.md`](findings/software-architecture-and-keymaps.md) — frontend architecture, native system IDs, and `.kmp` format
- [`findings/emulator-runtime-and-libretro-environment.md`](findings/emulator-runtime-and-libretro-environment.md) — exact embedded core revisions and the restricted core-option contract
- [`findings/save-state-and-core-dispatch.md`](findings/save-state-and-core-dispatch.md) — core dispatch, `.saN` bundle, thumbnails, and `.skp` auto-states
- [`findings/audio-sample-width-and-rate-normalization.md`](findings/audio-sample-width-and-rate-normalization.md) — final audio transport/sample format
- [`findings/wired-player2-protocol-family-comparison.md`](findings/wired-player2-protocol-family-comparison.md) — XGO/SF2000/NES/SNES Player 2 bus comparison
- [`findings/firmware-hashes.md`](findings/firmware-hashes.md) — hashes and specimen metadata

## Evidence labels

- **Confirmed** — directly observed in the physical device/card or reproducible binary evidence.
- **Strong evidence** — multiple independent observations point to the conclusion.
- **Hypothesis** — plausible explanation requiring further testing.
- **Unknown** — not established.

## Firmware preservation and copyright

This repository does **not** publish the original full SD image, commercial ROM collections, copyrighted BIOS archives, or the proprietary `bisrv.asd` firmware image. Instead, it records hashes, filenames, offsets, observations, tools, and reproducible analysis/patching methods.

Keep an untouched raw image of your own working card before experimenting.

## Related projects

- [vonmillhausen/sf2000](https://github.com/vonmillhausen/sf2000)
- [pt13762104/sf2000](https://github.com/pt13762104/sf2000)
- [axgdev/FrogQEMU](https://github.com/axgdev/frogqemu)
- [axgdev/UniFrog](https://github.com/axgdev/UniFrog)
- [madcock/sf2000_multicore](https://github.com/madcock/sf2000_multicore)
- [EricGoldsteinNz/tadpole](https://github.com/EricGoldsteinNz/tadpole)
- [tzlion/frogtool](https://github.com/tzlion/frogtool)

The XGO should be treated as a **software-relative but distinct hardware target**.
