# HANDOFF-CURRENT

## Checkpoint — 2026-09-13

The `research-game-metadata-enrichment` branch is **complete, hardware-confirmed, and merged** through Test72.

Merged closure PR: **#44**

Merged cumulative baseline before this documentation correction:

```text
eabe61bda0af86605cb84505a75ed1e7e51cc504
```

The CLASSIC metadata/artwork work is closed after 72 cumulative experiments. The final hardware test processed a real 50-game batch successfully and a second unchanged Refresh returned `No New Games`.

## Important roadmap correction

Do **not** resume a Pac-Man / Ms. Pac-Man CLASSIC load-failure investigation as the next task.

That was stale historical context accidentally promoted into the previous handoff. Early CLASSIC experiments did encounter Pac-Man/Ms. Pac-Man bounce-back, black-screen and freeze behavior while the loader architecture was still changing. Those experiments were superseded.

Current evidence includes:

```text
Test52: Pac-Man Save/Load hardware PASS
Test52: Galaga Save/Load hardware PASS
```

Pac-Man therefore demonstrably launched and ran under the protected normalized CLASSIC/MAME2000 path. No current Pac-Man defect has been established. Ms. Pac-Man should likewise not be called broken unless a present-day hardware test demonstrates a regression.

The mistakenly created branch `research-classic-pacman-load-failure` is **abandoned**. Do not base new work on its task premise.

The next work is additive: propagate the proven metadata/artwork concepts to the stock emulator catalogs while preserving the complete merged baseline.

---

# New branch

Create/use:

```text
research-stock-catalog-enrichment
```

It must branch from the corrected current `main`, not from an old experimental firmware or from the abandoned Pac-Man branch.

## Branch goal

Extend the already hardware-proven stock-console Refresh scanner so newly discovered games in the stock emulator catalogs can receive the same *kind* of practical enrichment now proven for CLASSIC:

- friendly display names where the stock catalog/wrapper contract permits them;
- user-supplied JPG/JPEG artwork;
- on-device conversion into the correct stock preview format;
- stable repeated Refresh semantics;
- no regression to existing stock games or any protected cumulative feature.

Target stock systems:

```text
FC
SFC
MD
GB
GBC
GBA
```

Stock Arcade is **not** the first target. CLASSIC is already complete and must remain untouched except for regression verification.

---

# Non-negotiable cumulative baseline

Future candidates must preserve all of the following.

## Mapper v19

```text
artifact ID: mapper-v19
xgo-interactive-mapper-v19-card.zip
SHA-256: c45925f965cf86b4e1efc622b02aabb5545122814743aaf7723d4dbf6ba4ec81
firmware SHA-256: 466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab
```

Protected behavior:

- fifth `Mapper` option in stock in-game pause menu;
- interactive remapping;
- per-game `.kmp` persistence;
- corrected v19 geometry.

## CPS1 scheduler repair

Keep the stock FBA engine and the repaired family-style absolute wall-time / bounded-catchup pacing policy.

Hardware result on Street Fighter II:

- no prolonged underwater slowdown;
- minimal frame drops;
- normal playable fight speed.

Do not restore the older incremental debt scheduler.

## Audio OSD v8

```text
artifact ID: audio-osd-v8-button-event-only
xgo-audio-osd-v8-button-event-only-test.zip
SHA-256: ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a
firmware SHA-256: 4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954
```

Preserve fine volume, transient button-event-only OSD, gray border, timeout, no false boot OSD, and uninterrupted gameplay.

## Existing generalized stock-console Refresh

Hardware-proven scanner coverage:

```text
FC
SFC
MD
GB
GBC
GBA
```

Expected behavior:

```text
actual catalog change -> Games Updated
unchanged next pass -> No New Games
```

This already works. The new branch is an **enrichment**, not a scanner rewrite.

## CLASSIC generalized importer / normalized runtime

Normalized runtime artifact:

```text
xgo-classic-mame2000-normalized-test47-baseline.zip
SHA-256: 59f23688770588b7ea0670d5ffa167097a5a7b7ca8be6d6c1d6674bba8b14d36
```

Protected core:

