# Family-wide arcade emulator research — external replacement decision

Date: 2026-09-05

## Research question

Before continuing per-ROM debugging of the XGO external CPS1 experiments, determine what actually works on closely related HC15xx/SF2000/GB300 firmware families.

## External evidence

### SF2000 Multicore

The current SF2000 Multicore release explicitly states:

> the only stock emulator without a better multicore option is the Arcade section

This is highly significant because the same project has successfully replaced stock emulators for NES, SNES, GB/GBC, GBA and others, but not arcade.

### SF2000 stock arcade

Independent SF2000 reverse engineering identifies the stock arcade emulator as a customised Final Burn Alpha close to v0.2.96.86, with a later libretro interface and vendor modifications.

This stock FBA is known to handle CPS1/CPS2/Neo Geo reasonably well for the class of hardware.

### GB300 v2

GB300 v2 uses the same family of stock FBA arcade implementation. Family documentation reports that stock FBA knows how to load roughly 1431 sets.

GB300 Multicore also ships MAME2000, but family documentation explicitly reports that MAME2000 performance is much worse than stock FBA on GB300 v2 and SF2000.

This independently matches our XGO hardware result:

- MAME2000 boots and plays
- but is slower than stock

### Other multicore forks

GB300 Multicore and DY19-family multicore forks inherit the same general core ecosystem. Their arcade option remains MAME2000 for multicore, not a demonstrated faster FBA replacement.

No evidence was found of a sibling firmware successfully replacing the stock arcade FBA with FBA2012/FBNeo/MAME while improving CPS1 performance.

## XGO evidence aligns with family evidence

Our XGO hardware results:

- Stock XGO CPS1: functional and generally fastest, though some games can lag.
- FBA2012/Musashi: ROM/content handoff works; stalls at first-frame execution.
- MAME2000: fully boots and plays; slower than stock.
- FBA2012/native-MIPS A68K: fails during second ROM-load pass before CPU execution.

This is not an isolated XGO anomaly. It follows the same pattern reported across sibling devices: stock arcade is unusually hard to beat.

## Decision

Stop treating “replace stock CPS1 core” as the default optimization path.

New primary research target:

**understand and optimize the stock XGO/SF2000-family FBA arcade implementation itself.**

Highest-value family-comparison targets:

1. Compare XGO stock FBA binary/config/runtime against SF2000 and GB300 v2 stock FBA.
2. Identify vendor-specific CPU backend, frameskip, audio sample rate, scheduler, and CPS1 speed hacks.
3. Determine whether GB300 v2 or later SF2000 firmware contains arcade-side performance fixes that can be transplanted.
4. Compare list/driver tables and CPS1-specific timing/configuration.
5. Preserve the external-core infrastructure as a secondary research path, not the main CPS1 optimization strategy.

## External-core status

Do not discard:
- MAME2000 gameplay proof
- FBA2012 content-path proof
- A68K reverse engineering

They remain useful architectural evidence.

But do not spend further hardware cycles bisecting individual SFII ROM loads unless a family comparison produces a concrete A68K-specific mechanism worth testing.
