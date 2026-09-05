# Hardware Test 01 — external Snes9x2005 gameplay PASS, mapper packaging regression

Status: **CORE #2 HARDWARE PASS / PACKAGE COMPOSITION FAIL**

Date: September 3, 2026

## Physical result

The first native SNES Core #2 package boots and launches ordinary SNES games through the stock browser.

Observed on physical XGO:

- games load successfully;
- games are playable;
- frame pacing/performance is visibly improved;
- titles feel substantially less choppy and laggy than under the embedded stock SNES core.

This is the first physical proof that a second real external libretro core runs through the XGO runtime architecture.

## Major architecture result

The following path is now hardware-proven with Snes9x2005:

```text
stock SNES browser
 -> stock run_game() ROM preload
 -> native SNES dispatch interception
 -> guarded external-core loader
 -> XGOC Snes9x2005
 -> external GP/newlib runtime
 -> stock run_emulator()
 -> stock RGB565 video
 -> stock audio transport using family 0x08 / 11025-Hz profile
 -> stock controller input
 -> playable SNES game
```

This moves the external runtime from "FCEUmm-specific proof" to a genuinely multi-core architecture.

## Performance observation

The user reports that games appear **much less choppy and laggy than before**.

This is qualitative rather than instrumented timing data, but it is the exact user-visible performance question that motivated SNES as Core #2. It strongly supports the newer HC15xx Snes9x2005 fork as a worthwhile replacement for the XGO's embedded SNES implementation.

## Regression: Mapper menu option disappeared

The new Mapping/Mapper menu item is absent in Test 01.

Root cause is package composition, not Snes9x2005 runtime behavior.

The Test 01 staging path built its patched `bios/bisrv.asd` from the pristine stock firmware:

```text
stock SHA-256
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
```

instead of starting from the already hardware-confirmed interactive mapper v19 firmware:

```text
mapper-v19 firmware SHA-256
466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab
```

Therefore copying the Test 01 overlay replaced the mapper-enabled firmware with a stock-derived SNES-patched image.

The external core did not remove or conflict with Mapper at runtime; the package simply failed to carry the merged mapper firmware forward.

## Required correction

Core #2 Test 02 must be composed as:

```text
hardware-confirmed mapper v19 firmware
 + native SNES loader/JAL interception
 + mapper-v19 gpapi.bvs resource
 + external Snes9x2005 XGOC
```

not:

```text
stock firmware
 + native SNES interception
```

The v19 identities to preserve are:

```text
bisrv.asd
466b336ee601f16314b73fbc66f0135a7090942157fce77c749391fbaa4189ab

gpapi.bvs
759cc078816e6b865ac177ca39a37bb542ae5f64bbfbf0c0cb10f230532950c8
```

## Test 02 acceptance gate

The corrected package must prove both features simultaneously:

1. ordinary SNES game launches through external Snes9x2005;
2. performance remains improved;
3. Start+Select opens the pause menu;
4. Mapper appears as the fifth menu option;
5. Mapper opens normally;
6. one remap can be saved with A/Confirm;
7. gameplay resumes through external Snes9x2005;
8. mapping persists after exit/relaunch.

## Classification

**HARDWARE CONFIRMED:** external Snes9x2005 launch and gameplay.

**HARDWARE OBSERVED:** materially smoother/less laggy SNES performance.

**NOT A CORE REGRESSION:** missing Mapper menu.

**CONFIRMED PACKAGING BUG:** Test 01 replaced mapper-v19 firmware with a stock-derived SNES firmware.

Core #2 itself remains a PASS.
