# Hardware test — Audio OSD v1 PASS

Date: 2026-09-05
Candidate: `xgo-audio-osd-v1-on-cps1-scheduler.zip`

## Result

**PASS** for the first transient volume OSD proof.

Observed on physical XGO hardware:

- the bottom-left volume bar is visible during gameplay;
- the bar updates as the stock four volume states are selected;
- the bar also updates while the in-game pause menu is displayed;
- the bar automatically disappears after approximately one to two seconds;
- the user reports the behavior is good and likes the presentation;
- Mapper remains present in the pause menu;
- frontend/system navigation remains functional.

Photographic evidence supplied with the test shows the bar rendered over Contra gameplay and over the stock pause menu.

## CPS frontend-menu limitation

One important scope boundary was discovered:

> In the CPS game-selection/menu screen, changing volume does not immediately update/show this OSD.

Once a CPS game is running, including while its pause menu is open, the OSD updates normally.

This is consistent with the v1 hook location: it intercepts the `run_screen_write` presentation path used by active emulation, not every independent frontend/menu renderer.

This is **not a failure of volume state detection or the bar renderer**. It establishes that the CPS selection menu has a separate presentation path that would need a second frontend-specific hook if menu-wide OSD coverage is desired later.

For now this limitation is acceptable because the experiment's primary goal was safe gameplay OSD.

## Next requested experiment: finer volume control

The user explicitly wants more choices than the stock four:

```text
0 -> 33 -> 66 -> 99 -> 0
```

Previous static archaeology already established:

- `g_volume @ 0x80c33a54` is an 8-bit frontend value;
- `set_audio_volume @ 0x801b3b40` forwards arbitrary uint8 values;
- the next sound-device wrapper does not re-quantize to four levels;
- GPIO L23 mute remains a separate zero/nonzero gate.

Therefore the next experiment should modify only the **frontend increment/wrap policy**, preserve zero mute behavior, and let the now-proven OSD visualize the finer values.

A conservative first policy is 10 useful levels plus mute:

```text
0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 99, then 0
```

This retains exact maximum 99 and exact mute 0 while providing substantially finer control.

Before building, recover the exact instruction sequence implementing `+33 / >99 / wrap` and patch only that policy. Do not modify the stock sound transport.
