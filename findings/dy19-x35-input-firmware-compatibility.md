# DY19 / Q19 / PGP AIO X35 Input-Firmware Compatibility Evidence

Status: **strong comparative evidence**.

## Summary

Community reports around DY19 and related Q19 / PGP AIO Union X35-family handhelds show a recurring failure mode when swapping related SF2000-family firmware:

- the device can boot;
- display output may work, sometimes mirrored or otherwise electrically mismatched;
- background music may play;
- **controls do not respond**;
- on Q19/X35-family units, pressing a key after an incompatible bootloader/firmware combination has also been reported to freeze the frontend or stop audio;
- restoring or replacing the correct device-specific BIOS/`bisrv.asd` can restore control operation.

This behavior is highly relevant to the XGO reconstruction because static analysis of the XGO firmware already shows board-specific GPIO controller scanning implemented directly inside `bisrv.asd`.

## DY19 reports

The 4PDA DY19 discussion records several relevant observations:

1. A DY19 owner with a Pinduoduo unit installed the firmware from the thread. It booted but menu controls were non-functional. The owner later reported that the problem was solved by **replacing the BIOS**.
2. A June 2026 DY19 owner reported that plain SF2000 firmware booted but **controls did not work**. The firmware linked in the DY19 thread then booted and **controls worked**.
3. The thread's 2024 multicore procedure explicitly requires replacing the BIOS for DY19, and the author separately reported difficulty remapping the controls.

These are direct DY19 observations and strongly imply that shared SF2000-family filesystem/resources do not imply shared input hardware configuration.

## Q19 / PGP AIO Union X35 comparator

A separate contributor in the DY19 thread explicitly identifies their device as **Q19, not DY19**, and later also tests a PGP AIO Union X35. These reports must not be attributed to DY19 itself.

The contributor reported:

- Q19/X35 firmware is similar to the DY19/SF2000 family but not identical;
- stock SF2000 firmware booted on both Q19 and X35 with mirrored video and music but **no button response**;
- after bootloader/firmware experiments, recovered original images could boot and play music, but pressing a key caused an apparent freeze/music stop;
- a `bios.rar` attachment posted in that sequence belongs to the contributor's **Q19-related recovery investigation**, not a confirmed DY19 BIOS archive.

This remains useful sibling evidence but is now kept distinct from direct DY19 evidence.

An older SF2000 discussion also warns that X35/X60 naming is inconsistent across products and that superficially similar devices can use different SoCs. Model labels therefore cannot establish PCB identity by themselves.

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

The recurring symptom `boots, music works, controls fail` is exactly what would be expected from a frontend/emulator build that is broadly compatible while its board-specific controller GPIO implementation is not.

The more severe `press key -> freeze / music stops` symptom remains a Q19/X35-family observation and is only consistent with, not proof of, input-task GPIO incompatibility.

## Additional firmware-recovery evidence

The DY19 thread preserves several potentially valuable firmware artifacts:

- `DY19 TF card files.torrent` (74.75 KB), attached June 2024;
- `multicore_DY19.zip` (~4.4 MB), referenced from the SF2000 thread as a DY19 BIOS replacement for multicore;
- `dy19_13menu.rar` (92.93 MB), a later modified DY19 firmware package;
- a stock firmware image linked from the thread and independently referenced by Handhelds Wiki.

A September 2025 owner states that the nominal ~30 GB original Chinese image contains only about **40 MB of actual files**, principally BIOS and directory layout. In June 2026 another owner confirms that the firmware linked in the thread still boots a DY19 with working controls. This makes recovery of the device-specific `bisrv.asd` a realistic target even though the distributed disk image is nominally large.

## Confidence

### CONFIRMED EXTERNALLY

- DY19 owners have reported firmware swaps where the system boots but controls do not.
- At least one direct DY19 report says replacing the BIOS restored control operation.
- A June 2026 direct DY19 report says SF2000 firmware booted without controls while the DY19 thread firmware booted with controls.
- Q19/X35-family units independently show the same broader `boot/display/audio but no input` compatibility pattern under stock SF2000 firmware.
- The `bios.rar` posted by Wild Hornet is associated with the Q19 recovery case, not proven stock DY19 firmware.

### STRONG INFERENCE

- controller GPIO/pinmux code is one of the device-specific portions of `bisrv.asd` across this hardware family;
- correct device-specific `bisrv.asd` is required even when the higher-level SF2000-derived frontend/resources are compatible;
- XGO's B15/L0/B7 scanner should be compared against genuine DY19 firmware before assuming accessory compatibility.

### NOT YET CONFIRMED

- whether stock DY19 uses B15/L0/B7;
- whether DY19 and XGO use the same 12-bit serial controller protocol;
- whether the Q19/X35 freeze-on-button symptom is caused specifically by GPIO contention rather than another input-path incompatibility;
- whether Q19, PGP AIO Union X35/X60, DY19 and XGO share one PCB lineage or only software ancestry.

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

The immediate target remains obtaining a genuine DY19 `bisrv.asd` and performing a function-level comparison against XGO's controller task. The small actual payload of the stock disk image and the existence of `multicore_DY19.zip` make those higher-value targets than the Q19 `bios.rar` attachment.

## External sources

- 4PDA DY19 discussion: `https://4pda.to/forum/index.php?showtopic=1090810`
- 4PDA SF2000 discussion: `https://4pda.to/forum/index.php?showtopic=1067862`
- Handhelds Wiki DY19 page, including stock firmware reference: `https://handhelds.wiki/DY19_Power_Bank_and_Game_Console`
