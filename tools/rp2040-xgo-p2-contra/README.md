# XGO P2 scripted Contra responder

Hardware experiment following the hardware-proven P1 fixed-R responder.

Wiring remains unchanged:
- RED -> Pico GND
- YELLOW -> GP26
- GREEN -> GP27
- BLUE/BROWN disconnected

The PIO serializes all twelve active-low XGO positions. GP27's output latch is permanently LOW; PIO writes only PINDIRS/OE, so each bit is either LOW-sink (pressed) or high-Z (released). GP26 remains input-only.

Script: RIGHT, jump+shoot, LEFT, DOWN, jump+shoot, repeat.

Current test assumption from hardware: raw R maps through the current Contra keymap to FC A/jump. SHOOT is initially raw B and should be corrected to the user's actual Contra .kmp mapping if needed.

Do not flash until the local generated PIO header is inspected.


## Generated-code audit — approved candidate

Hardware candidate UF2 SHA-256:

`C692A0F3DDBB76ACD0EB0E0E51C7B090C7212C17B1016ABF3D0BB7C0674E4A4F`

Generated PIO audit:
- instructions 0-1 wait for XGO DATA load-low then host release;
- instruction 3 serializes position 0 from OSR onto GP27 PINDIRS;
- X=10 yields exactly eleven subsequent DATA updates, positions 1..11;
- each subsequent DATA bit is installed during CLOCK-low before the corresponding CLOCK-high sample;
- the final/trailing 12th CLOCK pulse is consumed at instructions 9/11;
- instruction 10 forces GP27 high-Z before rearming;
- no PIO instruction writes DATA high: OUT/SET affect PINDIRS only, while the GP27 output latch remains fixed LOW in main.c;
- GP26 remains input-only.

Result: generated-code audit PASS. This exact SHA is approved for the first P2 scripted hardware test. It is not yet hardware-proven.


## Hardware result — PASS

The approved P2 candidate (SHA-256 `C692A0F3DDBB76ACD0EB0E0E51C7B090C7212C17B1016ABF3D0BB7C0674E4A4F`) was flashed and tested on the physical XGO A10 with Contra in 2-player gameplay.

Observed result: the Player-2 character executed the programmed autonomous sequence, including movement and jumping, and interacted normally with live gameplay. The user reported that the bot jumped over an enemy, leaving that enemy to kill Player 1, and confirmed that it was doing everything programmed.

HW conclusion:
- arbitrary multi-position 12-bit P2 serialization: PASS;
- RIGHT/LEFT/DOWN directional injection through the Handle Interface: PASS;
- action-button injection/jump through the current Contra mapper: PASS;
- repeated host-synchronous scripted transactions at the measured controller poll cadence: PASS;
- GP27 LOW-sink/high-Z electrical strategy remains stable in active gameplay: PASS;
- full path RP2040 -> XGO Handle Interface -> P2 scanner -> mapper -> libretro/game input: HW proven.

This closes the protocol proof needed before replacing the scripted state generator with live arcade/GP2040-style button state.
