# CLASSIC Test72 — 50-game metadata/JPEG batch hardware PASS

Date: 2026-09-13

Branch: `research-game-metadata-enrichment`

## Result

Test72 completed a full 50-game CLASSIC metadata/artwork batch on real XGO hardware and the subsequent unchanged Refresh returned `No New Games`.

This closes the metadata/artwork-enrichment branch.

## Protected baseline carried into this work

The branch started from the cumulative CLASSIC baseline already hardware-confirmed through Test52 and preserved:

- Mapper v19;
- Audio OSD v8;
- generalized CLASSIC importer;
- normalized `/cores/classic-mame2000/core.xgc` runtime layout;
- stable Refresh / `No New Games` behavior;
- CLASSIC Save/Load;
- stock consoles and stock Arcade behavior.

Protected MAME2000 core SHA-256:

```text
60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

The core was not changed by this branch.

## Major branch milestones

### Test53 — title metadata + raw RGB565 artwork

Hardware PASS.

New CLASSIC games can be staged as:

```text
/CLASSIC/bin/<shortname>.zip
/CLASSIC/meta/<shortname>.txt
/CLASSIC/art/<shortname>.rgb565
```

The first line of the metadata text file supplies the friendly UI/wrapper title while the original ROM shortname remains the runtime identity.

Exact 144 x 208 little-endian RGB565 artwork is supported.

### Test57 — CLASSIC logo atlas fix

Hardware PASS.

The fifth-page/CLASSIC strip corruption was traced to the stock `Resources/ihdsf.bke` atlas containing 11 336 x 64 slots while CLASSIC state 11 requires a twelfth slot. A 12th CLASSIC slot was appended without modifying `Resources/clssic.r56`.

### Test58 — deletion reconciliation

Hardware PASS.

Refresh now removes catalog entries whose generated wrapper or embedded ROM relationship no longer exists, while retaining malformed/manual wrappers rather than deleting them speculatively.

### Test60 — stable external Refresh helper

Hardware PASS.

The Refresh engine was moved to `/CLASSIC/refresh.xgc`, loaded by a small firmware bootstrap. Final catalog-byte comparison restored correct unchanged behavior:

```text
first Refresh after a real change -> Games Updated
next unchanged Refresh             -> No New Games
```

`/CLASSIC/refresh.xgc` is therefore a required runtime component and must not be deleted while cleaning generated `.zfb` wrappers.

### Test61 — on-device RGB565 resize/letterbox

Hardware PASS.

A 320 x 224 RGB565 Shinobi source image was resized on-device to the 144 x 208 preview contract with aspect preservation and black letterboxing. Existing exact-size 144 x 208 RGB565 remains supported.

### Test64 — integrated on-device JPEG conversion

Hardware PASS.

Artifact:

```text
xgo-classic-test64-integrated-jpeg-refresh.zip
ZIP SHA-256: 09ce9cd0a983f4a2887a5050718e30e55fe487dcb8ecc15b16f2b6c184676d3d
firmware SHA-256: 0fb8dda0f03b3a8068b23a02d03354475538be0c8e7ed83d8f2ee5d69ab57fef
refresh.xgc SHA-256: 6d416c71af871445023de96522d78bfa62b6277cfb7e5e37945bc12ea76dc98d
```

The on-device Refresh path now supports ordinary baseline/non-progressive JPEG artwork:

```text
/CLASSIC/art/<shortname>.jpg
        -> JPEG decode on-device
        -> aspect-fit / letterbox
        -> 144 x 208 RGB565
        -> stock-style .zfb preview prefix
```

PNG support was investigated in Tests65-70 and deliberately dropped from scope. JPG is the supported ordinary image format.

### Test72 — full 50-game batch validation

Hardware PASS for the complete batch import path.

Artifact used:

```text
xgo-classic-test72-one-shot-batch-import.zip
ZIP SHA-256: af14ce8eb2e111386873ad697e1c4654ea2dcde663be5410bfd5a71f36fa4a16
```

The final test SD contained 50 matching ROM / JPG / TXT sets. Refresh successfully:

- consumed all 50 metadata titles;
- converted all 50 JPG images to RGB565 on-device;
- created the friendly-title `.zfb` wrappers;
- left the ROM ZIPs intact;
- preserved game launch behavior;
- remained responsive;
- returned `No New Games` on a second unchanged Refresh.

Observed post-run state included 50 JPG sources, 50 generated RGB565 files, 50 metadata TXT files, and the generated `.zfb` wrappers.

## Cleanup decision

Automatic deletion of JPG, RGB565, and metadata TXT sidecars is **not part of the protected final behavior**.

During Test72 development, cleanup logic was exploratory and did not remove the files in the hardware-passed batch. The retained files are small enough to be practical and provide a useful editable source library for future rebuilds.

This is now the preferred steady state:

```text
/CLASSIC/bin/       original ROM ZIPs
/CLASSIC/art/       editable JPG source + generated RGB565 cache
/CLASSIC/meta/      editable friendly-title TXT files
/CLASSIC/*.zfb      generated stock-style wrappers
/CLASSIC/save/      save states
/CLASSIC/refresh.xgc
```

Do not add destructive cleanup to the protected baseline unless it is separately proven and explicitly desired.

## Final conclusions

The CLASSIC subsystem now has a practical on-device content-management workflow rather than a bare filename scanner:

- ROM shortnames remain stable runtime identities;
- friendly display titles are user-editable through TXT sidecars;
- ordinary JPG artwork is accepted directly on the SD card;
- artwork is decoded, resized, letterboxed, and converted on-device;
- stock-style wrappers embed the final preview;
- deletion reconciliation works;
- Refresh is externalized and maintainable;
- unchanged Refresh is stable;
- a 50-game real-world batch is hardware-proven.

After 72 experimental builds, this branch is closed. The next priority is the remaining Pac-Man / Ms. Pac-Man CLASSIC load-path discrepancy, to be investigated on a clean branch from the merged cumulative baseline.
