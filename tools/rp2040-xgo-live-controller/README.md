# RP2040 XGO live GPIO controller

Minimal "Neanderthal controller" layered directly on the hardware-proven native Pico Micro-B XGO Player-2 responder.

## Wiring

Each button is a normally-open switch from the listed Pico GPIO to GND. Firmware enables the RP2040 internal pull-up, so released is HIGH and pressed is LOW.

| XGO slot | Button | Pico GPIO |
|---:|---|---:|
| 0 | R | GP2 |
| 1 | Y | GP3 |
| 2 | X | GP4 |
| 3 | L | GP5 |
| 4 | A | GP6 |
| 5 | B | GP7 |
| 6 | SELECT | GP8 |
| 7 | START | GP9 |
| 8 | UP | GP10 |
| 9 | DOWN | GP11 |
| 10 | LEFT | GP12 |
| 11 | RIGHT | GP13 |

The XGO transport still uses only the Pico's native Micro-B connector:
- DP = XGO DATA/load-like
- DM = XGO CLOCK-like
- DATA output is LOW-sink/high-Z only
- CLOCK is never driven
- no USB HID/TinyUSB

Do not connect GP26/GP27 to the XGO; those pins belong only to the earlier loose-wire proof.

## First hardware test

For the smallest useful test, wire only GP12 (LEFT), GP13 (RIGHT), GP7 (B), and GP2 (R) to four momentary buttons sharing Pico GND. Unwired inputs remain released through their pull-ups.

Expected startup signature: three quick LED blinks. During successful XGO polling the LED toggles continuously.

In a two-player game, verify:
1. P1 remains normal.
2. GP12 produces only P2 LEFT.
3. GP13 produces only P2 RIGHT.
4. GP7 produces only P2 B.
5. GP2 produces only P2 R.
6. Simultaneous direction+action presses work.
7. Releasing every button produces no phantom input.

After that passes, wire/test the remaining eight inputs and preserve this build as the human-input golden reference before GP2040-CE integration.
