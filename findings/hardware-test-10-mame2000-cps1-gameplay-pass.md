# Hardware Test 10 — MAME2000 CPS1 boots and reaches gameplay

Status: **MAJOR HARDWARE PASS**

Physical XGO evidence supplied by the tester shows the MAME2000 Core #3 candidate successfully running Street Fighter II.

Observed evidence:

- SFII progresses beyond the startup/self-test boundary where FBA2012 Tests 08/09 froze.
- Actual SFII gameplay is rendered on the XGO.
- Multiple gameplay frames are visible, including active fighters, HUD, stage graphics and animation state.
- The XGO volume OSD is visible over live MAME2000 gameplay, demonstrating that the surrounding stock XGO runtime/UI path remains active while the external core is running.
- A separate captured screen shows the CPS1 diagnostic/test display ("OFFSET 0 COLOR 1 CODE 0-0"), further proving the emulated CPS1 machine is executing rather than hanging at FBA2012's first-frame boundary.

This validates the architectural pivot from FBA2012 to MAME2000.

## What Test 10 proves

The following chain now works on physical hardware:

```text
CPS1 list 7 discriminator
 -> existing corrected external-core loader
 -> stock-resolved ARCADE/bin/<game>.zip path
 -> MAME2000 0.37b5 core
 -> exact SF2000 libco backend
 -> CPS1 machine initialization
 -> ROM loading (including compatibility with the XGO SFII archive)
 -> emulated CPU/device execution
 -> RGB565 video callback
 -> sustained gameplay frames
 -> stock XGO OSD interaction
```

This sharply distinguishes MAME2000 from the FBA2012 candidate, which initialized SFII but froze inside/under the first BurnDrvFrame path.

## Still to verify before promotion

- subjective frame pacing / lag under heavy SFII action;
- controls, including all six CPS1 buttons;
- pause-menu behavior;
- QUIT back to the game list;
- relaunch after QUIT;
- regression check for CPS2/IGS/Neo Geo;
- mapper v19 and SNES regression check;
- behavior of save/load entries, because MAME2000 reports zero-size libretro serialization.

## Cleanup after behavioral acceptance

The Test 10 directory name is intentionally temporary:

```text
/cores/fbalpha2012_cps1/core.xgc
```

The binary at that path is MAME2000. Once behavioral testing passes, move it to a truthful MAME2000/CPS1 path and update the loader in a separately controlled firmware change.
