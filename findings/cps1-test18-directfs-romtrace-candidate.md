# CPS1 Test18 — direct stock-FS deep ROM trace candidate

Branch: `research-post-mapper-runtime`

This test follows the authoritative Test17 state and does not revisit stock/MAME identity.

## Why Test18 exists

Pinned FBA source contains exactly one `DrvInit()`. After applying Test16 and Test17 patches, the critical sequence is:

```cpp
xgo_a68k_trace("D10 before CpsInit");
nRet = CpsInit(); if (nRet != 0) return 1;
xgo_a68k_trace("D11 after CpsInit");

xgo_a68k_trace("D12 before Cps1LoadRoms load pass");
Cps1LoadRoms(1);
```

There is no CPS1 work between D11 and D12.

Hardware Test17 produced D11 but not D12. Therefore the earlier interpretation that execution hangs in CPS1 logic between CpsInit and Cps1LoadRoms is impossible. A high-probability explanation is that the D11 trace helper writes the payload and then blocks during newlib stdio teardown/fclose before returning.

## Test18 change

Test18 preserves all Test17 deep ROM markers and the FBA2012 + native-MIPS A68K architecture.

Only trace transport changes when `XGO_TRACE_DIRECT_FS` is enabled:

- old: newlib `FILE *` + `fopen/fputs/fputc/fclose`
- new: proven stock bridge `fs_open/fs_write/fs_close`

This removes FILE-stream allocation/buffering/teardown from every checkpoint while keeping each marker durable.

Commits:

- authoritative recovery handoff: `b8d3d44d13ee90b0573672d27ea5045ab32554ec`
- direct-FS trace backend: `5bd062b6606e4bd533d0a2898736dfaa398bd033`
- Test18 workflow: `215d223230bef2c1cd7b325fe6059e11a27a5ba8`

GitHub Actions:

- run: `33952925438`
- artifact: `9965417359`
- result: success

Packaged candidate:

`xgo-core3-cps1-test18-directfs-romtrace-v19-snes.zip`

ZIP SHA-256:

`5f93232933f991efdddc5e2e9768d8dbaa0247e256e96487d81bd9e498a1058d`

CPS1 core SHA-256:

`68e0d4144fa2bc1cc41e2fbcc2cba585badae7d93b07b217ed18c5c1d513acca`

The package is based on the exact uploaded Test17 SD package. Only:

`cores/fbalpha2012_cps1/core.xgc`

changes, aside from candidate README/manifest metadata.

## Hardware interpretation

Run SFII once and inspect `/xgo-a68k-trace.txt`.

If D12/P00 and deeper markers now appear, Test17's D11 boundary was an instrumentation artifact and the new trace can localize the real ROM-load/decode stall.

If the direct-FS trace still stops at D11, investigate the underlying stock `fs_close` return path or replace checkpoint persistence with a different mechanism before drawing any CPS1 conclusions.
