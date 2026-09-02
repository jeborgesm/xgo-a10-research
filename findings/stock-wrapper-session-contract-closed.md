# XGO stock emulator-wrapper session contract

Status: **static contract closed for first FCEUmm hardware bring-up**.

## Why this mattered

The external-core loader intercepts the stock GBA dispatcher call before `run_gba()` executes. Therefore every stock mutation normally performed by `run_gba()` before entering `run_emulator()` had to be classified as reproduced, intentionally replaced, or irrelevant. Otherwise a successful static link could still fail on hardware because the external core inherited stale frontend state.

## Cross-wrapper comparison

Static disassembly of all six stock emulator wrappers found the same setup skeleton. Each wrapper performs the following session preparation before entering the common `run_emulator()` loop:

1. stop/handshake the stock sound task;
2. install that emulator's state-save/state-load callbacks;
3. zero the shared word at `0x80c2e964`;
4. register video/audio/input/environment callbacks and initialize the core;
5. construct `retro_game_info` / content state;
6. install the active core API indirection slots, including the core-specific frameskip hook where applicable;
7. enter `run_emulator()`.

The shared `0x80c2e964` reset occurs at wrapper sites:

```text
0x8035f68c
0x8035fa28
0x8035fdc4
0x80360160   run_gba
0x803604fc
0x80360898
```

The common `run_emulator()` loop subsequently reads/increments/resets this same word around:

```text
0x8035ef60  load
0x8035ef68  reset
0x8035efc4  load
0x8035efdc  increment/store
```

The exact OEM symbol name is unavailable, but the behavior is sufficient to classify it as a **session-scoped run-loop phase/counter**.

Runtime address:

```text
0x80c2e964
```

## External FCEUmm disposition

The current production bridge/loader now covers every stock setup class:

```text
stock sound-task shutdown
    -> reproduced by injected XGOC loader

stock state-save/load callbacks
    -> intentionally replaced by safe external-core stubs for first bring-up

0x80c2e964 session phase/counter reset
    -> reproduced by FCEUmm bridge; old value restored on return

core callback registration + retro_init
    -> reproduced with FCEUmm exports and XGO compatibility environment

stock GBA game_info/preload construction
    -> intentionally replaced with real FCEUmm ROM path contract

active libretro API function-pointer slots
    -> replaced for FCEUmm session and restored afterward

stock core-specific frameskip pointer
    -> neutralized to NULL for FCEUmm session and restored afterward

active system-family policy
    -> temporarily changed from intercepted GBA family to NES (0x01), then restored
```

No additional unclassified pre-`run_emulator()` mutation was found in the stock GBA wrapper after comparison with the sibling wrappers.

## Rebuild after final missing reset

Commit:

```text
9bb0b3c53a0ac0dceea42949284b94b3c2954bbb
Reproduce XGO run-loop phase reset for FCEUmm
```

GitHub Actions:

```text
workflow      XGO FCEUmm link lab
run           #45
run id        33589709587
result        success
artifact id   9831311832
artifact zip SHA-256
1fd4f9763e5003ea6931f7b84a742ada7c68b3e92d582f277babd8e3b3e9d460
```

The full executable still links with:

```text
undefined symbols = 0
```

Current image layout:

```text
__image_start     0x87000000
__start           0x87000098
__file_end        0x8717ec30
__bss_start       0x8717ec30
__image_end       0x873a9e60

entry offset      0x98
linked file span  1,567,792 bytes
payload           1,567,784 bytes
runtime           3,841,632 bytes
zero/BSS tail     2,273,848 bytes
reserved window   13,479,424 bytes
remaining         9,637,792 bytes
```

XGOC v1:

```text
load              0x87000000
entry             0x87000098
payload CRC       0x7fcbef5b
header CRC        0x7c8f0683
```

Authoritative output hashes for this checkpoint:

```text
xgo-fceumm.elf
280ace02bb1ccd46c397ecca5fea1d7330bcd97be36ea83a1a3c7cd5e8a2f3ca

xgo-fceumm.bin
de98f31a746dec17b620334f6afd9d396cd0852455053fc2e274925a443f8d35

core.xgc
46d5678ecbaddff5e1f5d1f696aea0bad6a397ca4c7797f3f452a3b03742c4ac
```

## Classification

**Confirmed statically:** the bypassed stock emulator-wrapper setup contract is now accounted for at the instruction/state-mutation level for the first FCEUmm experiment.

**Not yet confirmed:** physical execution. Hardware can still reveal runtime assumptions that static analysis cannot prove, but there is no longer a known or unclassified stock `run_gba()` setup mutation blocking an SD-only bring-up.
