# XGO A10 / XGO Plus Research

Reverse engineering, preservation, and experimental software development for the **XGO A10 / XGO Plus** handheld game console / power-bank platform.

The XGO is an **SF2000-derived HC15xx/MIPS system**, but it is not simply an SF2000 in a different enclosure. This repository documents the actual XGO firmware, resources, hardware behavior, family relationships, and the custom modifications now proven on physical XGO hardware.

> **Current status — September 2026:** the cumulative XGO baseline now includes an interactive per-game button mapper, repaired CPS1 timing, fine-grained volume with transient OSD, generalized on-device game-list refresh, a first-class CLASSIC/MAME2000 list, CLASSIC Save/Load, deletion reconciliation, editable friendly titles, RGB565 artwork scaling, and fully on-device JPEG-to-wrapper artwork conversion. A 50-game CLASSIC metadata/JPEG batch completed successfully on hardware and a subsequent unchanged Refresh returned `No New Games`.

> Do **not** flash stock SF2000 firmware onto an XGO based only on family similarity. The XGO remains a distinct hardware/firmware target.

## Project goals

The project has two related purposes:

1. **Archaeology and preservation** — document the original machine, firmware, SD layout, interfaces, addresses, resource formats, emulator contracts, product lineage, and hardware behavior with reproducible evidence.
2. **Experimental development** — use that understanding to extend the stock XGO safely while preserving the original frontend, controls, audio/video behavior, stock consoles, and recoverability.

The second goal is no longer hypothetical. The XGO now runs substantial custom firmware-side functionality and external native emulator code on real hardware.

---

# Current cumulative hardware-proven baseline

The most important rule for future work is that the baseline is **cumulative**. New branches must not silently roll back earlier hardware-confirmed behavior.

Protected behavior currently includes:

- interactive **Mapper v19** in the stock pause menu;
- per-game `.kmp` persistence;
- repaired CPS1 pacing without the prolonged Street Fighter II slowdown;
- **Audio OSD v8** with fine volume and button-event-only transient display;
- generalized stock-console Refresh;
- first-class **CLASSIC** list and normalized MAME2000 runtime layout;
- stable repeated Refresh / `No New Games` behavior;
- CLASSIC Save/Load;
- stock consoles unaffected;
- stock Arcade unaffected;
- CLASSIC friendly-title metadata;
- stock-style embedded preview artwork;
- catalog deletion reconciliation;
- external `/CLASSIC/refresh.xgc` helper architecture;
- on-device RGB565 scaling/letterboxing;
- on-device ordinary JPEG decode and conversion;
- 50-game batch metadata/JPEG import proven on hardware.

Protected CLASSIC core:

```text
/cores/classic-mame2000/core.xgc
SHA-256: 60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

Do not replace this core casually. The final CLASSIC Save/Load solution was implemented around it specifically so the core could remain byte-for-byte unchanged.

---

# Major milestone: interactive on-device button mapper

The XGO now has a hardware-confirmed interactive mapper integrated into the stock in-game pause menu as a fifth option, `Mapper`.

```text
Start+Select pause menu
  -> Mapper
  -> six physical controls: X / Y / L / A / B / R
  -> choose logical target
  -> confirm
  -> existing per-game <game>.kmp persistence
