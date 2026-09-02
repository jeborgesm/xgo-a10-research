# Hardware test 02 candidate: direct stock-preloaded ROM size

Date prepared: 2026-09-02

## Purpose

Hardware Test 01 confirmed that the patched NES path reaches the native loader, stops the stock sound task, and returns safely to the menu, but the external frontend returned before gameplay. Static follow-up identified the frontend's exact-ROM-size helper as an invalid stock-ABI crossing: XGO `fseeko` uses a 64-bit O32 offset while the helper declared it with 32-bit arguments.

Test 02 removes that helper entirely rather than repairing an unnecessary dependency.

## Single variable from Test 01

The patched `bios/bisrv.asd` and native loader are unchanged.

Only this SD file changes:

```text
/cores/fceumm/core.xgc
```

The new core comes from source commit:

```text
5e18906a5faa11d0a03a72c2cc540823def15d16
```

Production exact-Codescape full-link run:

```text
33667274795
```

Result: success, zero undefined symbols, GP bridge assertions passed, XGOC validation passed.

## Exact image

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

## Expected diagnostic progression

If Test 01's early return was caused by the invalid `fseeko` helper, Test 02 should progress beyond native frontend validation and into stock `run_emulator()` with the external FCEUmm callback table installed.

Meaningful outcomes, in increasing order of progress:

- same immediate return: another pre-`run_emulator()` assumption is wrong, most likely ROM buffer/size state or runtime initialization;
- black screen/hang after launch: execution progressed beyond the previous early return and exposed a later runtime/ABI issue;
- first rendered NES frame: FCEUmm load plus video callback path confirmed on hardware;
- animation/input/audio: stock run loop and bidirectional callback ABI confirmed;
- clean exit to menu: complete first-pass external-core lifecycle confirmed.

The test should initially reuse the same known-good Contra ROM used in Test 01 so ROM content is not another variable.
