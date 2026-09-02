# Hardware test 07: loader/XGOC/entry/return round-trip proven

Date: 2026-09-02

Branch: `research-external-core-integration`

## Purpose

After repeated attempts to observe the full native FCEUmm path with file and video diagnostics produced no reliable checkpoint, the experiment was reduced to the smallest possible external core.

The continuity payload contains exactly four MIPS instructions / 16 bytes at `0x87000000`:

```asm
lui  v0,0x5847
ori  v0,v0,0x4f31
jr   ra
nop
```

It returns the magic value `0x58474f31` (`XGO1`) and performs no other work.

The exact HC15xx Codescape build was validated by GitHub Actions run `33681850536`:

- entry address: `0x87000000`
- payload: 16 bytes
- runtime memory: 16 bytes
- payload CRC32: `0xa32e56f0`
- header CRC32: `0x05f1db5a`
- XGOC SHA-256: `aac9310c13d6330270e17b8fd417cfbfaefebfbdc197a2a46a7567c384ac7802`

## Hardware setup detail

The device retained the same `bios/bisrv.asd` used by the earlier FCEUmm tests. Only `/cores/fceumm/core.xgc` was replaced with the 48-byte XGOC containing the 16-byte payload.

This detail matters: the firmware on the SD card still contains the earlier loader, which does **not** implement the newer diagnostic `XGO1 -> stock_run_nes()` handshake currently present in branch source. Therefore a successful probe return is expected to fall through the original loader and return to the game list.

## Hardware observation

Selecting the same known-good Contra ROM produced:

1. normal `Loading...` transition;
2. no freeze;
3. immediate return to the NES games list.

This reproduces the visible shape of Test 01, but now with a payload whose only possible successful execution path is four deterministic instructions followed by `jr ra`.

## What this proves

The result establishes a clean hardware round trip through the external-core loader boundary:

`stock run_game -> patched NES dispatch -> loader -> XGOC open/header validation -> payload read -> payload CRC -> upper-RAM install -> IRQ repair/cache flush -> entry at 0x87000000 -> external instructions execute -> return to loader -> return to menu`

A pre-entry XGOC validation/load failure in the original loader would have invoked untouched stock `run_nes()` instead. The observed return to the game list therefore distinguishes successful external entry/return from loader fallback.

This materially changes the fault tree. The persistent freeze of the full native FCEUmm candidate is **not** explained by:

- inability to open `/mnt/sda1/cores/fceumm/core.xgc`;
- malformed XGOC framing;
- upper-RAM payload copy itself;
- basic cache coherence of the loaded entry code;
- inability to jump to `0x87000000`;
- inability for external code to return through `$ra` to the loader.

The remaining defect is above the minimal loader/entry boundary and can now be isolated by incrementally reintroducing external-runtime layers.

## New diagnostic method

The reliable hardware observable is now binary and does not depend on logging or display internals:

- **return to game list** = tested stage completed and external core returned;
- **freeze at `Loading...`** = tested stage did not return.

The next experiments should therefore form a staged return ladder, adding one boundary at a time:

1. production GP entry veneer -> trivial C function -> return;
2. external newlib/runtime initialization -> return;
3. callback installation/environment setup -> return;
4. `retro_init()` -> return;
5. content-info setup / ROM validation -> return;
6. `retro_load_game()` without stock `run_emulator()` -> return;
7. only then reintroduce the stock `run_emulator()` lifecycle.

This avoids further attempts to debug the debugger and should locate the first non-returning operation directly.