```

The feature has been exercised with NES, SNES, and CPS1 titles and survives game exit/relaunch.

The final hardware-confirmed presentation build is **Mapper v19**. A long-lived visual corruption was traced to a resource regression rather than mapper logic: a 35-pixel strip of the intact v7 UI had been overwritten in later resource generation. v19 recombined the intact v7 geometry with the mature mapper behavior and corrected selector coordinates.

See:

- [`findings/interactive-xgo-mapper-v19-v7-geometry-v14-behavior.md`](findings/interactive-xgo-mapper-v19-v7-geometry-v14-behavior.md)
- [`findings/family-native-mapper-ui-state-model.md`](findings/family-native-mapper-ui-state-model.md)
- [`findings/gb300-v1-native-mapper-handler-and-commit-path.md`](findings/gb300-v1-native-mapper-handler-and-commit-path.md)
- [`findings/xgo-per-game-kmp-format-and-sf2000-branch-point.md`](findings/xgo-per-game-kmp-format-and-sf2000-branch-point.md)

---

# Major milestone: stock CPS1 slowdown fixed

Family comparison across XGO, SF2000, and GB300 recovered the stock arcade timing contract:

```text
C68K for ordinary CPS1/68000 execution
22050-Hz / 367-sample FBA audio
private render-only frameskip
continued emulation/audio during skipped-render frames
```

The critical XGO divergence was the frontend pacing policy. A scheduler-only transplant restored the family-style bounded wall-time behavior without replacing the stock FBA engine.

Hardware testing on Street Fighter II confirmed:

- no prolonged “underwater” slowdown;
- minimal frame drops;
- normal playable fight speed;
- protected mapper/SNES behavior retained.

See:

- [`findings/hardware-test-stock-cps1-sibling-scheduler-success.md`](findings/hardware-test-stock-cps1-sibling-scheduler-success.md)
- [`findings/stock-fba-cpu-backend-and-frontend-timing-comparison.md`](findings/stock-fba-cpu-backend-and-frontend-timing-comparison.md)
- [`findings/xgo-stock-scheduler-transplant-patch-surface.md`](findings/xgo-stock-scheduler-transplant-patch-surface.md)

---

# Major milestone: Audio OSD and fine volume

The XGO now has hardware-confirmed fine-grained volume control with a transient on-screen display.

Final Audio OSD behavior:

- finer audible volume steps than stock;
- OSD appears only on volume-button events;
- correct timeout in the main menu and in-game;
- no false OSD at boot;
- 1-pixel gray border;
- no interruption of gameplay;
- mapper and CPS1 timing changes preserved.

Final artifact ID:

```text
audio-osd-v8-button-event-only
```

The OSD work is part of the protected cumulative baseline.

---

# Major milestone: on-device game-list Refresh

The stock XGO game catalogs were reverse engineered and a visible **Refresh** option was added to the User Menu.

The catalog format is:

```text
uint32_le count
uint32_le offsets[count]
char string_blob[]
```

Each stock system uses three index-coupled catalogs. The generalized scanner can discover previously unindexed games and append them without destroying the stock ordering.

Hardware-proven console scanning includes:

- FC
- SFC
- MD
- GB
- GBC
- GBA

The UI also gained timed status feedback such as:

```text
Games Updated
No New Games
```

Repeated unchanged Refresh is expected to converge cleanly to `No New Games`.

See:

- [`findings/game-list-test08-hardware-pass.md`](findings/game-list-test08-hardware-pass.md)
- [`findings/general-refresh-scanner-runtime-contract.md`](findings/general-refresh-scanner-runtime-contract.md)
- [`findings/xgo-zxx-wrapper-and-import-packaging-contract.md`](findings/xgo-zxx-wrapper-and-import-packaging-contract.md)

---

# Major milestone: first-class CLASSIC / MAME2000 list

The fifth game page was converted from a fragile experimental arcade page into a first-class **CLASSIC** list with its own ROM area and MAME2000 runtime.

Canonical runtime layout:

```text
/CLASSIC/
/CLASSIC/bin/
/CLASSIC/art/
/CLASSIC/meta/
/CLASSIC/save/
/CLASSIC/refresh.xgc
/cores/classic-mame2000/core.xgc
/bios/classic-mame2000/
```

The normalized core path is:

```text
/cores/classic-mame2000/core.xgc
```

The CLASSIC list now supports 40+ games and has been exercised with titles including Cadillacs and Dinosaurs, Galaga, Pac-Man, Contra, and others.

## CLASSIC Save/Load

CLASSIC Save/Load is hardware-confirmed.

Final Test52 artifact:

```text
xgo-classic-test52-save-dir-fix.zip
SHA-256: f7aa1ebb7509913d389bc5922011c80795d4e5ec056f312800fe6ba3a02b78d4
firmware SHA-256: 8475cfdbec0e334d226d13e29c69bbd71dc99e5736b3ef185d4afdd360b91189
```

Hardware-confirmed Save/Load:

- Pac-Man: PASS
- Galaga: PASS
- state restoration correct
- approximately three seconds per Save/Load operation; accepted behavior
- protected MAME2000 core unchanged

See [`findings/classic-test52-save-load-hardware-pass.md`](findings/classic-test52-save-load-hardware-pass.md).

---

# Major milestone: CLASSIC metadata and artwork enrichment

The original generalized importer proved that arbitrary MAME2000 ROMs could be surfaced, but new entries were initially bare filename-derived items. The `research-game-metadata-enrichment` branch converted that proof into a practical content-management workflow.

## Friendly display titles

A ROM can retain its shortname/runtime identity while exposing a human-friendly title through:

```text
/CLASSIC/bin/tmnt.zip
/CLASSIC/meta/tmnt.txt
```

The first line of `tmnt.txt` becomes the friendly display/wrapper title. The ROM itself remains `tmnt.zip` for MAME compatibility.

This avoids renaming ROMs merely to improve the UI.

## Stock-style wrapper artwork

Reverse engineering confirmed the XGO wrapper contract:

```text
[144 x 208 RGB565 preview = 59,904 bytes]
[WQW-obfuscated ZIP payload]
```

Test53 proved external 144 x 208 little-endian RGB565 artwork on hardware.

The RGB565 packing contract is:

```text
value = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
```

## CLASSIC logo-atlas fix

A separate fifth-page visual bug was traced to `Resources/ihdsf.bke`.

Stock atlas:

```text
336 x 704 x 4 RGBA
11 vertical slots of 336 x 64
```

CLASSIC list state 11 required a twelfth slot, causing an out-of-bounds logo read. Test57 appended a proper 12th CLASSIC slot, producing a 336 x 768 atlas while keeping the original stock bytes intact.

`Resources/clssic.r56` was not modified for this fix; it is landing-page artwork, not the list-strip resource.

## Deletion reconciliation

Test58 added reconciliation so deleting a generated CLASSIC game is reflected in the catalogs. The Refresh path can remove catalog entries whose wrapper/ROM relationship no longer exists while leaving malformed/manual wrappers alone rather than deleting unknown content speculatively.

## External Refresh helper

From Test59 onward, most Refresh logic moved out of the crowded firmware cave and into:

```text
/CLASSIC/refresh.xgc
```

This helper is loaded at runtime by a small firmware bootstrap and is now a **required system file**. Deleting `refresh.xgc` while cleaning `.zfb` wrappers causes Refresh to fail.

Test60 restored exact stable no-change semantics through final catalog-byte comparison:

```text
real change -> Games Updated
next unchanged pass -> No New Games
```

## On-device RGB565 scaling

Test61 proved that source artwork does not need to be pre-sized to 144 x 208.

A 320 x 224 RGB565 Shinobi image was resized on-device with aspect preservation and letterboxing to the exact 144 x 208 preview contract.

## On-device JPEG conversion

Test64 integrated ordinary JPEG support directly into `refresh.xgc`.

Hardware-proven path:

```text
/CLASSIC/art/<shortname>.jpg
        -> decode on XGO
        -> aspect-fit / letterbox
        -> 144 x 208 RGB565
        -> wrapper preview
