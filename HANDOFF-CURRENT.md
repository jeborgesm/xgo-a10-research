# HANDOFF-CURRENT

## Current checkpoint — 2026-09-10

The `research-game-list-arcade-expansion` branch is complete and ready to merge.

### Hardware-proven final state

Generalized CLASSIC importer:

```text
TEST47 — PASS
xgo-classic-test47-general-importer.zip
SHA-256: d40a811e2ef05788688fe516e520b3f11b2e5b08ca77d926e77bf1c224f5db53
```

Normalized CLASSIC baseline:

```text
xgo-classic-mame2000-normalized-test47-baseline.zip
SHA-256: 59f23688770588b7ea0670d5ffa167097a5a7b7ca8be6d6c1d6674bba8b14d36
```

Canonical runtime layout:

```text
/CLASSIC/
/CLASSIC/bin/
/CLASSIC/save/
/cores/classic-mame2000/core.xgc
/bios/classic-mame2000/
```

Protected CLASSIC MAME2000 core:

```text
/cores/classic-mame2000/core.xgc
SHA-256: 60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

The misleading legacy runtime names `fbalpha2012_cps1` and `mame2000_xgo_t12` are no longer part of the active layout. Historical documents may still mention them where they accurately describe older tests.

CLASSIC Save/Load:

```text
TEST52 — PASS
xgo-classic-test52-save-dir-fix.zip
SHA-256: f7aa1ebb7509913d389bc5922011c80795d4e5ec056f312800fe6ba3a02b78d4
firmware SHA-256: 8475cfdbec0e334d226d13e29c69bbd71dc99e5736b3ef185d4afdd360b91189
```

Hardware confirmation:

- Pac-Man Save PASS.
- Pac-Man Load PASS with correct state restoration.
- Galaga Save PASS.
- Galaga Load PASS with correct state restoration.
- Save/Load latency is approximately 3 seconds and is accepted for this streamed firmware-side implementation.
- CLASSIC games still launch normally.
- 40+ imported CLASSIC games remain present and playable.
- Refresh remains functional.
- Repeated Refresh reaches stable `No New Games` without freezing.
- Stock console lists remain unaffected.
- Stock Arcade remains unaffected.
- Volume OSD remains intact.

### Save-state architecture

Do not re-open Test48/Test49 unless a new research question specifically requires it.

Test48 and Test49 both failed because replacement MAME2000 cores regressed at the game-launch boundary. The final solution deliberately leaves the hardware-proven MAME2000 core byte-for-byte unchanged.

Test52 installs CLASSIC-specific Save/Load callbacks on the firmware side. Those callbacks stream the live MAME2000 runtime snapshot directly to SD and restore it from SD. The implementation automatically ensures `/mnt/sda1/CLASSIC/save/` exists before opening the sidecar snapshot.

This bypasses the pinned MAME2000 core's nonfunctional libretro serialization stubs without rebuilding the core.

Primary finding:

```text
findings/classic-test52-save-load-hardware-pass.md
```

### Golden preservation

Private vault:

```text
jeborgesm/xgo-a10-artifacts
```

Golden paths:

```text
golden/xgo-classic-mame2000-normalized-test47-baseline.zip
golden/xgo-classic-test52-save-dir-fix.zip
```

### Branch closure

`research-game-list-arcade-expansion` has satisfied its final gates and should be merged to `main`.

After merge, begin the next task from a fresh branch created from the merged `main`. Do not carry forward Test48/Test49 experimental core replacements as active dependencies.
