# Core #3 Test 11 — FBA2012 CPS1 without speedhacks

Status: **READY FOR HARDWARE DIAGNOSTIC**

## Why this test exists

Hardware Test 09 disabled `poll_input()` and produced the exact same CPS1 startup stall.

Therefore input is not the blocker.

The remaining failure boundary is inside/under:

```text
BurnDrvFrame()
 -> CPS1 frame execution
 -> SekRun()
 -> m68k_execute()
```

The FBA2012 CPS1 build also enables:

```text
-DUSE_SPEEDHACKS
```

unconditionally in `makefile.libretro`.

Test 11 removes only that define while preserving:

- current pinned CPS1 core commit;
- normal input polling;
- M68K backend;
- XGO stock-path globals;
- CPS1-only list-ID gate;
- corrected arcade runtime hook;
- stock arcade cleanup;
- mapper v19;
- external NES;
- external Snes9x2005;
- stock CPS2/IGS/Neo Geo.

## Build result

GitHub Actions run:

```text
33901630275
```

Artifact:

```text
xgo-cps1-test11-no-speedhacks
artifact ID 9947877139
digest sha256:c9ff0e1213d5b33d958b813b89a19ec6b7024a3553e37f10c8d6803e980ae2fe
```

Complete XGO hardware package:

```text
xgo-core3-cps1-test11-no-speedhacks-v19-snes.zip
SHA-256 5c5b94b653f9796a853b909af32bf188128a7c6dc1feee17ada847f4ca47d167
```

CPS1 XGOC:

```text
d945944187cc5f49c7a20d351d391608fc1c8559365cd2d9ffae7ea60d26f42f
```

## Interpretation gate

If SFII now progresses past the self-test, the FBA CPS speedhack layer is incompatible with this HC15xx/XGO execution environment.

If behavior remains unchanged, the accumulated evidence is strong enough to classify this FBA2012 CPS1 port as unsuitable for XGO and pivot Core #3 to another arcade core.

## Alternative-core status

MAME2000 has a maintained `platform=sf2000` build using the same HC15xx Codescape toolchain and `-O3`.

Its SFII driver uses MAME 0.37b5-era ROM filenames but many CRCs match the same underlying SFII ROM data used by current FBA2012 sets. A future pivot must explicitly audit ZIP-member naming/ROM-set compatibility before hardware packaging.
