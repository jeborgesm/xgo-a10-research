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

Hardware status: candidate only until tested on the physical XGO.
