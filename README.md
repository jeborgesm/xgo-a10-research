# XGO A10 / XGO Plus Research

Reverse engineering, preservation, and experimental software development for the **XGO A10 / XGO Plus** handheld game console / power-bank platform.

The XGO is an **SF2000-derived HC15xx/MIPS system**, but it is a distinct hardware/firmware target. This repository documents the actual XGO firmware, resources, hardware behavior, family relationships, and custom modifications proven on physical XGO hardware.

> **Current status — September 2026:** the cumulative hardware-proven baseline includes Mapper v19, repaired CPS1 timing, Audio OSD v8, generalized on-device game-list Refresh, a first-class CLASSIC/MAME2000 list, CLASSIC Save/Load, deletion reconciliation, friendly titles, RGB565 artwork scaling, and fully on-device JPEG-to-wrapper artwork conversion. Test72 successfully processed a real 50-game CLASSIC metadata/JPEG batch; an immediate unchanged second Refresh returned `No New Games`.

> **Roadmap clarification:** Pac-Man is not an open load-path defect. Pac-Man was hardware-confirmed running with Save/Load in Test52. Earlier Pac-Man/Ms. Pac-Man failures belong to superseded experimental loader history and must not be promoted into a current blocker without new hardware evidence.

> Do **not** flash stock SF2000 firmware onto an XGO based only on family similarity.

## Project goals

1. **Archaeology and preservation** — document the original machine, firmware, SD layout, interfaces, addresses, resource formats, emulator contracts, product lineage, and hardware behavior with reproducible evidence.
2. **Experimental development** — extend the stock XGO safely while preserving the original frontend, controls, audio/video behavior, stock consoles, and recoverability.

## Cumulative protected baseline

Future work is additive. New branches must start from current merged `main` and must not silently roll back earlier hardware-confirmed behavior.

Protected behavior includes:

- interactive **Mapper v19** and per-game `.kmp` persistence;
- repaired CPS1 pacing without prolonged Street Fighter II slowdown;
- **Audio OSD v8** with fine volume, button-event-only display, gray border, correct timeout, and no boot-time false OSD;
- generalized Refresh for FC/SFC/MD/GB/GBC/GBA;
- first-class **CLASSIC** list and normalized MAME2000 runtime;
- stable `Games Updated` / `No New Games` convergence;
- CLASSIC Save/Load;
- stock consoles and stock Arcade preserved;
- CLASSIC friendly-title metadata and stock-style embedded artwork;
- deletion reconciliation;
- external `/CLASSIC/refresh.xgc` architecture;
- on-device RGB565 scaling/letterboxing;
- on-device JPG/JPEG decode and conversion;
- 50-game CLASSIC metadata/JPEG batch hardware validation.

Protected CLASSIC core:

```text
/cores/classic-mame2000/core.xgc
SHA-256: 60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

Do not replace or modify this core casually.

## Major milestone: Mapper v19

The stock in-game pause menu has a hardware-confirmed fifth `Mapper` option. Six physical controls can be remapped interactively and saved through the existing per-game `.kmp` mechanism. Mapper v19 combines the intact v7 UI geometry with the mature mapper behavior and corrected selector coordinates.

See `findings/interactive-xgo-mapper-v19-v7-geometry-v14-behavior.md` and related mapper findings.

## Major milestone: CPS1 scheduler repair

Family comparison across XGO, SF2000, and GB300 showed that the critical XGO divergence was frontend pacing rather than the FBA engine itself. Restoring the family-style absolute wall-time / bounded-catchup scheduler eliminated the prolonged Street Fighter II “underwater” slowdown while retaining the stock FBA engine.

## Major milestone: Audio OSD v8

Fine-grained volume and a transient OSD are hardware-confirmed. The OSD appears only on volume-button events, times out correctly, has the final 1-pixel gray border, does not falsely appear at boot, and does not interrupt gameplay.

## Major milestone: generalized on-device Refresh

The stock catalog format was reverse engineered as:

```text
uint32_le count
uint32_le offsets[count]
char string_blob[]
```

Each stock system uses three index-coupled catalogs. The generalized scanner can discover previously unindexed games while preserving existing ordering.

Hardware-proven stock-system discovery currently covers:

```text
FC
SFC
MD
GB
GBC
GBA
```

Stable UI semantics are:

```text
real change -> Games Updated
unchanged pass -> No New Games
```

This discovery capability predates the richer metadata/artwork pipeline completed for CLASSIC.

## Major milestone: first-class CLASSIC / MAME2000

Canonical layout:

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

The CLASSIC list supports the broader MAME2000 0.37b5-family collection used during development.

### Save/Load — Test52

```text
xgo-classic-test52-save-dir-fix.zip
SHA-256: f7aa1ebb7509913d389bc5922011c80795d4e5ec056f312800fe6ba3a02b78d4
firmware SHA-256: 8475cfdbec0e334d226d13e29c69bbd71dc99e5736b3ef185d4afdd360b91189
```

Hardware-confirmed:

- Pac-Man Save/Load: **PASS**;
- Galaga Save/Load: **PASS**;
- correct state restoration;
- approximately three seconds per operation;
- protected MAME2000 core unchanged.

This is why historical early Pac-Man launch failures are **not a current open issue**.

### CLASSIC metadata and artwork

Friendly display names are supplied without renaming MAME ROM ZIPs:

```text
/CLASSIC/bin/tmnt.zip
/CLASSIC/meta/tmnt.txt
```

The first line of the TXT is the friendly display/wrapper title; the shortname remains runtime identity.

The stock-style wrapper contract is:

```text
[144 x 208 RGB565 preview = 59,904 bytes]
[WQW-obfuscated ZIP payload]
```

Little-endian RGB565 packing:

```text
value = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
```

Test57 fixed the CLASSIC logo atlas by extending `Resources/ihdsf.bke` from 11 to 12 336x64 slots. `Resources/clssic.r56` is landing-page artwork and was not used as a list-strip fix.

Test58 added deletion reconciliation. Test59 moved heavy Refresh logic into required runtime helper `/CLASSIC/refresh.xgc`; deleting that helper causes `Refresh Failed`. Test60 established stable no-change semantics. Test61 proved on-device RGB565 scaling/letterboxing.

### Integrated JPEG — Test64

```text
xgo-classic-test64-integrated-jpeg-refresh.zip
ZIP SHA-256: 09ce9cd0a983f4a2887a5050718e30e55fe487dcb8ecc15b16f2b6c184676d3d
firmware SHA-256: 0fb8dda0f03b3a8068b23a02d03354475538be0c8e7ed83d8f2ee5d69ab57fef
refresh.xgc SHA-256: 6d416c71af871445023de96522d78bfa62b6277cfb7e5e37945bc12ea76dc98d
```

Hardware-proven path:

```text
/CLASSIC/art/<shortname>.jpg
  -> decode on XGO
  -> aspect-fit / letterbox
  -> 144 x 208 RGB565
  -> stock-style wrapper preview
