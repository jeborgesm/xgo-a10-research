# P6 stock-Pico raw-pad controller

Software-only stock Raspberry Pi Pico. Micro-USB is treated only as conductors.

P6 corrects two architectural defects in P3-P5:
1. TX value overrides (TX_DP/TX_DM) and TX OE overrides are both explicitly owned, so DATA is deterministically LOW/Hi-Z.
2. Frame synchronization returns to the hardware-proven P2 contract: observe DATA load LOW->HIGH, install slot 0 immediately, then serialize subsequent slots against CLOCK.

It also observes two independent raw receive views before driving anything: USBPHY_DIRECT RX_DP/RX_DM and SIE_STATUS LINE_STATE. LED result after the initial one-blink boot marker:
- 2 = PHY sees DP as 12-pulse CLOCK
- 3 = PHY sees DM as 12-pulse CLOCK
- 5 = SIE raw line-state sees DP as CLOCK
- 6 = SIE raw line-state sees DM as CLOCK
- 4 = no valid repeated 12-pulse clock structure; firmware remains passive

On a valid classification it runs the hardware-proven Contra pattern: RIGHT -> jump+shoot -> LEFT -> DOWN -> jump+shoot -> idle. CLOCK is never driven. DATA TX value is permanently LOW and only OE changes.

Safety: DM_PULLUP_OVERRIDE_EN remains excluded because P3-v3 froze XGO when that override was introduced. No TinyUSB, HID, USB enumeration, PCB modification, or external interface is involved.

## Hardware result
HW FAIL: P6 produced the initial diagnostic sequence ending in 4 blinks, no scripted movement, and only the familiar occasional P2 jump artifact. Therefore neither USBPHY_DIRECT RX_DP/RX_DM nor SIE_STATUS LINE_STATE observed the already-proven 12-pulse XGO clock structure, even after complete TX value/OE ownership and restoration of the proven DATA-load synchronization architecture. Do not issue another minor raw-PHY firmware variation from this design. The next work is offline reconciliation of the stock Pico connector/cable electrical path against the proven loose-wire GREEN/YELLOW conductors and RP2040 pad behavior.
