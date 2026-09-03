# XGO A10 / XGO Plus Research

Reverse engineering, preservation, and experimental software work for the **XGO A10 / XGO Plus** handheld game console and 10,000 mAh power bank.

The XGO is an **SF2000-derived HC15xx/MIPS platform**, but it is not simply an SF2000 in a different shell. This repository started as firmware and hardware archaeology and has now reached a much more important milestone: **custom native code and an external libretro emulator core have been loaded and executed successfully on real XGO hardware.**

> **Current status (September 2026): external NES/FCEUmm gameplay is hardware-confirmed.** The next phase is turning the NES proof into a reusable XGO libretro runtime and proving it with a second core.

> Do **not** flash stock SF2000 firmware onto an XGO based only on platform similarity. The XGO remains a distinct hardware/firmware target.

## Why this repository exists

Public technical information about the XGO A10 / XGO Plus is extremely limited. Investigation of a working unit and its original microSD card revealed substantial SF2000 ancestry in the firmware container, resources, ROM databases, emulator/frontend architecture, and controller subsystem.

The project therefore has two related purposes:

1. **Archaeology and preservation** — document the original machine, firmware, interfaces, addresses, formats, behavior, and provenance with reproducible evidence.
2. **Experimental development** — use that understanding to safely execute custom software and external libretro cores while preserving as much of the stock XGO frontend and hardware support as possible.

The second goal is no longer hypothetical.

## Major milestone: external native NES core running on hardware

The XGO now successfully launches and plays an NES ROM through an **external FCEUmm libretro core** stored on the SD card rather than through the firmware's embedded NES emulator.

Hardware-confirmed path:

```text
stock XGO NES menu
  -> stock ROM preload
  -> patched NES launch call
  -> injected loader @ 0x80001500
  -> /cores/fceumm/core.xgc
  -> external core loaded @ 0x87000000
  -> XGO native frontend
  -> external FCEUmm
  -> stock XGO video/audio/input services through GP-safe bridges
```

Contra has been confirmed to load and play normally with working controls, audio, video, and apparently normal timing. The remaining visible difference in the first successful build is somewhat darker/more-muted output than the stock NES emulator; that is being treated as a shared video-path research item rather than evidence that external execution is incomplete.

The proof was developed and hardware-bisected in PR #7 and merged into `main` at commit:

```text
30f1c852ee1a094baa4b72506f745b57737e642b
```

The successful FCEUmm full-path source lineage includes the controller-lifecycle fix at `8f62bcb...` and the hardware-tested Stage-0 build from `04ee153...`.

See:

- [`findings/external-nes-proof-handoff.md`](findings/external-nes-proof-handoff.md)
- [`findings/hardware-test-first-successful-external-fceumm-gameplay.md`](findings/hardware-test-first-successful-external-fceumm-gameplay.md)
- [`findings/hardware-test-stage6-controller-preload-null-deref.md`](findings/hardware-test-stage6-controller-preload-null-deref.md)
- [`findings/xgo-bidirectional-gp-abi.md`](findings/xgo-bidirectional-gp-abi.md)

## Yes — the custom code is preserved

The hardware-tested work is **source-controlled in this repository**, not just represented by generated binaries or chat notes. Git history also preserves the intermediate diagnostic experiments and failed hypotheses that led to the working implementation.

The main custom implementation currently lives under:

[`tools/multicore/native_nes/`](tools/multicore/native_nes/)

Important preserved pieces include:

| File | Purpose |
| --- | --- |
| `xgo_nes_loader.c` | Injected stock-firmware loader; validates and loads the external XGOC payload from SD |
| `xgo_core_entry.s` | True external-core entry veneer; establishes the external MIPS `$gp` and safely returns to stock context |
| `xgo_gp_bridges.s` | Bidirectional stock ↔ external `$gp` ABI veneers for firmware services and libretro callbacks |
| `xgo_nes_native_frontend.c` | XGO-specific libretro/FCEUmm frontend and stock-runner integration |
| `xgo_minimal_environment_shim.c` | Controlled libretro environment bridge; prevents unsafe raw stock callback leakage |
| `xgo_newlib_syscalls.c` | Runtime/newlib syscall integration with XGO firmware services |
| `xgo_core.ld` | External-core memory/link layout |
| `xgo_external_stock_services.ld` | Stock firmware service symbol definitions used by the external runtime |
| `build_native_nes_asd.py` | Reproducible firmware patch/build helper |
| `pack_core_elf.sh` | Packages linked external core payloads into the XGOC container |
| `stage_native_nes_test.py` | Hardware-test staging helper |

