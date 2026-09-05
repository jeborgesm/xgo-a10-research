# CPS1 Test21 — post-68000 program-ROM phase probe candidate

Purpose: determine whether the stall inside the second `Cps1LoadRoms(1)` occurs during 68000 program-ROM loading or later.

Hardware calibration from Test20:
- immediate forced failure at entry to `Cps1LoadRoms(1)`
- observed: `Loading.....` -> black screen -> freeze

Therefore black-screen transition is the calibrated signature that a forced failure point was reached.

## Test21 patch

After the complete 68000 program-ROM loop and immediately before the graphics phase:

```cpp
return 1; /* TEST21: 68000 program-ROM phase completed */
// Graphics
if (nCpsGfxLen) {
    ...
}
```

No trace calls and no filesystem I/O.

Interpretation for SFII:
- `Loading.....` -> black screen -> freeze: all 68000 program ROM loading completed; stall is later, beginning with graphics/tile loading.
- remains indefinitely on `Loading.....`: stall is within the 68000 program-ROM phase; next probe individual `BurnLoadRom()` calls.

Commits:
- Test20 hardware calibration: `51a848525659eaecd716c04191bf14cdaffaa76c`
- Test21 patch: `aaed0a6fc33de08394d617722fdb951d6b8584e5`
- Test21 workflow: `ed76f4a076c37c72a1954c56660ff8f57d81e2a2`

GitHub Actions:
- run `33953886650`
- artifact `9965722247`
- build result: success

Packaged candidate:
`xgo-core3-cps1-test21-after-program-phase-v19-snes.zip`

ZIP SHA-256:
`fcf68c596bb5988f3639fe00935bc3e5c7591cbb2ea7d75524acf030c1027d06`

CPS1 core SHA-256:
`b09c84ce83c42870ff400b37f03e4d94e0f4f83393cc9e985e35ba70bc813265`

Package is based on the exact uploaded Test17 protected SD package. Only `cores/fbalpha2012_cps1/core.xgc` changes, aside from README metadata.
