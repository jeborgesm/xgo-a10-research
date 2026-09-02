# Hardware finding: pre-load FCEUmm controller setup dereferences null GameInfo

## Status

Confirmed by transactional hardware bisection on XGO A10 and pinned FCEUmm source analysis.

Pinned FCEUmm revision:

- `e6111e684e7a7761f3f1d6c80d0a825e2c8cdc7e`

## Hardware evidence

The Stage-6 transactional ladder subdivided the previously ambiguous frontend setup window. Each checkpoint restored borrowed stock globals before returning, so a clean return to the NES list proves that checkpoint itself completed without leaving the stock frontend poisoned.

Observed on hardware with the same Contra ROM and patched firmware:

- substage 51: **PASS** — write/restore stock `GAME_INFO`
- substage 52: **PASS** — additionally install/restore all external `GFN_*` slots
- substage 53: **FAIL** — first added operation is `retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD)`

The failure therefore occurs before stock `run_emulator()` is entered.

## Source-level root cause

Pinned FCEUmm defines:

```c
#define RETRO_DEVICE_AUTO RETRO_DEVICE_JOYPAD
```

Its `retro_set_controller_port_device()` implementation treats plain `RETRO_DEVICE_JOYPAD` as **Auto**. For ports 0 and 1, the Auto path evaluates:

```c
update_nes_controllers(port, nes_to_libretro(GameInfo->input[port]));
```

At the XGO frontend's pre-load call site, FCEUmm `GameInfo` has not yet been established. It is assigned only after `FCEUI_LoadGame()` succeeds inside `retro_load_game()`. Thus the substage-53 call dereferences `GameInfo` before game load.

Changing the argument to FCEUmm's explicit `RETRO_DEVICE_GAMEPAD` subclass would not make pre-load setup safe. `update_nes_controllers()` calls `FCEUI_SetInput()`, which reaches `SetInputStuff()`. The `SI_GAMEPAD` case also evaluates `GameInfo->type` without a null guard.

Therefore the actual lifecycle rule for this pinned core is:

> Do not call `retro_set_controller_port_device()` for a gamepad before `retro_load_game()` has successfully established FCEUmm `GameInfo`.

## Why no replacement pre-load controller call is needed

Pinned FCEUmm already initializes both normal NES ports immediately after successful `FCEUI_LoadGame()`:

```c
for (i = 0; i < MAX_PORTS; i++) {
   FCEUI_SetInput(i, SI_GAMEPAD, &nes_input.JSReturn, 0);
   nes_input.type[i] = RETRO_DEVICE_JOYPAD;
}
```

The XGO frontend's two explicit pre-load controller calls were therefore both unsafe and redundant.

## Production correction

`tools/multicore/native_nes/xgo_nes_native_frontend.c` now omits both pre-load calls and leaves controller initialization to FCEUmm's normal post-load path.

This does **not** disable XGO input. The existing stock input callback remains registered through `retro_set_input_state(xgo_stock_input_state)`, and FCEUmm configures its NES gamepad devices after the ROM is loaded.

## Consequence for the previous Stage-6 interpretation

The earlier Stage-6 freeze must not be attributed to the stock `run_emulator()` transition. Transactional substages 51 and 52 passed, while 53 failed before `run_emulator()`. The first proven blocker in that window is the premature FCEUmm controller-device call.

The next hardware candidate should use the production frontend with those calls removed and then test the next real boundary: stock `run_emulator()` invoking the reverse-GP `retro_load_game` path.
