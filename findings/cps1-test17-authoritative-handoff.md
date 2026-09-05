# CPS1 Test17 authoritative handoff

Branch: `research-post-mapper-runtime`

Authoritative HEAD at recovery:
`96ff86f1ddbdaafc6fbaa7d5f6c8457545a8473c`
(`Fix Test17 trace declaration scope`)

## Guardrail

For XGO Archeology, recover project state from the active GitHub research branch before using conversation memory to infer the current implementation. Hardware results, source changes, build workflows, and test intent must be committed before advancing to a new hardware test.

Do not revert CPS1 to stock, MAME2000, or pre-A68K FBA paths unless a new experiment explicitly requires it.

## Preserved CPS1 progression

The current CPS1 line is not stock.

- Test 08: corrected FBA2012 CPS1 runtime/content path.
- Test 09: input removed as first-frame blocker; stall remained under `BurnDrvFrame()`.
- Tests 10-13: MAME2000 evaluated, made playable, input/state repaired, adaptive frameskip tried; hardware result was slower than stock, so MAME2000 was abandoned as the primary path.
- Test 14: returned to FBA2012 with native-MIPS A68K backend.
- Test 15: repaired the legacy A68K register-context ABI mismatch; loading hang remained.
- Test 16: durable SD trace localized the hang after `CpsInit()` and before `CpsRunInit()`; therefore A68K CPU execution had not started.
- Test 17: deep instrumentation of the second `Cps1LoadRoms(1)` pass and its ROM/decode phases.

## Test16 hardware result

Last trace:

```
F10 before stock run_emulator
L00 retro_load_game enter
L10 before fba_init
D00 DrvInit enter
D10 before CpsInit
D11 after CpsInit
```

No `D20 before CpsRunInit`.

The narrowed section is:

```cpp
Cps1LoadRoms(1);

if (AmendProgRomCallback) AmendProgRomCallback();

SetGameConfig();

if (Cps1Qs) {
    KabukiDecodeFunction();
}

CpsRunInit();
```

A68K has not executed at this point.

## Test17 implementation

Commits:

- `f012f47b13ce0849e3085f3347632aad3f77d504` — Add Test17 deep CPS1 ROM-load trace
- `ca96d5adf9d9d4a3a76a993ae3c5b0c23daeeeee` — Add Test17 ROM-load trace workflow
- `96ff86f1ddbdaafc6fbaa7d5f6c8457545a8473c` — Fix Test17 trace declaration scope

Source patch:
`tools/multicore/native_cps1/patch_test17_romload_trace.py`

Build workflow:
`.github/workflows/xgo-fba-a68k-test17-romtrace.yml`

The workflow pins FBA2012 CPS1 at:
`5714c8dc311f4dda6e54533bc8dd901a29700635`

and applies, in order:

1. `patch_a68k_mips32_audit.py`
2. `patch_a68k_legacy_context_abi.py`
3. `patch_test16_a68k_trace.py`
4. `patch_test17_romload_trace.py`

The Test17 deep trace marks:

- D12/D13 around second `Cps1LoadRoms(1)`
- D14/D15 around `AmendProgRomCallback`
- D16/D17 around second `SetGameConfig`
- P00/P99 around the load pass
- P10/P11/P12/P13/P14/P15/P19 for 68000 program ROMs
- G00/G10/G11/G20/G21/G99 for graphics/tile loading
- Z00/Z99 for Z80 program
- S00/S19 for OKI
- S20/S39 for QSound
- E00 for extra tiles

## Current hardware observation

The Test17 package run on hardware produced only through `D11 after CpsInit`, despite Test17 containing D12 and deeper probes.

Do not reinterpret this as stock-emulator fallback without evidence. Continue from the committed Test17 implementation and determine why the post-CpsInit trace path is not reaching D12 / whether tracing itself perturbs startup.

## Protected baseline

Preserve:

- Mapper v19
- external-core runtime infrastructure
- NES external core work
- Snes9x2005 integration
- stock CPS2 / IGS / Neo Geo fallthrough
- corrected CPS1 hook/content path

Only the CPS1 experiment should change unless a test explicitly states otherwise.
