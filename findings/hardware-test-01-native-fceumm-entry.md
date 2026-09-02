# Hardware test 01: native FCEUmm entry reaches external path and returns early

Date: 2026-09-02

Branch: `research-external-core-integration`

## Test setup

A disposable clone of the known-good XGO SD card was first boot-tested unchanged. The GP-safe native NES overlay was then applied. The modified firmware booted normally and the stock menu remained usable before launching NES content.

Test content included a known-good Contra `.nes` title from the stock NES browser and a `.nes` title launched from User Games.

## Observed behavior

For both launch paths:

1. the normal NES loading transition began;
2. execution returned quickly to the NES selection/menu instead of entering gameplay;
3. menu music remained muted after the return;
4. pressing the volume button caused menu music to resume.

The device did not crash, reboot, or become unresponsive.

## What the observation proves

The muted menu music is direct behavioral evidence that the patched NES path reached the native loader far enough to execute the loader's stock-matching sound-task stop sequence. That sequence clears bit 0 of `g_snd_task_flags` at `0x80c2e80c` and waits for the sound task to quiesce before upper-RAM takeover.

Because the loader's pre-entry validation failures fall back to untouched stock `run_nes()` (`0x8035f63c`), an immediate menu return with sound still stopped is more consistent with successful loader progression into the external image followed by an early return from the native frontend than with a missing/invalid XGOC file.

This is therefore a positive partial-execution result: the firmware interception, loader invocation, and sound-task sequencing are confirmed on real XGO hardware.

## First live ABI defect identified

The native frontend revision used in Test 01 reopened the selected ROM solely to recover its exact byte count because stock `run_game()` rounds `g_run_file_size` upward to a four-byte boundary. The helper called stock `fopen`, `fseeko`, `ftell`, and `fclose` through GP-switching veneers.

The helper incorrectly declared stock `fseeko` as:

```c
int xgo_stock_fseeko(FILE *, int, int);
```

XGO firmware machine code proves that `fseeko` at `0x802b37e4` uses a 64-bit offset under the O32 ABI. Its call sites place the aligned 64-bit offset in `a2/a3` and the fifth argument (`whence`) at caller `sp+16`.

Therefore the Test 01 helper had both an incorrect C prototype and a stack-sensitive call boundary. This is the strongest explanation for the only explicit early return in the native C frontend before `run_emulator()`.

## Upstream comparison

SF2000 Multicore also uses `fseeko` while loading content for cores that do not require full paths. However, that call occurs inside its own runtime/frontend compilation environment, where the standard `fseeko` prototype and ABI are native to the build. The XGO frontend had instead crossed from external code into a preserved stock-firmware implementation and therefore had to preserve the stock O32 ABI explicitly.

Pinned FCEUmm commit `e6111e684e7a7761f3f1d6c80d0a825e2c8cdc7e` makes the extra seek unnecessary for iNES/NES2 ROMs. Its in-memory wrapper records the supplied buffer size, while the iNES loader derives PRG+CHR sizes from the NES header. If the supplied buffer is a few bytes larger than the header-declared content, FCEUmm reports the difference as unused trailing data and continues loading.

Since stock XGO only rounds the preloaded size upward by at most three bytes, the already-populated `g_run_file_size` is sufficient for the in-memory FCEUmm path.

## Fix after Test 01

Commit `5e18906a5faa11d0a03a72c2cc540823def15d16` removes the ROM reopen/seek/size helper from the launch-critical path. The native frontend now:

- validates `gp_buf_64m` and the existing `g_run_file_size`;
- passes the stock-preloaded ROM buffer directly to FCEUmm;
- uses the stock aligned length as the memory-stream size;
- performs no second ROM open, seek, read, copy, or allocation.

This also makes the intended handoff strictly simpler:

`SD -> stock run_game preload -> gp_buf_64m -> FCEUmm memory stream`

## Current interpretation

Test 01 is not a failed loader experiment. It is the first hardware confirmation that the native interception path executes and returns safely enough to preserve the menu. The next test should use a rebuilt XGOC containing commit `5e18906` while retaining the same patched firmware/loader unless build geometry requires otherwise.
