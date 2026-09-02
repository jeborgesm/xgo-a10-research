# Hardware Test 08 — return-ladder boundary

Physical XGO result using the six-stage FCEUmm return ladder on the experimental SD card:

- Stage 1: returns to game menu
- Stage 2: returns to game menu
- Stage 3: returns to game menu
- Stage 4: returns to game menu
- Stage 5: returns to game menu
- Stage 6: remains frozen at `Loading...`

## What this proves

The hardware survives, in sequence:

1. external core entry and external `$gp` installation;
2. external newlib/reentrancy/constructor initialization;
3. reads of stock ROM/global state;
4. FCEUmm libretro callback setter calls;
5. `retro_init()` through completion and return.

Therefore the persistent freeze is **not** in any of those layers.

## Narrow suspect window

Stage 5 returns immediately after `retro_init()`.
Stage 6 returns only after the following additional work:

```c
GAME_INFO.path = filename;
GAME_INFO.data = ROM_BUFFER;
GAME_INFO.size = rom_size;
GAME_INFO.meta = 0;

GFN_STATE_LOAD = xgo_core_state_io;
GFN_STATE_SAVE = xgo_core_state_io;
GFN_GET_REGION = xgo_core_get_region;
GFN_GET_AV = xgo_core_get_av;
GFN_LOAD_GAME = xgo_core_load_game;
GFN_UNLOAD_GAME = xgo_core_unload_game;
GFN_RUN = xgo_core_run;
GFN_FRAMESKIP = 0;

retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD);
retro_set_controller_port_device(1, RETRO_DEVICE_JOYPAD);
```

Since Stage 6 never reaches its deliberate return, the failure is introduced somewhere in this exact block.

The next hardware probe should subdivide this window only:

- 5A — return after `GAME_INFO` writes;
- 5B — return after `GFN_*` slot writes;
- 5C — return after controller-port 0 setup;
- 5D — return after controller-port 1 setup.

This is now a deterministic hardware boundary; no file/video diagnostic channel is required.
