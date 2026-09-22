# XGO A10 / XGO Plus Research

Reverse engineering, preservation, and experimental software development for the **XGO A10 / XGO Plus** handheld game console / power-bank platform.

The XGO is an **SF2000-derived HC15xx/MIPS system**, but it is a distinct hardware/firmware target. This repository documents the actual XGO firmware, resources, hardware behavior, family relationships, product provenance, and custom modifications proven on physical XGO hardware.

> **Current status — September 2026:** the cumulative hardware-proven baseline now includes Mapper v19, repaired CPS1 timing, Audio OSD v8, generalized on-device game-list Refresh, first-class CLASSIC/MAME2000 with Save/Load and metadata/JPEG artwork, Test74 SFC enrichment, Test75 FC enrichment, Test106 hardened Mega Drive Refresh, and the new first-class **REFRESH GAMES** selector through **Test123**. Test123 hardware-proves independent CLASSIC Refresh routing through the preserved native Refresh lifecycle and canonical Test72 external helper. FC/SFC/MD execution paths remain preserved; GB/GBC/GBA and Arcade are the next individually gated wiring work.

> **Regression status:** SFC Test74 and FC Test75 are both independently hardware-proven enrichment baselines. Test75 passed a real five-game FC batch, launch/play, and JPG artwork repair workflow. Test106 MD work did not directly modify the protected FC/SFC helper files, but the final Test106 cycle did not include a fresh physical FC/SFC launch regression. Therefore FC/SFC are proven historically and structurally preserved, while a post-Test106 spot-check remains the only missing cumulative regression evidence.

> **Roadmap clarification:** Pac-Man is not an open load-path defect. Pac-Man was hardware-confirmed running with Save/Load in Test52. Earlier Pac-Man/Ms. Pac-Man failures belong to superseded experimental loader history and must not be promoted into a current blocker without new hardware evidence.

> Do **not** flash stock SF2000 firmware onto an XGO based only on family similarity.

## Project goals

1. **Archaeology and preservation** — document the original machine, firmware, SD layout, interfaces, addresses, resource formats, emulator contracts, product lineage, packaging/manual evidence, and hardware behavior with reproducible evidence.
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
- 50-game CLASSIC metadata/JPEG batch hardware validation;
- **Test74 SFC stock enrichment**, including on-device materialization, explicit catalog merge, friendly titles/artwork, and successful multi-game batch behavior.

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

Hardware-confirmed Pac-Man and Galaga Save/Load, correct state restoration, and unchanged protected MAME2000 core.

### CLASSIC metadata and artwork

Friendly display names are supplied without renaming MAME ROM ZIPs:

```text
/CLASSIC/bin/tmnt.zip
/CLASSIC/meta/tmnt.txt
```

The stock-style wrapper contract is:

```text
[144 x 208 RGB565 preview = 59,904 bytes]
[WQW-obfuscated ZIP payload]
```

Test64 proved integrated on-device JPEG decoding, scaling/letterboxing and wrapper generation. Test72 then validated the complete path with a real **50-game** ROM/JPG/TXT batch; all 50 entries integrated and the immediate unchanged second Refresh returned `No New Games`.

```text
xgo-classic-test72-one-shot-batch-import.zip
SHA-256: af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16
```

## Major milestone: stock-console metadata/artwork enrichment

The stock wrapper/catalog contract was compared before propagation. Packaged console games use a 59,904-byte RGB565 preview followed by a WQW-obfuscated ZIP payload, with the catalog triplets remaining position-coupled. The implementation is being propagated **one stock family at a time**, preserving the existing generalized scanner rather than replacing it.

### SFC — Test74 hardware PASS

Test74 combines:

```text
/SFC/import/<basename>.sfc
/SFC/art/<basename>.jpg
/SFC/meta/<basename>.txt
        -> on-device materializer
        -> stock-style .zsf wrapper
        -> explicit SFC catalog merge
```

