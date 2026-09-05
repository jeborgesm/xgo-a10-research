# Hardware Test18 — direct-FS tracing fails before first durable marker

Hardware result:

- SFII does not load.
- No `/xgo-a68k-trace.txt` is created.

Interpretation:

Test18 replaced Test16/17 newlib stdio tracing with direct calls to the stock filesystem bridge (`fs_open/fs_write/fs_close`). Because no trace file is created at all and loading regresses immediately, the direct filesystem trace transport is itself unsafe in this external-core execution context.

This means the Test17 D11-only result must not be used to infer a CPS1 control-flow boundary. Both stdio and direct stock-FS tracing perturb startup.

Next diagnostic must use **zero filesystem I/O**.

Plan: restore the Test15 A68K+ABI baseline with no Test16/Test17 tracing and add a pure control-flow reachability probe around the second `Cps1LoadRoms(1)` call. If the call returns, intentionally return failure from `DrvInit()` so the frontend should exit loading cleanly. If the device remains stuck at Loading, the second `Cps1LoadRoms(1)` call itself did not return.

No trace helper, no file operations, no extra runtime services.
