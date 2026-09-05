# CPS1 Test19 — zero-I/O Cps1LoadRoms return probe candidate

Purpose: avoid all filesystem/trace side effects and answer one control-flow question: does the second `Cps1LoadRoms(1)` return?

Baseline:
- FBA2012 CPS1
- native-MIPS A68K enabled
- legacy A68K context ABI fix
- no Test16/Test17 tracing
- Mapper v19 / NES / SNES / stock CPS2-IGS-NeoGeo protected

Patch:

```cpp
Cps1LoadRoms(1);
return 1; /* TEST19: if this call returns, abort DrvInit cleanly */
```

Interpretation:
- Still stuck on `Loading.....` => `Cps1LoadRoms(1)` did not return.
- Loading aborts/returns cleanly instead of hanging => `Cps1LoadRoms(1)` returned; blocker is later in `DrvInit()`.

Commits:
- Test18 hardware failure record: `44d89fcfa66a3c12ea2ca03050f6c359a146013f`
- Test19 probe patch: `d8d3ae2f07f12ba6fa7246a33681fb799d076e24`
- Test19 workflow: `155ff4e776710bf51a9cb408b87c198543f07726`

GitHub Actions:
- run `33953332560`
- artifact `9965548622`
- build result: success

Packaged hardware candidate:
`xgo-core3-cps1-test19-zeroio-return-probe-v19-snes.zip`

ZIP SHA-256:
`6360a9bb7548073b1087c1beb1a2a3e6bbbe7a3f6a52076c76a8abb3871018ee`

CPS1 core SHA-256:
`2b0cb42c2f5545212298eba008446f077dbd71c50aeedeefb0f45c9d6121b37c`

Package is based on the exact uploaded Test17 SD package; only `cores/fbalpha2012_cps1/core.xgc` changes, plus README metadata.
