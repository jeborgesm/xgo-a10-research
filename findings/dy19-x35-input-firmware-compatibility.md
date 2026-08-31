# DY19 / PGP AIO X35 Input-Firmware Compatibility Evidence

Status: **strong comparative evidence**.

## Summary

Community reports around DY19 and PGP AIO Union X35/X60-family handhelds show a recurring failure mode when swapping related SF2000-family firmware:

- the device can boot;
- display output may work, sometimes mirrored or otherwise electrically mismatched;
- background music may play;
- **controls do not respond**;
- in some cases pressing any key causes the frontend to freeze or stop audio;
- restoring or replacing the correct device-specific BIOS/`bisrv.asd` restores control operation.

This behavior is highly relevant to the XGO reconstruction because static analysis of the XGO firmware already shows board-specific GPIO controller scanning implemented directly inside `bisrv.asd`.

## DY19 reports

The 4PDA DY19 discussion records several relevant observations:

1. A user installed a firmware build that booted but left menu controls non-functional. The user later reported that the problem was solved by **replacing the BIOS**.
2. Another owner reported that stock SF2000 firmware booted with a mirrored image and music, but **did not respond to buttons**.
3. A later report states that after recovering card data the DY19 booted and played music, but **pressing any key caused the system to freeze / stop music**.
4. Another DY19 owner reported that a firmware image from the thread worked and **controls also worked**, while plain SF2000 firmware booted but had no controls.

These observations strongly imply that shared SF2000-family filesystem/resources do not imply shared input hardware configuration.

## PGP AIO Union X35 / X60 comparator

The same 4PDA discussion notes that PGP AIO Union X35 firmware is visually/software similar to DY19 but not byte-identical. A user reported the same broad symptom on both devices: stock SF2000 firmware displayed output and played music, but **buttons did not work**.

An older SF2000 thread also distinguishes the X35 from the X60 at hardware level, with a community reverse engineer noting that X35 uses a different Actions SoC while X60 belongs to the 'frog' family. This reinforces that superficially shared UI/card structure can span multiple board variants.

## Why this matters for XGO

The XGO controller path is already reconstructed from firmware:

- B15 = serial data channel 0;
- L0 = serial data channel 1;
- B7 = shared clock;
- firmware temporarily drives both data lines low for the load/reset phase;
- then samples 12 active-low button bits from each stream;
- this scanner runs persistently in the controller task.

Therefore a firmware built for another PCB can plausibly:

- read the wrong GPIO bank/pin;
- reconfigure an unrelated signal as input/output;
- drive a board signal low during the controller load phase;
- miss the real button bus entirely;
- or corrupt another peripheral whenever a button scan runs.

The community symptom 'boots, music works, controls fail' is exactly what would be expected from a frontend/emulator build that is broadly compatible while its board-specific controller GPIO implementation is not.

The more severe 'press any key -> freeze / music stops' behavior is also consistent with input-task execution triggering incompatible board control logic, although this remains an inference until the affected firmware is disassembled.

## Confidence

### CONFIRMED EXTERNALLY

- DY19 owners have reported firmware swaps where display/audio still function but controls do not.
- At least one DY19 report says replacing the BIOS restored control operation.
- Stock SF2000 firmware has been reported to boot on related DY19/X35-family devices while buttons remain non-functional.

### STRONG INFERENCE

- controller GPIO/pinmux code is one of the device-specific portions of `bisrv.asd` across this hardware family;
- correct device-specific `bisrv.asd` is required even when the higher-level SF2000-derived frontend/resources are compatible;
- XGO's B15/L0/B7 scanner should be compared against DY19 firmware before assuming accessory compatibility.

### NOT YET CONFIRMED

- whether stock DY19 uses B15/L0/B7;
- whether DY19 and XGO use the same 12-bit serial controller protocol;
- whether the reported freeze-on-button symptom is caused specifically by GPIO contention rather than another input-path incompatibility;
- whether PGP AIO Union X35, X60, DY19 and XGO share one PCB lineage or only software ancestry.

## Research consequence

Firmware compatibility across this family must be evaluated by subsystem rather than by successful boot alone.

A useful compatibility matrix is:

1. bootloader format;
2. display initialization;
3. audio initialization;
4. input GPIO scanner;
5. RF / external-controller implementation;
6. power/battery GPIO and ADC paths;
7. filesystem/resource layout.

The immediate target remains obtaining a stock DY19 `bisrv.asd` and performing a function-level comparison against XGO's controller task.

## External sources

- 4PDA DY19 discussion: `https://4pda.to/forum/index.php?showtopic=1090810`
- 4PDA SF2000 discussion: `https://4pda.to/forum/index.php?showtopic=1067862`
- Handhelds Wiki DY19 page, including stock firmware reference: `https://handhelds.wiki/DY19_Power_Bank_and_Game_Console`
