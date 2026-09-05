# Core #3 Test 08 candidate — use stock XGO arcade path globals

Status: **OFFLINE BUILD PASS; HARDWARE TEST PENDING**

## Why this candidate is different

Tests 06 and 07 attempted to parse the selected arcade `.zfb` from `ROM_BUFFER` at the corrected runtime hook. Hardware proved that assumption wrong.

Static XGO disassembly now closes the actual frontend path contract.

Stock code reads 128 bytes from the selected wrapper into:

```text
0x8109fce8
```

and immediately treats that buffer as a filename string, including searching for its extension.

Later the arcade branch constructs the real archive path with:

```text
%s/bin/%s
```

using:

```text
0x810a0eb0 = current system/list directory
0x8109fce8 = current game/archive filename
```

Therefore Test 08 removes all raw-ZFB parsing and reuses the exact stock-produced values.

## Regression boundary

Test 08 is based on the known Test 05 firmware/hook.

Unchanged:

- mapper v19;
- NES external path;
- Snes9x2005;
- CPS1-only list-ID gate;
- CPS2 stock fallthrough;
- IGS/PGM stock fallthrough;
- Neo Geo stock fallthrough;
- corrected CPS1 runtime hook at 0x80360df8;
- stock arcade cleanup at 0x80360e00.

Only:

```text
cores/fbalpha2012_cps1/core.xgc
```

changes.

## Candidate identities

```text
Test08 ZIP
98c8c40a6e9a8cf4c939d82184f0f00c2eccd10b46101ef1862489c5d8af928f

CPS1 core.xgc
4d9f3ec4f203793f4907748df7351b958e548edee39a4481be277a41b9977a9b

firmware
16233cbb0d7b7e5a90d72a0eed04b873a3754bcdbaaedcea64fc1b3b972e3f1f

mapper gpapi.bvs
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8

Snes9x2005
ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf
```

## Hardware discriminator

Expected CPS2 behavior remains fully stock.

For CPS1/SFII:

- immediate return -> stock path globals are not valid by the external frontend entry point;
- startup/self-test freeze -> real archive path is now found, but core initialization has another blocker;
- gameplay -> content handoff is closed and performance/QUIT can finally be evaluated.
