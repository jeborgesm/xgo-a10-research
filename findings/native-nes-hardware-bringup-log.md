# Native NES hardware bring-up log

Status: **active physical-device investigation**.

This file records observations from the first XGO native NES/FCEUmm hardware tests. The disposable SD clone boots normally before and after applying the native NES overlay; the untouched stock card remains preserved.

## Test 1 — first GP-safe candidate

Hardware observation:

- normal XGO UI boots and behaves normally before NES launch;
- selecting a known-good Contra `.nes` shows the normal loading transition, then immediately returns to the NES selection menu;
- menu music remains muted until the volume button is pressed;
- the same behavior occurs for NES content launched through User Games.

Interpretation:

- the patched NES dispatch is being reached far enough to stop the stock sound task;
- the machine returns rather than crashing;
- investigation found an unnecessary `exact_rom_size()` helper whose stock `fseeko` declaration/bridge did not preserve the real O32 64-bit calling convention.

The helper was removed; FCEUmm can safely consume the stock preloaded aligned ROM size because ordinary iNES/NES2 declared payload sizes tolerate the XGO's 0-3 bytes of alignment padding.

## Test 2 — remove exact-ROM-size stdio path

Hardware observation:

- selecting the same Contra ROM remains on the `Loading...` screen indefinitely;
- controls no longer return to the menu;
- a power cycle is required.

Interpretation:

- execution progressed beyond the Test 1 early return;
- the failure moved into later external-core initialization / stock `run_emulator` lifecycle.

## Test 3 — constrain environment / raw callback escape

Static investigation found that forwarding `RETRO_ENVIRONMENT_GET_LOG_INTERFACE` to the old stock frontend could expose a raw stock logger pointer to external FCEUmm. Such a pointer would bypass the core->stock GP veneer when called under external `_gp`. The environment boundary was tightened and libretro boolean-output handling corrected.

Hardware observation:

- behavior is unchanged from Test 2: frozen indefinitely on `Loading...`, requiring a power cycle.

Interpretation:

- the logger-pointer defect was real ABI risk but was not the complete cause of the observed freeze.

## Test 4 — SD trace instrumentation

The diagnostic frontend added fixed-string checkpoints around:

- external C entry;
- newlib runtime initialization;
- ROM validation;
- `retro_init`;
- entry to stock `run_emulator`;
- `retro_load_game`;
- AV-info callback;
- region callback;
- first `retro_run`;
- unload/deinit/return.

The tracer deliberately avoided `printf` and malloc, using GP-wrapped stock `fs_open`, `fs_write`, and `fs_close` calls against `/mnt/sda1/xgo-native.log`.

Hardware observation:

- no `xgo-native.log` was created;
- as a control, an empty `xgo-native.log` was manually created in the SD root and the same test repeated;
- after the frozen launch, the manually created file remained completely empty;
- NES still does not load.

Interpretation:

- the SD tracer is not a usable observability channel in its current raw-VFS form;
- an empty file does **not** prove that external C entry was never reached, because the first diagnostic operation itself crosses the unproven raw `fs_open/fs_write` ABI;
- further bring-up must not use the file tracer as evidence of execution stage.

## Next diagnostic boundary

The next probe should remove filesystem I/O from the diagnostic path entirely.

The stock XGO video transport is already reverse-engineered and confirmed to accept RGB565 frames through `retro_video_refresh_cb @ 0x8035e70c`, which forwards into the XGO OSD/scaler/display stack. A controlled diagnostic core can therefore submit synthetic RGB565 stage frames through the existing GP-safe video veneer.

The probe should minimize moving parts:

1. establish a visible marker immediately after external C entry, before newlib initialization;
2. change the marker after runtime initialization;
3. change it before/after `retro_init`;
4. change it before entering stock `run_emulator`;
5. use stock->core diagnostic wrappers to change markers on `retro_load_game`, AV, region, and first `retro_run` boundaries.

The first version should prefer unmistakable solid-color/pattern markers over text rendering so no font, printf, allocation, or filesystem dependency is introduced into the debugger.