```text
/cores/classic-mame2000/core.xgc
SHA-256: 60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

Do not modify this core for stock-catalog enrichment.

## CLASSIC Save/Load — Test52

```text
xgo-classic-test52-save-dir-fix.zip
SHA-256: f7aa1ebb7509913d389bc5922011c80795d4e5ec056f312800fe6ba3a02b78d4
firmware SHA-256: 8475cfdbec0e334d226d13e29c69bbd71dc99e5736b3ef185d4afdd360b91189
```

Hardware-confirmed:

- Pac-Man Save/Load PASS;
- Galaga Save/Load PASS;
- state restoration correct;
- approximately three seconds;
- core unchanged.

This evidence supersedes the old Pac-Man load-failure experiments.

## CLASSIC visual and reconciliation fixes

Preserve:

- Test57 12-slot `Resources/ihdsf.bke` CLASSIC logo-atlas fix;
- Test58 deletion reconciliation;
- `Resources/clssic.r56` as landing-page artwork, not a list-strip resource;
- stock consoles and stock Arcade behavior.

## External Refresh architecture

From Test59 onward CLASSIC heavy Refresh logic lives in:

```text
/CLASSIC/refresh.xgc
```

It is required runtime infrastructure. Deleting it causes `Refresh Failed`.

Test60 established stable CLASSIC no-change semantics.

## RGB565 scaling — Test61

Hardware-proven on-device resize/letterbox into the CLASSIC 144x208 RGB565 preview contract.

## Integrated JPEG — Test64

```text
xgo-classic-test64-integrated-jpeg-refresh.zip
ZIP SHA-256: 09ce9cd0a983f4a2887a5050718e30e55fe487dcb8ecc15b16f2b6c184676d3d
firmware SHA-256: 0fb8dda0f03b3a8068b23a02d03354475538be0c8e7ed83d8f2ee5d69ab57fef
refresh.xgc SHA-256: 6d416c71af871445023de96522d78bfa62b6277cfb7e5e37945bc12ea76dc98d
```

Hardware-proven CLASSIC path:

```text
/CLASSIC/art/<shortname>.jpg
  -> JPEG decode on XGO
  -> aspect-fit / letterbox
  -> 144 x 208 RGB565
  -> embedded wrapper preview
