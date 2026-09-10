# CLASSIC Test52 Save/Load — Hardware PASS

Date: 2026-09-10

Branch: `research-game-list-arcade-expansion`

## Result

Test52 is hardware-confirmed PASS for CLASSIC save/load.

Tested games:

- Pac-Man — Save PASS, Load PASS, state restored correctly.
- Galaga — Save PASS, Load PASS, state restored correctly.

Observed latency is approximately 3 seconds for Save and Load, versus about 1 second for the stock emulator families. This is accepted behavior for the current implementation.

## Architecture

The hardware-proven CLASSIC MAME2000 core is left byte-for-byte unchanged.

Canonical core path:

```text
/cores/classic-mame2000/core.xgc
```

Protected core SHA-256:

```text
60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e
```

Test52 changes only firmware behavior. The CLASSIC Save/Load callbacks run on the stock firmware side and stream the live MAME2000 runtime snapshot to/from SD rather than depending on the core's nonfunctional libretro serialization stubs.

The implementation automatically ensures:

```text
/mnt/sda1/CLASSIC/save/
```

exists before opening the sidecar snapshot.

## Files

Hardware-tested artifact:

```text
xgo-classic-test52-save-dir-fix.zip
SHA-256: f7aa1ebb7509913d389bc5922011c80795d4e5ec056f312800fe6ba3a02b78d4
```

Firmware:

```text
bios/bisrv.asd
SHA-256: 8475cfdbec0e334d226d13e29c69bbd71dc99e5736b3ef185d4afdd360b91189
```

Normalized Test47 dependency baseline:

```text
xgo-classic-mame2000-normalized-test47-baseline.zip
SHA-256: 59f23688770588b7ea0670d5ffa167097a5a7b7ca8be6d6c1d6674bba8b14d36
```

Both artifacts are preserved in the private vault under `golden/`.

## Branch closure status

The branch's two final gates are satisfied:

1. Generalized CLASSIC importer — Test47 hardware PASS.
2. CLASSIC Save/Load — Test52 hardware PASS on Pac-Man and Galaga.

Refresh remains hardware-proven, including stable `No New Games` behavior. The normalized CLASSIC naming/layout remains in use.

`research-game-list-arcade-expansion` is ready to merge to `main` and close.
