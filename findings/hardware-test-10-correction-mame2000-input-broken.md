# Hardware Test 10 correction — MAME2000 executes, but input mapping is broken

Status: **PARTIAL HARDWARE PASS / NOT PLAYABLE**

Correction to the initial Test 10 interpretation after tester clarification.

What is proven:
- MAME2000 loads the XGO CPS1/SFII ROM successfully.
- CPS1 CPU/device execution advances beyond the FBA2012 first-frame stall.
- Video renders sustained game/diagnostic frames.
- Stock XGO volume OSD can appear over the running external core.

What is NOT proven:
- playable controls;
- correct six-button mapping;
- normal game interaction;
- pause/quit behavior.

Actual hardware behavior:
- pressing XGO controls does not map cleanly to SFII controls;
- some button presses trigger a very loud sound;
- other button presses expose apparently random MAME administrative/service/test features;
- therefore Test 10 cannot be considered a gameplay pass.

Likely failure class:
The XGO stock input callback contract and MAME2000's expected libretro joypad IDs/arcade service inputs are not aligned. MAME2000 itself is executing, unlike FBA2012, but its input translation layer needs to be adapted explicitly for XGO.

Next action:
Trace MAME2000 libretro input mapping and MAME 0.37b5 OSD input ports against the already recovered XGO stock input callback. Build an input-only diagnostic/fix. Do not change the working MAME2000 CPU/video/runtime path.

Baseline remains protected:
mapper v19, NES, SNES, CPS2/IGS/Neo Geo stock fallback, CPS1 list discriminator, corrected content path/runtime hook.
