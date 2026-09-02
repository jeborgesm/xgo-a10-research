# Hardware test 04: SD stage trace

Date prepared: 2026-09-02

## Why this test exists

Hardware Test 03 reproduced the same hard freeze as Test 02: the XGO remained on the stock `Loading...` screen and required a power cycle. At this point symptom-driven inference is no longer efficient enough. Test 04 therefore adds explicit execution-stage observability.

The maintained SF2000 Multicore project uses both direct LCD diagnostics and an SD-card log for this purpose. Its direct LCD implementation is explicitly panel-specific, so the first XGO diagnostic uses the lower-risk option: a fixed-string trace written to the SD card through already GP-wrapped XGO VFS services.

## Instrumentation contract

Log path:

```text
/mnt/sda1/xgo-native.log
```

The logger deliberately avoids `printf`, `malloc`, newlib stdio and raw stock callback pointers. It calls only:

```text
xgo_stock_fs_open
xgo_stock_fs_write
xgo_stock_fs_close
```

Each of those enters stock firmware through the established external-core -> stock `$gp` veneer.

The first marker truncates/recreates the log for the current launch. Later markers append.

## Stage markers

Frontend lifecycle:

```text
E0 core C entry
E1 runtime initialized
E2 ROM validation OK|FAILED
E3 before retro_init
E4 after retro_init
E5 before stock run_emulator
E6 stock run_emulator returned
E7 retro_deinit returned
E8 frontend return
```

Stock `run_emulator()` -> external-core callback crossings are routed through diagnostic C wrappers behind the existing reverse `$gp` veneers:

```text
L1 retro_load_game enter
L2 retro_load_game TRUE|FALSE
A1 get_av enter
A2 get_av return
R1 get_region enter
R2 get_region return
F1 first retro_run enter
F2 first retro_run return
U1 retro_unload_game enter
U2 retro_unload_game return
```

`xgo_diag_run()` logs only the first `retro_run()` entry/return so normal frame execution cannot flood the SD card.

## Important interpretation rule

The final complete log line is the highest hardware-proven execution stage.

If `xgo-native.log` is absent entirely, that is also evidence: either execution did not reach the C entry or the diagnostic VFS write itself is not hardware-safe. In that case the next probe should avoid filesystem I/O and use an in-RAM stage word or an XGO-proven display path.

## Exact build

Source commit:

```text
70759c616a010f80ac4528afcdd26785b97a7725
```

Exact Codescape production full-link run:

```text
33674788395
```

Result: success. The full-link, XGOC packaging and bridge assertions completed successfully.

Exact diagnostic image:

```text
XGOC SHA-256    f01d236fb91bc0b71304db472dfe0f0578b178d0715b788aa467558e624844a7
ELF SHA-256     a06ee08ed6741df364964b3536cc5f9bcfd9965379884190cc0260056b214a13
BIN SHA-256     8ec62a58135498c9980759051361997bdf8b7f865869a1f2a268fa652dbcffec
load            0x87000000
entry           0x87000000
C entry         0x8700070c
external _gp    0x8718f850
payload         1,603,696 bytes
runtime         3,877,128 bytes
reserved        13,479,424 bytes
headroom        9,602,296 bytes
payload CRC     0x02e970f5
header CRC      0xe8897cd0
```

## Hardware procedure

Only `/cores/fceumm/core.xgc` changes from Test 03. The patched `bios/bisrv.asd` and native loader remain untouched.

Use the same known-good Contra ROM, reproduce the launch once, power off if frozen, then inspect the SD root for `xgo-native.log` and preserve its complete contents as evidence.
