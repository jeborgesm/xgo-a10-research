# RP2040 responder P2 — scripted Contra demo

Status: DESIGN, not yet hardware-tested.

Purpose: after the P1 fixed-R hardware proof, exercise multiple serial positions with an unmistakable autonomous Player-2 sequence in Contra.

Desired visible loop:

1. move RIGHT
2. jump + shoot
3. move LEFT
4. crouch/down
5. jump + shoot
6. repeat

The responder must preserve the hardware-proven P1 electrical contract:
- XGO RED -> Pico GND
- XGO YELLOW -> GP26 CLOCK input only
- XGO GREEN -> GP27 shared P2 DATA
- GP27 is LOW-sink/high-Z only and must never be driven HIGH
- BLUE/BROWN disconnected

XGO serial positions remain:
0 R
1 Y
2 X
3 L
4 A
5 B
6 SELECT
7 START
8 UP
9 DOWN
10 LEFT
11 RIGHT

The scripted actions should be expressed as XGO raw button states before the existing per-game mapper. Contra's current mapper determines which XGO logical buttons produce FC A/B, so implementation must inspect that mapping rather than guess jump/shoot assignments.

Timing: XGO polls P2 at ~16.032 ms (~62.37 Hz). Script phases should advance by poll count, not wall-clock sleeps, so the RP2040 remains synchronized to the host transaction stream.

This experiment is intended to prove arbitrary multi-bit 12-position serialization, not GP2040-CE integration yet.
