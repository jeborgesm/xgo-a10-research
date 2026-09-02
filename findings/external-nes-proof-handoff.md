# External NES proof — branch handoff

## Branch outcome

This branch proved that the XGO A10 / XGO Plus can load and execute a native external libretro NES core from SD and run real gameplay through the stock XGO frontend services.

Hardware-proven path:

```text
stock NES menu
  -> stock ROM preload
  -> patched NES launch call site
  -> injected loader @ 0x80001500
  -> /cores/fceumm/core.xgc
  -> external entry @ 0x87000000
  -> external FCEUmm
  -> GP-safe stock video/audio/input services
  -> stock exit/save-state UI
```

## Proven on hardware

Using the same Contra ROM throughout bring-up:

- XGOC validation/read/CRC/load succeeds
- external entry and return semantics are correct
- external newlib/runtime initialization succeeds
- bidirectional stock/external `$gp` transition works for the exercised lifecycle
- stock-preloaded ROM can be handed directly to FCEUmm
- `retro_init()` succeeds
- `retro_load_game()` succeeds
- stock AV setup succeeds
- `retro_run()` executes continuously
- video callback works
- stereo audio callback works
- stock input callback works
- gameplay/timing are normal by observation
- `Select+Start` exits normally
- exit reaches the stock XGO save-state UI

The tested full-path core was produced from source commit `04ee153bfaf685241dbfbe5d899e74137014cc2c`; subsequent documentation commits do not change that successful runtime payload.

## Final blocker found before success

The Stage-6 transactional ladder produced:

- 51 PASS — GAME_INFO write/restore
- 52 PASS — GFN slot install/restore
- 53 FAIL — first call to `retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD)`

Pinned FCEUmm defines `RETRO_DEVICE_AUTO == RETRO_DEVICE_JOYPAD`. Its pre-load Auto path reads `GameInfo->input[port]` before `retro_load_game()` has established `GameInfo`. Both explicit pre-load controller calls were removed. FCEUmm initializes its normal NES gamepad ports after successful ROM load, making the calls both unsafe and redundant.

## Known limitations intentionally left for follow-up

### Save states

The stock save-state UI is reached correctly, but save/load itself is disabled. `GFN_STATE_SAVE` and `GFN_STATE_LOAD` currently point through `xgo_core_state_io` to `xgo_disabled_state_io()`, which returns 0.

Follow-up should implement a generic state bridge around libretro `retro_serialize_size()`, `retro_serialize()`, and `retro_unserialize()` while preserving the stock XGO path/file contract.

### Video black level

Direct A/B comparison with an original unmodified SD card shows the external FCEUmm image has a raised black level: black areas appear gray and the overall image is somewhat brighter. Gameplay geometry and color identity are otherwise normal.

Follow-up should determine whether the difference originates in FCEUmm palette generation/RGB565 packing or in emulator-specific stock display setup.

## Architecture that should be generalized next

The reusable pieces are:

- XGOC loader and executable-memory handoff
- external `$gp` entry veneer
- stock -> external and external -> stock GP-safe veneers
- exact HC15xx Codescape toolchain/build closure
- stock video/audio/input callback adapters
- minimal controlled environment shim
- stock ROM-buffer handoff
- stock `run_emulator()` function-slot integration

The current source still contains NES/FCEUmm-specific assumptions. Do not copy those assumptions wholesale into the next core.

## Recommended next branch

`research-generic-libretro-runtime`

Goals, in order:

1. extract a core-neutral XGO libretro runtime from the proven NES implementation
2. document and normalize physical XGO button -> libretro joypad mapping
3. implement generic libretro serialization/save-state bridging
4. resolve or characterize shared RGB565/black-level behavior
5. add SNES as the second external core to prove that the runtime is genuinely multicore rather than an FCEUmm-specific integration

SNES is the recommended second core because it stresses more buttons, different geometry/timing, heavier CPU load, and larger serialization state while remaining a well-understood libretro target.

## Research rules carried forward

- hardware observations outrank static assumptions
- treat similar SF2000 code as comparison evidence, not XGO authority
- preserve O32 calling convention details, including stack-passed arguments
- never assume a function is GP-independent because its address is correct
- account for synthetic raw-firmware ELF address bias before interpreting disassembly PCs
- prefer behavior-based continuity probes over diagnostics that depend on unproven display/filesystem paths
- restore borrowed stock globals before interpreting an early-return probe

This branch should be considered the architectural proof that native external-core execution is viable on XGO A10 hardware.