The directory also intentionally preserves continuity probes, return ladders, transactional probes, diagnostic frontends, and other bring-up code. Those are useful archaeological evidence: they document not merely the final answer, but **how we proved where execution succeeded or failed**.

GitHub Actions workflows preserve the reproducible build/audit machinery, including loader preflight, GP ABI audits, FCEUmm link/runtime closure checks, entry/return continuity tests, and the staged hardware-bisection builds.

Generated `.xgc` hardware-test artifacts are build products; the important part is that the source, linker contracts, packaging tools, workflows, hashes, and hardware findings needed to reproduce them are preserved in Git.

## What the external-core work taught us

Several discoveries were essential to making native external execution work:

- XGO's stock firmware and an external MIPS ELF have **different `$gp` contexts**. Calls must bridge `$gp` in both directions.
- Stock callbacks such as video, audio, input, environment, filesystem services, and timing routines depend on stock GP-relative state.
- The stock `run_emulator()` can drive external libretro function pointers, provided calls back into the external core restore its GP first.
- MIPS O32 ABI details matter; for example, the 64-bit `fs_lseek` offset changes where the fifth argument lives.
- A synthetic ELF wrapper around raw firmware introduced a `+0x30` address bias. Runtime addresses must be normalized against `fw_start` rather than copied blindly from wrapper PCs.
- FCEUmm's `RETRO_DEVICE_AUTO` equals `RETRO_DEVICE_JOYPAD`; calling its controller setter before `retro_load_game()` dereferences `GameInfo` before it exists. Hardware return-ladder testing isolated this as the final launch freeze.
- Diagnostic mechanisms can perturb the machine. Behavior-based entry/return probes proved substantially safer than trying to log or draw through not-yet-initialized stock subsystems.

These are now platform knowledge, not disposable NES-specific debugging notes.

## Current development branch: generic libretro runtime

Active work continues in:

```text
research-generic-libretro-runtime
```

with draft PR #8.

The goal is to separate the reusable XGO runtime from the FCEUmm proof and then validate that abstraction with **SNES as Core #2**.

Current sequence:

1. formalize the generic input/mapping contract;
2. separate core-neutral loader, GP, environment, runtime, and frontend services from NES/FCEUmm assumptions;
3. implement generic libretro serialization for the stock save-state UI;
4. characterize the shared RGB565 brightness/black-level behavior;
5. integrate and hardware-test an external SNES core.

### Input is already more generic than expected

The stock XGO input callback exposes all 16 standard libretro joypad IDs on both controller ports. The `.kmp` compiler can map the six remappable physical action/shoulder controls to any of those IDs, including hidden `L2`, `R2`, `L3`, and `R3` targets that the stock UI never exposes.

For normal SNES controls, the hardware/firmware already provides the required D-pad, Select, Start, A/B/X/Y, and L/R namespace. The current direction is therefore to preserve and formalize the stock mapping layer rather than replace it.

See [`findings/generic-runtime-input-contract.md`](findings/generic-runtime-input-contract.md) and [`findings/hidden-libretro-input-targets.md`](findings/hidden-libretro-input-targets.md).

## Other confirmed headline findings

