# Exact FBA 0.2.97.42 CPS1 external-core link closure

Status: **OFFLINE BUILD PASS; HARDWARE TEST PENDING**

## Source identity

The external candidate is built from the exact public revision identified inside the XGO stock firmware:

```text
repository  madcock/sf2000-fbalpha
commit      621e371e553eb7814f12504b23f78de4715b7d11
version     0.2.97.42
```

This matches the stock XGO firmware string:

```text
FB Alpha
v0.2.97.42 621e371
```

## CPS1 driver specialization

The generated libretro driver table was restricted to:

```text
src/burn/drv/capcom/d_cps1.cpp
```

and contains:

```text
288 CPS1-family BurnDriver declarations
```

The first audit still compiles much of the historical FB Alpha source tree; source-directory reduction is a later optimization. Link-time garbage collection nevertheless produces a compact external image.

## HC15xx build

Toolchain:

```text
Codescape GNU Tools 2019.09-03-2
MIPS32 little-endian
soft-float
-G0
-mno-abicalls
-fno-pic
```

Compatibility changes for the audit:

```text
FASTCALL = 0
PTR64 = 0
INCLUDE_7Z_SUPPORT = 0
STATIC_LINKING = 1
RGB565 enabled
```

The original 0.2.97.42 ROM/driver database is preserved.

## Link result

```text
undefined symbols     0
payload/file-backed   2,499,116 bytes
runtime image         3,467,448 bytes
reserved XGOC window 13,479,424 bytes
remaining headroom   10,011,976 bytes
```

Canonical XGOC:

```text
core-fba42-cps1.xgc
SHA-256
73d3709b7db588bd90ab82b55941cad7c815f9224bff15b65cd6e501ae568d0c
```

Other hashes:

```text
xgo-fba42-cps1.elf
72543aa26f3ccf7dd8f3215171c2ed77e8c6002ab37ef7d9f032d63fc34a1d5c

xgo-fba42-cps1.bin
cf324d876f37741cd8bfb084b715cb9de6e57918b6dc57488f089a0239c03129
```

CI:

```text
run       33899398980
job       101109648794
artifact  9947134161
digest    sha256:0a5d641ab3824e2c0afee3b59545adb41af65d379783a710511a2444b2fb67fb
```

## Why this candidate is different from Test 08

Test 08 used FB Alpha 2012 CPS-1 `0.2.97.28`, while the XGO ROM collection and embedded emulator are from `0.2.97.42`.

The new candidate removes that 14-revision ROM-definition mismatch while retaining:

- CPS1-only list-ID interception;
- stock-produced arcade directory/game-name path;
- stock XGO family `0x40` run loop;
- stock video/audio/input adapters;
- stock CPS2/IGS/Neo Geo fallback;
- untouched stock arcade cleanup;
- mapper v19 and external SNES baseline.

## Performance discipline

This first exact-`.42` candidate is a **compatibility baseline**, not yet the optimized performance build.

Do not lower audio rate, alter CPU speed, skip frames, or change the shared runtime until physical hardware confirms that the exact stock ROM lineage reaches gameplay externally.

If it boots, optimization can then be measured independently against the embedded stock `.42` build.

## Next hardware gate

1. CPS2 remains stock and launches/quits normally.
2. SFII CPS1 reaches gameplay using exact FBA42 source lineage.
3. Pause-menu QUIT returns normally.
4. SFII can be relaunched.
5. Mapper v19 and Snes9x2005 remain functional.
6. Only after compatibility PASS, begin CPS1 performance optimization.
