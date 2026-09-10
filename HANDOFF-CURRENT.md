# HANDOFF-CURRENT

## Current checkpoint — 2026-09-10

Active branch:

```text
research-next
```

Created from merged `main` commit:

```text
7bef32b9953fd0b5d477b644563f6a62eabef9d2
```

The previous branch `research-game-list-arcade-expansion` is closed and merged through PR #43.

## Protected golden baseline

The merged baseline is cumulative. Future work must preserve the already hardware-confirmed button-mapping, Audio OSD, game-list, CLASSIC importer, and CLASSIC Save/Load behavior unless a new task explicitly requires changing one of those subsystems.

### Interactive button mapping — Mapper v19

The hardware-confirmed interactive button mapper is part of the protected baseline and must not be regressed.

```text
artifact ID: mapper-v19
xgo-interactive-mapper-v19-card.zip
SHA-256: c45925f965cf86b4e1efc622b02aabb5545122814743aaf7723d4dbf6ba4ec81
firmware SHA-256: 466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab
```

Protected behavior:

- Stock in-game pause menu includes the fifth `Mapper` option.
- Interactive button remapping remains functional.
- Existing per-game/button mapping behavior must survive future firmware work.
- Do not replace later cumulative firmware with a baseline that predates Mapper v19.

### Audio OSD

The final Audio OSD work remains part of the protected baseline and must remain intact.

```text
artifact ID: audio-osd-v8-button-event-only
xgo-audio-osd-v8-button-event-only-test.zip
SHA-256: ba3dad99471c6144fd8f6e9f5891bc88d44b955c5de8a21df905d0d396cdb83a
firmware SHA-256: 4b8f7af994d16371a2664a3d46c983e52ffd1aefbebc5b5a4a9ae63dc6cbe954
```

Protected behavior includes fine volume control, button-event-only transient OSD, gray border, correct timeout, and no boot-time false OSD.

### Generalized CLASSIC importer

```text
TEST47 — hardware PASS
xgo-classic-test47-general-importer.zip
SHA-256: d40a811e2ef05788688fe516e520b3f11b2e5b08ca77d926e77bf1c224f5db53
```

### Normalized CLASSIC runtime baseline

```text
xgo-classic-mame2000-normalized-test47-baseline.zip
SHA-256: 59f23688770588b7ea0670d5ffa167097a5a7b7ca8be6d6c1d6674bba8b14d36
```

### CLASSIC Save/Load overlay

```text
TEST52 — hardware PASS
xgo-classic-test52-save-dir-fix.zip
SHA-256: f7aa1ebb7509913d389bc5922011c80795d4e5ec056f312800fe6ba3a02b78d4
firmware SHA-256: 8475cfdbec0e334d226d13e29c69bbd71dc99e5736b3ef185d4afdd360b91189
```

Protected CLASSIC MAME2000 core:

```text
/cores/classic-mame2000/core.xgc
SHA-256: 60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

Canonical CLASSIC layout:

```text
/CLASSIC/
/CLASSIC/bin/
/CLASSIC/save/
/cores/classic-mame2000/core.xgc
/bios/classic-mame2000/
```

Hardware-confirmed cumulative behavior:

- Mapper v19 interactive button mapping remains part of the baseline.
- Stock pause-menu `Mapper` option remains available.
- Volume OSD remains intact.
- 40+ CLASSIC games present and playable.
- Refresh works.
- Repeated Refresh reaches stable `No New Games` without freezing.
- Pac-Man Save/Load works.
- Galaga Save/Load works.
- CLASSIC Save/Load takes about 3 seconds; accepted behavior.
- The MAME2000 core remains byte-for-byte unchanged by the final save-state solution.
- Stock consoles remain unaffected.
- Stock Arcade remains unaffected.

Golden private-vault paths include:

```text
golden/xgo-interactive-mapper-v19-card.zip
golden/xgo-audio-osd-v8-button-event-only-test.zip
golden/xgo-classic-mame2000-normalized-test47-baseline.zip
golden/xgo-classic-test52-save-dir-fix.zip
```

Primary final CLASSIC finding:

```text
findings/classic-test52-save-load-hardware-pass.md
```

## Next scope

No next research item has been selected yet.

Start the next item from `research-next` and preserve the entire cumulative merged golden baseline above unless the new task explicitly requires changing it.
