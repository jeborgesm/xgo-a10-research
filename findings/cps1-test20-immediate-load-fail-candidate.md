# CPS1 Test20 — immediate Cps1LoadRoms failure calibration candidate

Purpose: calibrate whether the persistent `Loading.....` screen is a valid control-flow oracle.

Baseline:
- FBA2012 CPS1
- native-MIPS A68K enabled
- legacy A68K context ABI fix
- zero trace/file I/O
- protected Mapper v19 / NES / SNES / stock CPS2-IGS-NeoGeo

Patch:

```cpp
if (bLoad) {
    return 1; /* TEST20: immediate load-pass failure calibration */
    ...
}
```

Interpretation:
- If SFII exits/returns instead of sitting on `Loading.....`, then immediate load failure propagates visibly and Test19 is validated: the real stall is inside `Cps1LoadRoms(1)`.
- If SFII still sits on `Loading.....`, then frontend load failure and true hang are visually indistinguishable; Test19's result is ambiguous and we need a different zero-I/O observability mechanism.

Commits:
- Test19 hardware result: `a67794ad1aa7feeba1f154d48558ec6df073cb80`
- Test20 patch: `a5527d9c8b46a1d868deba881438d9b99cb5ffb9`
- Test20 workflow: `2253bb67901cc0366328d161188a2c2976164cdc`

GitHub Actions:
- run `33953612858`
- artifact `9965638032`
- build result: success

Packaged candidate:
`xgo-core3-cps1-test20-immediate-load-fail-v19-snes.zip`

ZIP SHA-256:
`b6309d5e5d25d00b280f503ac0e9655434d159466d25134303462101eb3f6500`

CPS1 core SHA-256:
`22cdcd47fd9929fad39985187a9228d29b43e60020e5184e786086f6e117ba2b`
