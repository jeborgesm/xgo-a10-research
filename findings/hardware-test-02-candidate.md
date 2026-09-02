# Hardware test 02: direct stock-preloaded ROM size

Date prepared: 2026-09-02  
Date executed: 2026-09-02

## Purpose

Hardware Test 01 confirmed that the patched NES path reaches the native loader, stops the stock sound task, and returns safely to the menu, but the external frontend returned before gameplay. Static follow-up identified the frontend's exact-ROM-size helper as an invalid stock-ABI crossing: XGO `fseeko` uses a 64-bit O32 offset while the helper declared it with 32-bit arguments.

Test 02 removed that helper entirely rather than repairing an unnecessary dependency.

## Single variable from Test 01

The patched `bios/bisrv.asd` and native loader were unchanged.

Only this SD file changed:

```text
/cores/fceumm/core.xgc
```

The tested core came from source commit:

```text
5e18906a5faa11d0a03a72c2cc540823def15d16
```

Production exact-Codescape full-link run:

```text
33667274795
```

Result: success, zero undefined symbols, GP bridge assertions passed, XGOC validation passed.

## Exact tested image

```text
XGOC SHA-256    3e4420a7b039b32904e0d8d7862b858726147562072f0fccb49eb94ae19bf9b8
ELF SHA-256     26fbbb488088d1a6d172b2f50112cf0e4f436e751cf2f6038be03bbf1a2f7e8e
BIN SHA-256     11996f4b60940543219a73d50e5225a6cc6a85130b26db39a225812d820ded7c
load            0x87000000
entry           0x87000000
C entry         0x87000490
external _gp    0x8718f300
payload         1,602,328 bytes
runtime         3,875,760 bytes
reserved        13,479,424 bytes
headroom        9,603,664 bytes
payload CRC     0xa9946df9
header CRC      0xc128817e
```

## Hardware result

Using the same known-good Contra ROM as Test 01:

- launch no longer returns immediately;
- the display remains on the stock `Loading...` screen;
- the system becomes unresponsive to all button combinations;
- recovery requires a power cycle.

This confirms that removing `exact_rom_size()` advanced execution beyond the Test 01 early-return boundary and into stock `run_emulator()` / external-core load processing.

## Machine-code localization

Preserved XGO `run_emulator()` at `0x8035ed48` calls the function pointer at stock global `0x80c33acc` (`gfn_retro_load_game`) at runtime `0x8035edf8`, passing `&g_retro_game_info`. Only after this callback returns does the function call `gfn_get_system_av_info` and `gfn_retro_get_region` and proceed into sound/timing setup.

The persistent `Loading...` state therefore strongly localizes Test 02 to `retro_load_game()` or an operation it performs before returning.

## Raw stock logger callback GP defect

Pinned FCEUmm performs this sequence:

1. `retro_set_environment()` installs the XGO shim.
2. `retro_init()` calls `RETRO_ENVIRONMENT_GET_LOG_INTERFACE` (command 27).
3. The Test 02 shim delegated unknown commands to stock `retro_environment_cb` through a stock-GP veneer.
4. XGO stock environment command 27 is explicitly implemented and writes a raw firmware logging function pointer into the supplied `retro_log_callback`.
5. The veneer then restores external-core `_gp` before returning to FCEUmm.
6. Early in `retro_load_game()`, after RGB565 negotiation, FCEUmm calls `log_cb.log(...)` directly.
7. That raw stock function pointer therefore executes with the **external core GP**, not XGO stock GP `0x80c34774`.

This bypasses the bidirectional GP bridge and is a concrete freeze mechanism exactly at the Test 02 boundary.

The relevant distinction is important: returning plain data from stock environment calls can be safe, while returning callable stock function pointers is not safe unless the pointer itself targets a GP-switching veneer.

## Follow-up fix

Commit:

```text
084975cec6e3675e26846efd5f111729d9330da8
```

changes the environment contract to:

- explicitly return `false` for `GET_LOG_INTERFACE`, leaving pinned FCEUmm's built-in no-op logger installed;
- stop forwarding unsupported modern libretro commands to the 2017 XGO environment handler;
- retain stock delegation only for command 15 (`GET_VARIABLE`), which returns option data rather than callable firmware pointers;
- correct one-byte libretro boolean writes for `GET_CAN_DUPE` and `GET_VARIABLE_UPDATE`.

This is the Test 03 candidate direction.