```

JPG/JPEG is the supported ordinary image source. PNG Tests65-70 are failed/deferred history and must not be resurrected for this branch.

## Test72 — final CLASSIC batch validation

```text
xgo-classic-test72-one-shot-batch-import.zip
SHA-256: af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16
```

Dataset:

```text
50 ROM ZIPs
50 matching JPGs
50 matching TXT metadata files
```

Hardware result:

- all 50 friendly titles integrated;
- all 50 JPGs converted on-device;
- matching RGB565 files generated;
- friendly-title `.zfb` wrappers created;
- ROM ZIPs retained;
- device responsive;
- second unchanged Refresh returned `No New Games`.

Automatic destructive cleanup was **not promoted**. Retaining JPG, RGB565, and TXT sidecars is accepted and useful.

CLASSIC steady state:

```text
/CLASSIC/bin/       ROM ZIPs
/CLASSIC/art/       JPG sources + generated RGB565 cache
/CLASSIC/meta/      editable friendly titles
/CLASSIC/*.zfb      generated wrappers
/CLASSIC/save/      state files
/CLASSIC/refresh.xgc
/cores/classic-mame2000/core.xgc
/bios/classic-mame2000/
```

---

# Known stock catalog contracts

Stock catalog binaries use:

```text
uint32_le count
uint32_le offsets[count]
char string_blob[]
```

Offsets are relative to the string blob. Each system's three files are index-coupled and must remain synchronized.

Known triplets:

```text
SFC  urefs.tax / adsnt.nec / xvb6c.bvs
FC   rdbui.tax / fhcfg.nec / nethn.bvs
MD   scksp.tax / setxa.nec / wmiui.bvs
GB   vdsdc.tax / umboa.nec / qdvd6.bvs
GBC  pnpui.tax / wjere.nec / mgdel.bvs
GBA  vfnet.tax / htuiw.nec / sppnp.bvs
```

Stock Arcade has multiple triplets and a different family/runtime problem space; leave it out of the first propagation step.

## Wrapper knowledge

SF2000-family/XGO wrappers generally follow the model:

```text
[preview bytes]
[WQW-obfuscated ZIP]
```

For CLASSIC the proven preview is exactly:

```text
144 x 208 x 2 = 59,904 bytes RGB565
WQW payload begins at 0xEA00
```

**Do not assume every stock system uses the exact CLASSIC dimensions or naming contract.** Determine the real contract per stock wrapper family before writing anything.

---

# New branch engineering strategy

The guiding rule is: **reuse proven mechanisms, not assumptions.**

CLASSIC proved that the XGO can decode JPEG, resize/letterbox RGB565, build stock-style wrappers, reconcile catalogs, and converge to stable no-change behavior. The next branch should reuse those components where the stock format matches, but must first characterize each stock system's wrapper and catalog semantics.

## Phase 1 — archaeology before patching

Start by comparing known stock wrappers for FC, SFC, MD, GB, GBC, and GBA.

For each system establish:

- outer wrapper extension and naming;
- preview byte count, dimensions and pixel format;
- WQW payload offset/header;
- embedded ZIP member name and compression expectations;
- which catalog field controls visible title;
- which field controls wrapper path/runtime identity;
- whether the ROM shortname/filename can remain independent from the display title;
- how favorites/save/mapper persistence references the entry;
- whether existing generalized Refresh currently creates a wrapper or only indexes an existing/raw ROM.

Use existing stock files as authoritative examples. Family devices may be comparators, but XGO stock behavior wins.

## Phase 2 — choose ONE representative system

Do not patch all six systems at once.

SFC is a strong first candidate because the project already proved generated `.zsf` wrappers early in the game-list work (`Test03`) and the hidden controller test also provides a known-good SFC wrapper reference.

The first candidate should prove only:

```text
raw/new SFC ROM
+ optional metadata TXT
+ optional JPG
-> Refresh
-> correct stock-style SFC wrapper/catalog entry
-> correct friendly title
-> correct artwork
-> launches normally
```

Then immediately verify an unchanged second Refresh returns `No New Games`.

## Phase 3 — regression gate

Before propagation, verify at minimum:

- newly enriched SFC game launches;
- an existing untouched stock SFC game launches;
- Mapper v19 still works and persists;
- Refresh unchanged pass says `No New Games`;
- CLASSIC game launches;
- CLASSIC Save/Load still works on a known title;
- CLASSIC metadata/artwork remains unchanged;
- Audio OSD still behaves correctly;
- stock Arcade remains unaffected.

Do not proceed to the other five systems until this gate passes.

## Phase 4 — propagate by contract family

Once one stock system is hardware-proven, compare the other wrapper families and group only those that are actually compatible. Reuse shared code where evidence supports it. Keep per-system descriptors for dimensions/extensions/catalog triplets rather than duplicating logic or assuming everything is SFC-shaped.

Recommended order after SFC proof:

```text
FC
MD
GB
GBC
GBA
```

This order is not sacred; change it if archaeology shows a more natural shared-contract grouping.

---

# Proposed SD-side source convention

Do not force this blindly onto stock systems, but use it as the starting design because it mirrors the successful CLASSIC workflow and keeps source material editable.

Possible pattern:

```text
/<SYSTEM>/<rom>
/<SYSTEM>/art/<basename>.jpg
/<SYSTEM>/meta/<basename>.txt
```

If stock directory conventions make a separate top-level source tree safer, prefer that rather than disturbing manufacturer files. The implementation should preserve ROM runtime identity and use metadata only for display naming where possible.

Retain source JPG/TXT after successful processing unless there is a compelling storage reason not to. Do not reintroduce automatic destructive cleanup.

---

# Things explicitly NOT to do

- Do not restart CLASSIC architecture work.
- Do not investigate Pac-Man merely because old experiments failed.
- Do not swap the protected MAME2000 core.
- Do not resume PNG decoding.
- Do not rewrite the already-working generalized scanner from scratch.
- Do not modify all six stock systems in the first candidate.
- Do not change stock Arcade as part of the first propagation.
- Do not use `Resources/clssic.r56` for unrelated UI work.
- Do not delete user JPG/TXT metadata after conversion.
- Do not treat a failed experimental branch as a new baseline.
- Do not build from a firmware predating the merged Test72-era cumulative baseline.

---

# First task in the new chat

Read this handoff and inspect the current merged repository before writing code.

Then perform the **stock wrapper contract comparison**, beginning with SFC because generated SFC wrapper import was already hardware-proven in Test03.

The first deliverable should be a concise evidence table for FC/SFC/MD/GB/GBC/GBA showing:

```text
system
wrapper extension
preview offset/size
preview dimensions/pixel format if established
payload/WQW offset
catalog triplet
visible-title field
runtime/wrapper field
current Refresh behavior
confidence/evidence source
```

After that, propose the smallest SFC-only enrichment candidate that reuses the Test64 JPEG decoder/scaler concepts without altering CLASSIC.

Only then build the first hardware test.

---

# Branch closure / continuation summary

The project is no longer trying to make CLASSIC basically work. That objective is complete.

After Test72 we have a strong additive platform:

- stock frontend preserved;
- Mapper v19;
- CPS1 pacing repair;
- Audio OSD v8;
- generalized stock-console discovery;
- first-class CLASSIC/MAME2000;
- CLASSIC Save/Load;
- stable external Refresh;
- friendly titles;
- stock-style artwork;
- on-device RGB565 scaling;
- on-device JPG conversion;
- 50-game CLASSIC batch validation;
- stable unchanged `No New Games`.

The next branch should **build on that success** by bringing richer metadata/artwork import to the stock console catalogs one proven system at a time, with the cumulative baseline treated as protected infrastructure.
