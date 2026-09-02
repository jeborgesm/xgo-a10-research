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

## Test 5 — full-frame visual stage probe

The SD tracer was removed. A 256x240 RGB565 framebuffer encoded stage numbers as binary black/white bars plus a stage-specific full-screen color. The marker was submitted through the GP-safe stock `retro_video_refresh_cb` beginning immediately after external C entry, before newlib initialization.

Hardware observation:

- selecting Contra shows the ordinary `Loading...` screen;
- the display then becomes completely black;
- no stage bars or stage color are visible;
- the system remains non-responsive and requires a power cycle.

Interpretation:

The callback address was re-audited against raw firmware. A temporary apparent mismatch was traced to a **+0x30 PC bias in the local ELF wrapper used for disassembly**: `fw_start` is linked at `0x80000030`. After correcting that bias, the established runtime callback entries remain valid. See `findings/raw-firmware-disassembly-address-bias.md`.

The black screen instead matches `run_screen_write` behavior. Before writing a frame it compares incoming width/height with cached display geometry. On a mismatch it closes the current OSD path, delays 200 ticks, recreates the region, then resumes writing. Sending a 256x240 emulator-style frame while the menu/loading UI still owns the display can therefore tear down the current display path before the diagnostic becomes visible.

Test 5 consequently does **not** establish an execution stage; it establishes that the normal video-refresh path is a poor pre-`run_emulator` debugger because it performs geometry management.

## Test 6 — current-region visual probe

The next diagnostic removes geometry switching from the marker path. It uses the already-mapped `run_osd_region_write @ 0x8035c31c` through a GP-safe veneer and writes only a 128x64 RGB565 patch into the currently active OSD region.

The patch encodes:

- top half: eight 16-pixel binary bars, least-significant bit first;
- bottom half: stage-specific color.

Normal FCEUmm video remains wired to `retro_video_refresh_cb`; only the diagnostic markers use the direct current-region writer.

This test is intended to distinguish external-entry/runtime/libretro lifecycle stages without closing or resizing the loading UI's OSD path.
