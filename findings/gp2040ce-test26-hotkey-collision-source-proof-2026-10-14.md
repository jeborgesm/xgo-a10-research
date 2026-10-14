# Test26 activation collision — upstream source proof

Evidence: HW user report; UP pinned GP2040-CE source at 3d1f32f7d02d418826b725b60208278d3be878c3; SRC Test26 candidate.

## UP: confirmed conflict
- `src/addons/neopicoleds.cpp` tests `gamepad->pressedS1() && gamepad->pressedS2()`, then `gamepad->pressedR1()`.
- It assigns `HOTKEY_LEDS_PARAMETER_CYCLE` and clears `GAMEPAD_MASK_R1 | GAMEPAD_MASK_S1 | GAMEPAD_MASK_S2` from `gamepad->state.buttons`.
- `src/animationstation/animationstation.cpp` increments `baseCycleTime` for `HOTKEY_LEDS_PARAMETER_CYCLE`.
- `src/display/ui/screens/ButtonLayoutScreen.cpp` emits `LED Idle Rate = N/CYCLE_STEPS` when base cycle changes.

## SRC/HW interpretation
- Test26 uses precisely S1+S2+R1 (SELECT+START+HK) as its arming combination.
- Upstream LED add-on consumes those bits, depending on execution order, explaining unreliable arming and the user-observed Idle Rate overlay.
- The OLED phase sequence does run when triggered; MP-dominant gameplay remains a separate serial-slot/stream problem.

## Next implementation
- Eliminate collision by using a trigger that upstream does not consume, or intercept inputs before LED hotkeys, with pinned ordering proof. Prefer minimal change to Test26 Core0 control path and preserve Test16 Core1 responder.
- Investigate first serial slot and stream ownership independently; do not attribute rare HK to successful pulse duration.