```

Test64 artifact:

```text
xgo-classic-test64-integrated-jpeg-refresh.zip
ZIP SHA-256: 09ce9cd0a983f4a2887a5050718e30e55fe487dcb8ecc15b16f2b6c184676d3d
firmware SHA-256: 0fb8dda0f03b3a8068b23a02d03354475538be0c8e7ed83d8f2ee5d69ab57fef
refresh.xgc SHA-256: 6d416c71af871445023de96522d78bfa62b6277cfb7e5e37945bc12ea76dc98d
```

Supported ordinary image format for the protected workflow is **JPG/JPEG**.

PNG was investigated in Tests65-70 but intentionally dropped from scope after repeated device-side failures. JPG already satisfies the practical requirement and is the supported source format.

## 50-game batch validation — Test72

The metadata/artwork branch closed with a full real-world batch test.

Test SD input:

```text
50 ROM ZIPs
50 matching JPGs
50 matching TXT metadata files
```

Hardware result:

- all 50 titles were imported with friendly names;
- all 50 JPGs were converted on-device;
- matching RGB565 preview files were generated;
- stock-style `.zfb` wrappers were created;
- ROM ZIPs remained intact;
- device remained responsive;
- second unchanged Refresh returned **No New Games**.

Test72 artifact:

```text
xgo-classic-test72-one-shot-batch-import.zip
SHA-256: af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16
```

The attempted one-shot cleanup idea was not promoted. The hardware-passed batch retained JPG, RGB565, and TXT sidecars. That is now acceptable and useful: JPG/TXT files are editable source material and the RGB565 files are a small cache.

Preferred steady-state layout:

```text
/CLASSIC/bin/       ROM ZIPs
/CLASSIC/art/       JPG sources + generated RGB565
/CLASSIC/meta/      editable friendly titles
/CLASSIC/*.zfb      generated wrappers
/CLASSIC/save/      states
/CLASSIC/refresh.xgc
```

See [`findings/classic-test72-batch-metadata-jpeg-hardware-pass.md`](findings/classic-test72-batch-metadata-jpeg-hardware-pass.md).

---

# Major milestone: external native NES core

The XGO can launch and play an NES ROM through an **external FCEUmm libretro core** stored on the SD card rather than the firmware's embedded NES emulator.

Hardware-confirmed path:

```text
stock XGO NES menu
  -> stock ROM preload
  -> patched launch call
  -> injected loader
  -> /cores/fceumm/core.xgc
  -> external core @ 0x87000000
  -> XGO native frontend
  -> FCEUmm
  -> stock XGO video/audio/input through GP-safe bridges
```

This work established several platform-level facts:

- external MIPS code requires correct `$gp` handling in both directions;
- stock callbacks depend on stock GP-relative state;
- stock `run_emulator()` can drive external libretro function pointers;
- MIPS O32 ABI details matter for filesystem/timing calls;
- behavior-based probes are safer than logging through partially initialized subsystems.

See:

- [`findings/external-nes-proof-handoff.md`](findings/external-nes-proof-handoff.md)
- [`findings/hardware-test-first-successful-external-fceumm-gameplay.md`](findings/hardware-test-first-successful-external-fceumm-gameplay.md)
- [`findings/xgo-bidirectional-gp-abi.md`](findings/xgo-bidirectional-gp-abi.md)

---

# Chinese hardware / product-line archaeology

The project also investigates the physical XGO specimen and its Chinese/OEM lineage rather than assuming every answer comes from the better-known SF2000 scene.

Strong product identity evidence ties the transparent XGO specimen to **DY10** / XGO-branded Chinese listings and an A10/HC15xx-family platform footprint.

Useful target fingerprint includes:

```text
芯果 / Xinguo / XGO
XGO PLUS+ 10000MAH
A10
DY10
transparent landscape enclosure
10000 mAh nominal
5800 mAh / 37 Wh rated
22.5 W wired charging
15 W magnetic wireless charging
~141 x 67 x 20 mm
left joystick + Select/Start
six face buttons
TF / USB-C / AV / external-controller support
H1512 / HC15xx / B210 evidence
```

DY19, DY12, Q19, X60, and SF2000 remain useful comparators but are not substitutes for the exact XGO target.

---

# Golden artifact preservation

The public archaeology repository deliberately does not publish proprietary firmware bytes. Hardware-confirmed binaries are preserved separately in the **private** companion vault:

```text
jeborgesm/xgo-a10-artifacts
```

Canonical indexing and verification live here:

- [`artifacts/golden-artifacts.json`](artifacts/golden-artifacts.json)
- [`docs/artifact-preservation.md`](docs/artifact-preservation.md)
- [`tools/artifacts/verify_golden_artifact.py`](tools/artifacts/verify_golden_artifact.py)

Important cumulative milestones include:

```text
Mapper v19
  -> native SNES proof
  -> CPS1 scheduler repair
  -> Audio OSD v8
  -> generalized game-list Refresh
  -> CLASSIC importer
  -> normalized CLASSIC MAME2000 runtime
  -> CLASSIC Save/Load
  -> metadata/artwork enrichment
  -> integrated JPEG Refresh
  -> 50-game batch validation
```

Public Git history preserves the source, patch logic, findings, hashes, and diagnostic history even when the final proprietary firmware ZIP itself belongs only in the private artifact vault.

---

# Hidden controller diagnostic

From the normal XGO menu, press **L + SELECT** simultaneously to launch the built-in Super Famicom controller diagnostic stored as:

```text
Resources/Test.zsf
```

The firmware checks the translated input value `0x1001` and branches directly to the diagnostic launcher.

See [`findings/hidden-controller-test-trigger.md`](findings/hidden-controller-test-trigger.md).

---

# Repository map

- [`HANDOFF-CURRENT.md`](HANDOFF-CURRENT.md) — current checkpoint and exact next-task handoff
- [`docs/hardware.md`](docs/hardware.md) — known hardware and ports
- [`docs/firmware.md`](docs/firmware.md) — SD layout and firmware evidence
- [`docs/sf2000-lineage.md`](docs/sf2000-lineage.md) — evidence connecting XGO to the SF2000 family
- [`docs/controller-research.md`](docs/controller-research.md) — Player 2 / Handle Interface research
- [`docs/experiments.md`](docs/experiments.md) — physical-device experiments
- [`docs/research-log.md`](docs/research-log.md) — chronological notes
- [`findings/`](findings/) — evidence-backed conclusions and hardware-test records
- [`tools/game_lists/`](tools/game_lists/) — game-list / Refresh work
- [`tools/multicore/`](tools/multicore/) — external-core/runtime research
- [`artifacts/golden-artifacts.json`](artifacts/golden-artifacts.json) — hardware-confirmed artifact index
- [`.github/workflows/`](.github/workflows/) — reproducible audits/build experiments

---

# Next priority

The metadata/JPEG branch is closed after Test72.

The next priority is the remaining **Pac-Man / Ms. Pac-Man CLASSIC load-path discrepancy** on a clean branch from the merged cumulative baseline.

The key question is why these titles historically behaved differently from the broader MAME2000 set despite the generalized CLASSIC loader, while other 0.37b5-family titles launch normally. The next branch should investigate the ROM/core/driver/load contract without regressing the now-stable CLASSIC Refresh, Save/Load, metadata, artwork, or JPEG pipeline.

See [`HANDOFF-CURRENT.md`](HANDOFF-CURRENT.md) for the detailed starting state.

---

# Preservation philosophy

This repository intentionally keeps more than a polished final implementation.

Reverse engineering benefits from preserving:

- original specimen hashes and offsets;
- raw observations separately from interpretations;
- failed experiments when they establish a boundary;
- diagnostic source used to prove those boundaries;
- exact upstream revisions and toolchains;
- build workflows and generated-artifact hashes;
- corrections when a previous interpretation is disproved;
- hardware observations, because hardware outranks static assumptions.

**Copies of copies are a feature.** Prefer adding a clearly identified replacement or superseding finding over silently erasing useful archaeological history.

## Evidence labels

- **Confirmed** — directly observed on the physical device/card or established by reproducible executable/binary evidence.
- **Strong evidence** — multiple independent observations support the conclusion.
- **Hypothesis** — plausible explanation requiring further testing.
- **Unknown** — not established.

## Firmware preservation and copyright

This repository does **not** publish the original full SD image, commercial ROM collections, copyrighted BIOS archives, or the proprietary stock `bisrv.asd` image. It preserves hashes, filenames, offsets, observations, custom source, linker/runtime contracts, diagnostics, and reproducible patch/build methods.

Keep an untouched image of a known-working SD card before experimenting. Prefer testing on a clone.
