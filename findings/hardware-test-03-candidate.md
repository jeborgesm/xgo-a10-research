# Hardware test 03 candidate: close stock environment callback escape

Date prepared: 2026-09-02

## Purpose

Hardware Test 02 advanced from Test 01's immediate return into a hard freeze while the stock UI remained on `Loading...`. Preserved XGO machine code localizes that screen to the `gfn_retro_load_game` callback inside stock `run_emulator()`.

Static follow-up identified a concrete GP violation in the tested environment shim: pinned FCEUmm's `retro_init()` requests `RETRO_ENVIRONMENT_GET_LOG_INTERFACE` (command 27). The Test 02 shim forwarded that request to stock `retro_environment_cb` through a GP bridge. Stock command 27 returns a raw firmware logger function pointer. Once the bridge returned, FCEUmm retained that pointer while executing under the external image's `_gp`. Early in `retro_load_game()`, FCEUmm calls `log_cb.log(...)` directly, bypassing the bridge and entering stock code with the wrong GP.

Test 03 prevents raw stock callbacks from escaping the compatibility boundary and closes unsupported modern environment commands instead of forwarding them to the 2017 stock handler.

## Single variable from Test 02

The patched `bios/bisrv.asd` and native loader remain unchanged.

Only this SD file changes:

```text
/cores/fceumm/core.xgc
```

Source commit containing the environment fix:

```text
084975cec6e3675e26846efd5f111729d9330da8
```

Production exact-Codescape full-link run:

```text
33673373546
```

Result: success, zero undefined symbols, GP entry assertions passed, valid XGOC produced.

## Exact image

```text
XGOC SHA-256    d0873d60452dabee64f7bc31a9217728262ea7e4205522dc73bebf51c756a26c
ELF SHA-256     659928566f348867b39a1255f2cc6bf520cf1e8b5204d4ef30b40f4c6f452ef5
BIN SHA-256     6ec5dd530c7be7a48152a374e13305032e49c853379f6ef9f0c91bf4b2ed838b
load            0x87000000
entry           0x87000000
C entry         0x87000490
external _gp    0x8718f2f0
payload         1,602,320 bytes
runtime         3,875,752 bytes
reserved        13,479,424 bytes
headroom        9,603,672 bytes
payload CRC     0x78240ac0
header CRC      0xbdd0fb6a
```

Independent artifact inspection confirms the entry veneer begins by saving stock GP, loading `0x8718f2f0`, calling `__core_entry_c`, then restoring the caller's GP before return.

## Compatibility changes in this candidate

- `GET_LOG_INTERFACE` explicitly returns false, so pinned FCEUmm retains its own no-op logger rather than receiving a raw stock function pointer.
- Unsupported modern libretro environment commands return false instead of reaching the 2017 stock environment default path.
- Stock delegation remains only for `GET_VARIABLE` command 15, which returns option data and not callable firmware pointers.
- One-byte libretro boolean output writes are used for `GET_CAN_DUPE` and `GET_VARIABLE_UPDATE`.

## Expected diagnostic progression

Reuse the same known-good Contra ROM used by Tests 01 and 02.

- same hard freeze on `Loading...`: logger escape was real but not the only pre-return defect; next test should instrument/binary-search `retro_init`, `retro_load_game`, AV and region stages;
- return to menu: the dangerous call is gone but `retro_load_game` is failing normally; inspect load result and content/options state;
- black screen or changed display: `retro_load_game` returned and execution progressed into AV/timing or first frame;
- first NES frame: external FCEUmm load and stock video transport are confirmed on hardware.
