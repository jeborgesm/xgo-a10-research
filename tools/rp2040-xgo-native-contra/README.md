# XGO native-Micro-USB scripted Contra responder

Hardware candidate following the marked five-wire proof.

HW prerequisite:
- direct custom five-conductor XGO Handle Interface -> stock Raspberry Pi Pico Micro-B;
- Pico powered by XGO through the cable;
- marked wire-id HW result: DP = XGO DATA/load-like, DM = XGO CLOCK-like;
- no USB protocol and no TinyUSB.

This ports the already hardware-proven P2 scripted Contra sequence from GP26/GP27 to the RP2040 native USB PHY:
- DM RX: CLOCK input only;
- DP RX: DATA/load observation;
- DP TX latch remains LOW;
- DP TX OE is the only active control: OE=1 sinks DATA LOW, OE=0 releases high-Z.

Script is unchanged: RIGHT -> jump+shoot -> LEFT -> DOWN -> jump+shoot -> idle.

Safety invariant: every timeout and recovery path releases DP to high-Z. DM is never driven.

## Hardware result — PASS

HW: flashed native candidate SHA-256 `7b9307721f0c95649eaf67e5242c221adf6feb5e12ac5e957bb6240bbd9a94ca` and connected the stock Pico to XGO using only the custom five-conductor Micro-B cable. Initial no-action/LED-off observation was mechanically intermittent; after slightly repositioning the handmade cable, the LED flashed continuously and Player 2 executed the scripted sequence in Contra: moving back and forth and shooting. The character was in water during this observation, so visible jumping could not be adjudicated from that scene.

HW conclusion:
- native Micro-B DP DATA sink/release: PASS;
- native Micro-B DM CLOCK receive: PASS;
- repeated host-synchronous 12-slot responder: PASS;
- one-cable XGO -> stock Pico native receptacle transport: PASS;
- scripted movement and action-button injection into live P2 gameplay: PASS;
- cable/DIY connector mechanical reliability: OPEN; movement of the cable changed behavior and must be improved before treating the physical harness as robust.

This closes the electrical/native-receptacle transport proof. Do not reinterpret the earlier LED-off result as a firmware timing failure; the subsequent same-firmware success after cable movement identifies mechanical contact as the immediate cause.
