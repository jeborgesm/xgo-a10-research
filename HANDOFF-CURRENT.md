# HANDOFF-CURRENT

## Checkpoint — 2026-09-13

The `research-game-metadata-enrichment` branch is complete and ready to merge.

This branch started from merged `main` commit:

```text
7bef32b9953fd0b5d477b644563f6a62eabef9d2
```

It closes after **72 cumulative CLASSIC/game-list experiments** with the metadata/artwork pipeline hardware-proven at full-batch scale.

The next branch should be created from the merged `main` result and should investigate the remaining **Pac-Man / Ms. Pac-Man CLASSIC load-path discrepancy** without regressing the cumulative baseline below.

---

# Protected cumulative baseline

Future work must preserve all hardware-confirmed behavior unless the next task explicitly requires changing that subsystem.

## Mapper v19

```text
artifact ID: mapper-v19
xgo-interactive-mapper-v19-card.zip
SHA-256: c45925f965cf86b4e1efc622b02aabb5545122814743aaf7723d4dbf6ba4ec81
firmware SHA-256: 466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab
```

Protected behavior:

- fifth `Mapper` option remains in the stock in-game pause menu;
- interactive remapping works;
- per-game mapping persistence remains intact;
- do not regress to a firmware baseline predating Mapper v19.

## Audio OSD v8

```text
artifact ID: audio-osd-v8-button-event-only
xgo-audio-osd-v8-button-event-only-test.zip
SHA-256: ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a
firmware SHA-256: 4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954
```

Protected behavior:

- fine volume control;
- transient button-event-only OSD;
- 1-pixel gray border;
- correct timeout;
- no false boot-time OSD;
- gameplay remains uninterrupted.

## CPS1 scheduler repair

The stock FBA engine remains in place. The pacing repair came from restoring the family-style absolute wall-time / bounded-catchup policy rather than replacing the engine.

Hardware result on Street Fighter II:

- no prolonged underwater slowdown;
- minimal frame drops;
- normal playable fight speed.

Do not replace this with the older incremental debt scheduler.

## Generalized stock-console Refresh

Hardware-proven scanner coverage:

```text
FC
SFC
MD
GB
GBC
GBA
```

Expected stable behavior:

```text
real change -> Games Updated
unchanged next pass -> No New Games
```

## CLASSIC generalized importer / normalized runtime

```text
TEST47 — hardware PASS
xgo-classic-test47-general-importer.zip
SHA-256: d40a811e2ef05788688fe516e520b3f11b2e5b08ca77d926e77bf1c224f5db53
```

Normalized runtime artifact:

```text
xgo-classic-mame2000-normalized-test47-baseline.zip
SHA-256: 59f23688770588b7ea0670d5ffa167097a5a7b7ca8be6d6c1d6674bba8b14d36
```

Protected MAME2000 core:

```text
/cores/classic-mame2000/core.xgc
SHA-256: 60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

Do **not** modify this core as the first move in the next branch.

## CLASSIC Save/Load

```text
TEST52 — hardware PASS
xgo-classic-test52-save-dir-fix.zip
SHA-256: f7aa1ebb7509913d389bc5922011c80795d4e5ec056f312800fe6ba3a02b78d4
firmware SHA-256: 8475cfdbec0e334d226d13e29c69bbd71dc99e5736b3ef185d4afdd360b91189
```

Hardware-confirmed:

- Pac-Man Save/Load PASS;
- Galaga Save/Load PASS;
- state restoration correct;
- operation takes about three seconds;
- protected MAME2000 core remains byte-for-byte unchanged.

## CLASSIC logo-atlas fix

Test57 hardware PASS.

Root cause:

```text
Resources/ihdsf.bke = 336 x 704 x 4 RGBA
11 vertical slots of 336 x 64
```

CLASSIC state 11 required slot 12. The fixed atlas is 336 x 768 with stock bytes preserved and a new CLASSIC slot appended.

Do not touch `Resources/clssic.r56` to fix list-strip issues; it is CLASSIC landing-page artwork.

## CLASSIC deletion reconciliation

Test58 hardware PASS.

Refresh removes stale generated catalog entries when their expected wrapper/ROM relationship is gone, while leaving malformed/manual wrappers alone rather than deleting unknown files speculatively.

## External Refresh architecture

From Test59 onward the heavy Refresh logic lives in:

```text
/CLASSIC/refresh.xgc
```

The firmware contains only the bootstrap required to load and execute it.

**Important:** `/CLASSIC/refresh.xgc` is a required runtime file. If it is deleted while clearing generated `.zfb` files, Refresh returns `Refresh Failed`.

Test60 hardware PASS established the stable `No New Games` path.

## On-device RGB565 scaling

Test61 hardware PASS.

A 320 x 224 RGB565 source image was resized on-device to 144 x 208 using aspect preservation and black letterboxing. Exact 144 x 208 RGB565 remains supported.

## Integrated JPEG conversion

Test64 is the protected JPEG baseline.

```text
xgo-classic-test64-integrated-jpeg-refresh.zip
ZIP SHA-256: 09ce9cd0a983f4a2887a5050718e30e55fe487dcb8ecc15b16f2b6c184676d3d
firmware SHA-256: 0fb8dda0f03b3a8068b23a02d03354475538be0c8e7ed83d8f2ee5d69ab57fef
refresh.xgc SHA-256: 6d416c71af871445023de96522d78bfa62b6277cfb7e5e37945bc12ea76dc98d
```

Hardware-proven path:

```text
/CLASSIC/art/<shortname>.jpg
  -> decode on-device
  -> aspect-fit / letterbox
  -> 144 x 208 RGB565
  -> embed as stock-style wrapper preview