```

JPG/JPEG is the supported ordinary source format. PNG Tests65-70 were exploratory failures and were deliberately dropped from scope.

### Full batch validation — Test72

```text
xgo-classic-test72-one-shot-batch-import.zip
SHA-256: af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16
```

Real hardware dataset:

```text
50 ROM ZIPs
50 matching JPGs
50 matching TXT metadata files
```

Result: all 50 friendly titles integrated, all 50 JPGs converted on-device, RGB565 previews generated, `.zfb` wrappers created, ROMs retained, device responsive, and the next unchanged Refresh returned **No New Games**.

Automatic destructive sidecar cleanup was not promoted. The accepted steady state retains JPG/TXT source material and the small RGB565 cache:

```text
/CLASSIC/bin/       ROM ZIPs
/CLASSIC/art/       JPG sources + generated RGB565
/CLASSIC/meta/      editable friendly titles
/CLASSIC/*.zfb      generated wrappers
/CLASSIC/save/      states
/CLASSIC/refresh.xgc
```

See `findings/classic-test72-batch-metadata-jpeg-hardware-pass.md`.

## External native-core research

The XGO has also executed external native libretro cores using stock XGO video/audio/input services. This work established the bidirectional `$gp` bridge requirement, stock callback/runtime contracts, and reusable MIPS O32 integration knowledge. See `tools/multicore/` and the external-core findings.

## Chinese hardware / product-line archaeology

The physical specimen remains the primary target. Chinese/OEM research strongly connects the transparent XGO specimen with DY10/XGO-branded listings and A10/HC15xx-family evidence. SF2000, GB300, DY19, DY12, Q19, and related devices are comparators, not substitutes for XGO-specific evidence.

## Golden artifact preservation

Proprietary hardware-confirmed binaries are preserved in the private companion vault `jeborgesm/xgo-a10-artifacts`. Public repository indexing and verification live in:

- `artifacts/golden-artifacts.json`
- `docs/artifact-preservation.md`
- `tools/artifacts/verify_golden_artifact.py`

Public Git history preserves source, patch logic, findings, hashes, and diagnostic history.

## Hidden controller diagnostic

From the normal XGO menu, **L + SELECT** launches the built-in Super Famicom controller diagnostic stored as `Resources/Test.zsf`.

## Repository map

- `HANDOFF-CURRENT.md` — exact current checkpoint and next-task handoff
- `docs/` — hardware, firmware, lineage, controller and experiment documentation
- `findings/` — evidence-backed conclusions and hardware-test records
- `tools/game_lists/` — game-list / Refresh work
- `tools/multicore/` — external-core/runtime research
- `artifacts/golden-artifacts.json` — hardware-confirmed artifact index
- `.github/workflows/` — reproducible audits/build experiments

# Next priority: propagate the proven enrichment model to stock catalogs

The CLASSIC metadata/JPEG work is complete after Test72. The next additive branch should **extend the useful metadata/artwork behavior to the existing stock emulator catalogs** — FC, SFC, MD, GB, GBC, and GBA — building on the already hardware-proven generalized stock-console scanner.

This is explicitly **not** a rewrite of Refresh and not a reason to disturb CLASSIC. The implementation should first document each stock wrapper/catalog contract, identify what can be shared safely from the CLASSIC pipeline, and then add enrichment one stock family at a time with hardware gates.

Primary objectives:

1. preserve current stock ROM discovery and stable `No New Games` semantics;
2. allow friendly display metadata for newly discovered stock-console games without requiring ROM renames where the stock format permits it;
3. allow user-supplied JPG artwork to be converted on-device into each stock system's actual wrapper/preview contract;
4. preserve stock ordering, launch behavior, pause menu, Mapper v19, Save/Load behavior, Audio OSD, CPS1 repair, stock Arcade, and the complete CLASSIC/Test72 path;
5. avoid a monolithic all-systems first test: prove one representative stock system, then propagate only after hardware validation.

See `HANDOFF-CURRENT.md` for the detailed branch plan and regression gates.

## Preservation philosophy

Reverse engineering benefits from retaining original observations, failed experiments that establish boundaries, diagnostic source, exact upstream revisions/toolchains, generated-artifact hashes, corrections to disproved interpretations, and hardware observations.

**Hardware outranks static assumptions.** Keep an untouched image of a known-working SD card before experimenting. Prefer testing on a clone.