Hardware validation passed both the initial proof and a real three-game batch. Friendly entries appeared with artwork, launched normally, and the unchanged path converged correctly. Test74 is therefore part of the protected cumulative baseline.

See:

- `findings/stock-catalog-enrichment-wrapper-contract-comparison.md`
- `findings/hardware-test74-sfc-batch-catalog-merge-pass.md`
- `findings/hardware-test74-sfc-three-game-batch-pass.md`

### FC — Test75 hardware PASS

Test75 is hardware-proven. A five-game FC batch was added; all five generated entries launched and ran correctly. The first artwork attempt used unsupported PNG inputs by mistake; after replacing them with supported JPG files and regenerating the wrappers, artwork appeared correctly and the catalog records remained stable without duplication. Test75 also established the current append-only removal limitation: deleting a wrapper alone would leave a stale catalog entry, so standardized removal remains future work.

See `findings/hardware-test75-fc-enrichment-pass.md`.

### MD — Test106 hardened Refresh baseline

MD work progressed through Tests76–106. The decisive architecture preserves the exact known-booting Test97 firmware and its fixed 2642-byte helper load contract:

```text
unchanged bisrv.asd
      |
      v
MD/catalog.xgc          2642-byte Stage1
      |
      | loads + cache-syncs
      v
MD/catalog-safe.xgc     7000-byte relocated Stage2 @ 0x87180000
```

Test105 proved normal repeated no-change execution and deterministic recovery, but post-run forensics found the coherent stale 788 recovery triplet remained physically present. Static analysis showed the intended remove calls already existed, so Test106 stopped treating file deletion as transaction identity and introduced:

```text
/mnt/sda1/MD/art/.xgo-cat-state

ACTIVE  -> recovery may be required
CLEAN!  -> verified LIVE; stale .bak triplet is logically inert
```

Final hardware sequence:

```text
LIVE 839 + stale backup 788 + no marker
    -> Games Updated
    -> responsive
    -> artwork + gameplay PASS
    -> filesystem confirms CLEAN! + coherent LIVE 839

CLEAN! + stale backup 788 still physically present
    -> No new games
    -> responsive
```

This closes the repeated-stale-recovery defect without deliberately power-cutting or corrupting the SD card. Actual power-loss/media durability and fsync semantics remain OPEN.

Source/reconstruction and the full positive/negative experiment history are preserved under `tools/game_lists/md/test106/` and `findings/md-refresh-test76-test106-preservation-record.md`.

## Physical specimen and product provenance

The repository now preserves primary-source evidence from a newly purchased physical XGO specimen in addition to firmware archaeology.

The physical bilingual manual explicitly identifies **Model A10**, and the device itself also carries A10 labeling. The retail packaging presents the consumer identity as **XGO / XGO PLUS+ / GAME POWER BANK**, advertises 10000mAh power-bank functionality, magnetic wireless charging and the stock emulator-family concept. The manual documents the manufacturer-facing user-game workflow of copying compatible games to the TF card `ROMS` folder and accessing them through Settings → User Games.

A separate shipping/compliance label identifies **Shenzhen Jinhangzhaobang Technology Co., Ltd.** as the manufacturer for this exported specimen and supplies a distinct supply-chain SKU. This is evidence about the shipped unit; it does not by itself prove that the named company designed the PCB, owns the XGO brand, or is the ultimate OEM.

Primary-source photographs are organized under `evidence/` and `images/box/`. Repository photographs containing personal information have been sanitized/cropped; future evidence should likewise be checked before public commit.

## Chinese hardware / product-line archaeology

The physical specimen remains the primary target. Chinese/OEM research connects the transparent XGO specimen with XGO/DY10/A10/HC15xx-family evidence while keeping confidence levels explicit. SF2000, GB300, DY19, DY12, Q19, and related devices are comparators, not substitutes for XGO-specific evidence. Similar corporate names or marketplace identifiers are not collapsed into a single legal/OEM identity without supporting evidence.