| Finding | Confidence |
| --- | --- |
| microSD card is required for the tested XGO Plus to boot | **Confirmed on tested unit** |
| Card is a single FAT32 volume containing `bios`, `Resources`, ROM-system folders, etc. | **Confirmed** |
| Main firmware file is `bios/bisrv.asd` | **Confirmed for preserved specimen** |
| `bisrv.asd` uses the SF2000-family `LCFG` firmware format | **Confirmed** |
| XGO resources and ROM databases use SF2000-family filenames/formats | **Confirmed** |
| Stock firmware contains a libretro-style emulator frontend | **Confirmed from executable behavior** |
| Two independent controller streams feed libretro ports 0 and 1 | **Confirmed end-to-end** |
| GPIO B15 is Player 1 DATA and GPIO L0 is Player 2 DATA | **Confirmed in firmware** |
| GPIO B7 is the shared serialized-controller clock | **Confirmed in firmware** |
| Product-family documentation labels the external controller connector `Handle Interface` | **Strong external evidence** |
| Generic GP2040-CE USB controller works as Player 2 | **No — tested and not working** |
| Handle Interface necessarily implements standard USB HID | **No evidence / do not assume** |
| Custom external native code can execute and return on XGO | **Confirmed on hardware** |
| External FCEUmm can run a real NES game using stock XGO services | **Confirmed on hardware** |
| Stock SF2000 firmware is safe to run on XGO hardware | **Unknown / do not assume** |

## Hidden controller diagnostic

From the normal XGO menu, press **L + SELECT** simultaneously to launch the built-in Super Famicom controller diagnostic stored as `Resources/Test.zsf`.

This shortcut is confirmed both by static firmware analysis and physical reproduction. The firmware checks for the exact translated input value `0x1001` (`L` + `SELECT`) and branches directly to the `Test.zsf` launcher.

See [`findings/hidden-controller-test-trigger.md`](findings/hidden-controller-test-trigger.md).

## Repository map

- [`docs/hardware.md`](docs/hardware.md) — known hardware and ports
- [`docs/firmware.md`](docs/firmware.md) — SD layout and firmware evidence
- [`docs/sf2000-lineage.md`](docs/sf2000-lineage.md) — evidence connecting XGO to SF2000
- [`docs/controller-research.md`](docs/controller-research.md) — Player 2 and Handle Interface investigation
- [`docs/experiments.md`](docs/experiments.md) — experiments performed on the physical unit
- [`docs/research-log.md`](docs/research-log.md) — chronological research notes
- [`findings/`](findings/) — evidence-backed focused conclusions and hardware-test records
- [`tools/multicore/`](tools/multicore/) — external-core research, runtime, patching, and diagnostic source code
- [`.github/workflows/`](.github/workflows/) — reproducible static audits and build/test artifact generation

## Preservation philosophy

This repository deliberately keeps more than a polished final implementation.

Reverse engineering benefits from preserving:

- original specimen hashes and offsets;
- raw observations separately from interpretations;
- failed experiments when they establish a boundary;
- diagnostic source used to prove those boundaries;
- exact upstream revisions and toolchains;
- build workflows and generated-artifact hashes;
- corrections when a prior interpretation is disproved;
- hardware observations, because hardware outranks static assumptions.

In other words: **copies of copies are a feature.** Future work should prefer adding a clearly identified replacement or superseding finding over silently erasing useful archaeological context.

## Evidence labels

- **Confirmed** — directly observed on the physical device/card or established by reproducible executable/binary evidence.
- **Strong evidence** — multiple independent observations point to the conclusion.
- **Hypothesis** — plausible explanation requiring further testing.
- **Unknown** — not established.

## Firmware preservation and copyright

This repository does **not** publish the original full SD image, commercial ROM collections, copyrighted BIOS archives, or the proprietary stock `bisrv.asd` firmware image. Instead, it preserves hashes, filenames, offsets, observations, custom source code, linker/runtime contracts, diagnostic tools, and reproducible patch/build methods.

Keep an untouched raw image of a known-working card before experimenting. Prefer testing on a clone.

## Related projects

- [vonmillhausen/sf2000](https://github.com/vonmillhausen/sf2000)
- [axgdev/FrogQEMU](https://github.com/axgdev/FrogQEMU)
- [axgdev/UniFrog](https://github.com/axgdev/UniFrog)
- [madcock/sf2000_multicore](https://github.com/madcock/sf2000_multicore)
- [EricGoldsteinNz/tadpole](https://github.com/EricGoldsteinNz/tadpole)
- [tzlion/frogtool](https://github.com/tzlion/frogtool)

These projects are invaluable lineage and comparison sources, but the XGO should be treated as a **related, independently verified target** rather than assumed binary-compatible hardware.
