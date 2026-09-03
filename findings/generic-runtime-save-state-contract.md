# Generic external-core save-state contract

Status: **stock contract confirmed; implementation path identified; hardware implementation pending**.

## Headline

The XGO stock in-game save-state UI does not require an emulator-specific state format. It delegates state persistence through two function-pointer slots:

```text
GFN_STATE_SAVE = 0x80c33a70
GFN_STATE_LOAD = 0x80c33ac0
```

The hardware-proven external FCEUmm frontend already installs a GP-safe external veneer in both slots, but that veneer currently reaches `xgo_disabled_state_io()` and deliberately returns failure. This exactly explains the observed hardware behavior: Select+Start exits external FCEUmm into the normal stock save-state UI, while an attempted state operation cannot succeed.

The next implementation can therefore be generic: bridge the stock path callback to the standard libretro serialization API rather than add FCEUmm-specific save-state logic.

## Current XGO path

The successful external frontend does:

```text
GFN_STATE_LOAD = xgo_core_state_io;
GFN_STATE_SAVE = xgo_core_state_io;
```

`xgo_core_state_io` is a stock-GP -> external-GP veneer. At present it targets:

```c
int xgo_disabled_state_io(const char *path)
{
    (void)path;
    return 0;
}
```

Thus the GP crossing needed for save-state callbacks is already structurally solved. Save/load only needs separate external targets and persistence logic.

## Libretro contract

A generic libretro core provides:

```c
size_t retro_serialize_size(void);
bool retro_serialize(void *data, size_t size);
bool retro_unserialize(const void *data, size_t size);
```

This is sufficient to implement the XGO's two frontend callbacks independently of the emulator core.

### Save

Conceptually:

```text
stock save UI
  -> GFN_STATE_SAVE(path)
  -> stock->external GP veneer
  -> generic state_save(path)
  -> retro_serialize_size()
  -> allocate state buffer
  -> retro_serialize(buffer, size)
  -> persist bytes
  -> return stock success/failure
```

### Load

```text
stock load UI
  -> GFN_STATE_LOAD(path)
  -> stock->external GP veneer
  -> generic state_load(path)
  -> read state bytes
  -> retro_unserialize(buffer, size)
  -> return stock success/failure
```

## SF2000 Multicore comparison

Pinned SF2000 Multicore `core_api.c` independently uses exactly this architecture: its wrapped `retro_load_game()` assigns `gfn_state_load = state_load` and `gfn_state_save = state_save`; the handlers persist buffers produced by `retro_serialize()` and restore them through `retro_unserialize()`.

This is useful lineage evidence, but the XGO implementation should not be copied blindly.

Important XGO-specific differences already established by hardware bring-up include:

- stock/external `$gp` must be bridged explicitly in both directions;
- stock stdio/filesystem calls also require stock-GP veneers;
- XGO's stock ROM is already preloaded and handed directly to the external core;
- the original XGO frontend path/slot behavior should be preserved where practical;
- SF2000 Multicore rewrites state filenames into `/mnt/sda1/ROMS/save/<basename>.state<slot>`, while XGO's exact stock path argument is not yet documented strongly enough to assume the same transformation is required.

Therefore the first XGO implementation should inspect/preserve the path supplied by the stock UI rather than import the SF2000 path-rewrite policy as an assumption.

## Implementation design

The generic runtime should expose two distinct external functions:

```c
int xgo_core_state_save(const char *frontend_path);
int xgo_core_state_load(const char *frontend_path);
```

and two corresponding stock->external GP veneers. Do not keep a single `xgo_core_state_io` target once real serialization is enabled.

The state implementation should:

1. reject null/empty paths;
2. obtain `retro_serialize_size()` and reject zero/unreasonable sizes;
3. allocate exactly the required state buffer;
4. propagate `retro_serialize()` / `retro_unserialize()` failure;
5. verify file open/read/write results rather than assuming success;
6. free all buffers on every exit path;
7. return the stock frontend's expected integer success convention (`1` success, `0` failure), consistent with the SF2000-family frontend contract;
8. keep all stock filesystem calls behind existing GP-safe veneers;
9. preserve the caller-provided stock path until hardware evidence shows a translation is necessary.

## Why this belongs in the generic runtime

Nothing in this contract is NES- or FCEUmm-specific. Once implemented correctly, any libretro core with working serialization can participate in the stock XGO save-state UI.

That makes save states a useful abstraction test before SNES:

```text
FCEUmm proof
  -> generic serialization bridge
  -> verify save + load on NES hardware
  -> reuse unchanged for SNES Core #2
```

If SNES later needs special handling, that should be treated as a core quirk layered above this contract rather than built into the XGO runtime by default.

## Hardware test required

A first save-state implementation should be tested conservatively on the known-working FCEUmm build:

1. launch the same known-good NES ROM;
2. reach a visually unmistakable game state;
3. Select+Start into the stock state UI;
4. save to one slot;
5. resume and alter game state;
6. return to stock state UI;
7. load the saved slot;
8. confirm restoration of game state;
9. reboot/relaunch and test persistent load if the stock UI permits it;
10. inspect the SD card afterward to document the actual filename/path/size produced.

The SD-card inspection is part of the research result: it will establish the XGO's real state-file persistence contract instead of inferring it from SF2000.

## Conclusion

The observed save-state failure in the first external FCEUmm build is not an unknown compatibility defect. It is the direct and expected result of a deliberately disabled callback.

The stock UI boundary, callback slots, GP crossing, and standard libretro serialization mechanism are now sufficiently understood to implement save/load as a **generic runtime service**.
