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