## External native-core research

The XGO has executed external native libretro cores using stock XGO video/audio/input services. This work established the bidirectional `$gp` bridge requirement, stock callback/runtime contracts, and reusable MIPS O32 integration knowledge. See `tools/multicore/` and the external-core findings.

## Golden artifact preservation

Proprietary hardware-confirmed binaries are preserved in the private companion vault `jeborgesm/xgo-a10-artifacts`. Public repository indexing and verification live in:

- `artifacts/golden-artifacts.json`
- `docs/artifact-preservation.md`
- `tools/artifacts/verify_golden_artifact.py`

Public Git history preserves source, patch logic, findings, hashes, diagnostic history, and corrections.

## Hidden controller diagnostic

From the normal XGO menu, **L + SELECT** launches the built-in Super Famicom controller diagnostic stored as `Resources/Test.zsf`.

## Repository map

- `HANDOFF-CURRENT.md` — checkpoint and protected-baseline handoff
- `docs/` — hardware, firmware, lineage, controller and experiment documentation
- `findings/` — evidence-backed conclusions, candidates and hardware-test records
- `evidence/` — physical/manual/shipping-label primary-source evidence
- `images/box/` — retail packaging photographs
- `images/external/` — sourced comparator/device evidence
- `images/inbox/` — historical working-image archive
- `tools/game_lists/` — game-list / Refresh work
- `tools/multicore/` — external-core/runtime research
- `artifacts/golden-artifacts.json` — hardware-confirmed artifact index
- `.github/workflows/` — reproducible audits/build experiments

# Current next priority

The CLASSIC Refresh resurfacing branch is complete through **Test123 HW PASS** and is ready to merge. The first-class REFRESH GAMES UI has eight system rows, hardware-proven navigation/B-cancel/re-entry, suppression of the underlying Setup selector border, and independent CLASSIC execution. The canonical CLASSIC helper remains external at `/CLASSIC/refresh.xgc` with SHA-256 `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f`.

Exact current execution status:

```text
Famicom          -> preserved FC path
Super Famicom    -> preserved SFC path
Mega Drive       -> preserved MD path
Game Boy         -> intentionally inert pending next branch
Game Boy Color   -> intentionally inert pending next branch
Game Boy Advance -> intentionally inert pending next branch
Arcade            -> intentionally inert pending dedicated Arcade branch
Classic           -> HW-proven CLASSIC path (Test123)
```

The next branch wires **GB, GBC and GBA** individually using the already-preserved generalized native scanner/materializer evidence. Do not infer a generic Arcade list ID from that work: Arcade is a separate follow-on because the stock frontend separates shared `/ARCADE` content into CPS1, CPS2, NeoGeo and IGS catalogs (lists 7..10), requiring classification/orchestration rather than a single blind scan.

After all eight individual operations are stable, add the explicitly requested ninth **Refresh All** row. It must never be implicit in one of the eight system commands.

Source-of-truth rule: GitHub is the authoritative engineering record. Every firmware modification must have preserved source/reconstruction, deterministic build logic where practical, exact hashes/manifests, evidence classification, and hardware result before a branch is considered complete. Proprietary binary artifacts belong in the companion artifact vault; source, patch logic and findings belong in this repository.

Key current records:
- `HANDOFF-CURRENT.md`
- `docs/MODIFICATION-CONTINUITY-PROTOCOL.md`
- `docs/REUSE-FIRST-ENGINEERING-INDEX.md`
- `findings/test123-classic-rescue-hardware-pass.md`
- `tools/refresh_selector/build_test123_from_test122.py`

## Preservation philosophy

Reverse engineering benefits from retaining original observations, failed experiments that establish boundaries, diagnostic source, exact upstream revisions/toolchains, generated-artifact hashes, corrections to disproved interpretations, and hardware observations.

**Hardware outranks static assumptions.** Keep an untouched image of a known-working SD card before experimenting. Prefer testing on a clone.