```

Supported ordinary source format for this workflow is JPG/JPEG.

PNG Tests65-70 were diagnostic/failed experiments and are **not** part of the protected baseline. PNG was deliberately dropped from scope.

## Friendly title metadata

For a new or rebuilt game:

```text
/CLASSIC/bin/<shortname>.zip
/CLASSIC/meta/<shortname>.txt
/CLASSIC/art/<shortname>.jpg
```

The first line of the TXT becomes the friendly display/wrapper title. The ROM ZIP shortname remains the runtime identity required by MAME.

## Test72 — 50-game batch hardware PASS

Artifact:

```text
xgo-classic-test72-one-shot-batch-import.zip
SHA-256: af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16
```

Final test dataset:

```text
50 ROM ZIPs
50 matching JPGs
50 matching TXT metadata files
```

Hardware result:

- all 50 friendly titles integrated;
- all 50 JPGs converted on-device;
- 50 RGB565 files generated;
- friendly-title `.zfb` wrappers created;
- ROM ZIPs retained;
- device remained responsive;
- second unchanged Refresh returned `No New Games`.

The post-run filesystem intentionally retains the JPG, RGB565, and TXT sidecars. Automatic destructive cleanup was not promoted.

Preferred steady-state layout:

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

Primary branch-closure finding:

```text
findings/classic-test72-batch-metadata-jpeg-hardware-pass.md
```

Machine-readable milestone index:

```text
artifacts/classic-metadata-jpeg-milestones.json
```

---

# Important stock/wrapper contracts

## XGO wrapper format

Stock-style `.zfb` / `.zsf` wrappers have the general structure:

```text
[preview image bytes]
[WQW-obfuscated ZIP]
```

For the CLASSIC preview path:

```text
144 x 208 x 2 = 59,904 bytes RGB565
```

The obfuscated ZIP begins at offset:

```text
0xEA00
```

## RGB565 packing

Little-endian RGB565:

```text
value = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
```

## Catalog format

```text
uint32_le count
uint32_le offsets[count]
char string_blob[]
```

Offsets are relative to the string blob. Catalog triplets are index-coupled and must remain synchronized.

## Stock Arcade model relevant to CLASSIC

The useful stock pattern is:

- friendly outer `.zfb` wrapper;
- actual MAME shortname ZIP under `/ARCADE/bin` or `/CLASSIC/bin`;
- preview embedded in wrapper;
- runtime identity remains the shortname.

That pattern is the basis of the current CLASSIC architecture.

---

# Next branch / next priority

Create a fresh branch from the newly merged `main` baseline:

```text
research-classic-pacman-load-failure
```

Goal:

**explain and correct the remaining Pac-Man / Ms. Pac-Man CLASSIC load-path discrepancy without changing the protected MAME2000 core unless evidence proves it is necessary.**

Historical observations to carry forward:

- many MAME 0.37b5-family games work normally in CLASSIC;
- Cadillacs and Dinosaurs worked early;
- Galaga became playable through the generalized importer;
- Pac-Man / Ms. Pac-Man historically showed inconsistent behavior during early CLASSIC work, including `Loading...` followed by bounce-back, black/freeze, or failure depending on the exact loader experiment;
- later CLASSIC Save/Load was hardware-confirmed on Pac-Man, so the current cumulative state must be re-verified before assuming the old failure still exists in exactly the same form;
- do not start by swapping cores: the current protected MAME2000 core is known-good for the broader set and Save/Load;
- previous attempts that replaced/ported core contracts introduced freezes and cost substantial time;
- family/SF2000/GB300 implementations should be used as comparative evidence before inventing a new loader contract.

Recommended first sequence in the new chat:

1. Reproduce the current Pac-Man and Ms. Pac-Man behavior on the **merged Test72-era baseline** and record exactly what still fails.
2. Compare their generated `.zfb`, inner ZIP names, catalog entries, and ROM shortnames against known-working CLASSIC titles such as Galaga.
3. Verify whether Pac-Man and Ms. Pac-Man are using the same normalized `/cores/classic-mame2000/core.xgc` path and the same launcher contract as working games.
4. Inspect MAME2000 0.37b5 driver/ROM expectations for `pacman` and `mspacman` and compare required ROM members/CRC names against the actual SD ZIPs.
5. Compare the XGO path with known SF2000/GB300 family MAME2000 loader behavior before modifying firmware.
6. Only after those checks should any code change be proposed.

Do not disturb the working metadata/JPEG pipeline while investigating load behavior.

---

# Branch-closure summary

After 72 tests, the metadata/artwork branch has achieved its practical goal:

- user-editable titles;
- user-supplied JPG artwork;
- on-device image conversion;
- stock-style wrapper generation;
- deletion reconciliation;
- stable external Refresh;
- stable unchanged `No New Games`;
- full 50-game batch validation;
- CLASSIC Save/Load and earlier protected features preserved.

This branch should now be merged and retired. The next work belongs on a clean branch focused only on the remaining load-path problem.
