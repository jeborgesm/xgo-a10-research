# Preferred GP2040-CE Pico wiring — user diagram (2026-10-08)

Source: user-provided `picowiring-BIG-V4.png`. This is the requested physical-controller configuration, distinct from the temporary GP2–GP13 Caveman twelve-button test harness.

## Physical GPIO map (diagram evidence)

| GPIO | Label in diagram | GP2040 logical action / role |
|---|---|---|
| GP0 | SDA | I2C0 SDA, OLED |
| GP1 | SCL | I2C0 SCL, OLED |
| GP2 | UP | UP |
| GP3 | DOWN | DOWN |
| GP4 | RIGHT | RIGHT |
| GP5 | LEFT | LEFT |
| GP6 | B1 | B1 (A) |
| GP7 | B2 | B2 (B) |
| GP8 | R2 | R2 (RT) |
| GP9 | L2 | L2 (LT) |
| GP10 | B3 | B3 (X) |
| GP11 | B4 | B4 (Y) |
| GP12 | R1 | R1 (RB) |
| GP13 | L1 | L1 (LB) |
| GP14 | TURBO | Turbo input |
| GP15 | T LED | Turbo indicator output |
| GP16 | S1 | Select/Share |
| GP17 | S2 | Start/Options |
| GP18 | L3 | Left stick button |
| GP19 | R3 | Right stick button |
| GP20 | A1 | Home/PS/XB |
| GP21 | A2 | Touchpad/Select Back |

The OLED diagram labels its pins VCC/GND/SCL/SDA and connects SDA→GP0, SCL→GP1. The diagram draws VCC from VBUS and ground from Pico ground; **HW (user-confirmed): this exact VBUS-powered OLED arrangement already works across the user's existing controllers; do not reopen voltage compatibility for these modules**. Diagram also shows an additional indicator LED with a 4.7V annotation; do not infer an adequate resistor/current-limiting circuit from this drawing.

## User-selected target

Preserve GP2040-CE's normal display and Web Config capabilities and this full arcade layout. **Do not substitute the Caveman test harness's GP2 R / GP3 Y / ... / GP13 RIGHT physical mapping as the final board configuration.**

The existing `configs/Pico/BoardConfig.h` at pinned upstream `3d1f32f7d02d418826b725b60208278d3be878c3` matches this diagram's primary GP2–GP21 action assignments, including GP14 turbo and GP15 turbo LED, and declares I2C0 GP0/GP1 with display support. It is therefore a much stronger starting point for XGO Test01 than a stripped custom board config.

## XGO output mapping remains logical

R1→XGO slot0 R; B4→1 Y; B3→2 X; L1→3 L; B1→4 A; B2→5 B; S1→6 SELECT; S2→7 START; UP→8; DOWN→9; LEFT→10; RIGHT→11.

R2/L2, L3/R3, A1/A2 and Turbo have no independently hardware-proven XGO slots. Keep them available for GP2040 processing, hotkeys, profiles, and other output modes. Do not silently promise their separate native XGO button behavior.

## Important design correction

Earlier manifest advice to use a minimal board configuration was a *transport-isolation idea*, not the desired product configuration. User specifically prefers the full Pico layout shown here. Use upstream Pico board config as the starting point and add XGO output mode, with explicit audit of peripheral ownership and Web Config recovery.

## Status

User reference and upstream source comparison documented. Integrated firmware not compiled or hardware tested. OLED VBUS power and existing GP0/GP1 display wiring are HW (user-confirmed). Web Config boot chords, Turbo behavior and Core1 display responsiveness in the *integrated XGO firmware* remain OPEN.
