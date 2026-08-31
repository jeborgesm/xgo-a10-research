# Wired Player 2 protocol family comparison

## Summary

The XGO wired Player 2 scanner is closely related to the **SF2000 local keypad shift-register contract**, but it is **not electrically identical to a stock NES or SNES controller interface**.

This distinction matters because original NES/SNES controllers are synchronous serial devices, but their host contract uses three logical signals:

- latch / parallel-load output
- clock output
- serial data input

The XGO scanner instead uses a **bidirectional data/load line plus a shared clock** for each controller channel:

- P1 data/load: GPIO B15
- P2 data/load: GPIO L0
- shared clock: GPIO B7

The host first drives the data line low, waits about 4 us, then releases that same pin back to input and reads serial data from it while pulsing the shared clock. There is no separately traced latch GPIO in the active XGO wired scanner.

That is essentially the same unusual two-wire contract now implemented for the SF2000 local keypad in UniFrog/FrogQEMU.

## XGO wired scan sequence

The XGO scanner performs the following sequence on both P1 and P2 data lines:

1. configure the data line as output;
2. drive it low;
3. wait approximately 4 us;
4. switch the same line back to input;
5. sample the first bit;
6. pulse shared clock low/high with short delays;
7. sample subsequent bits;
8. repeat for the 12-button state.

Decoded XGO serial sample order:

1. R
2. Y
3. X
4. L
5. A
6. B
7. SELECT
8. START
9. UP
10. DOWN
11. LEFT
12. RIGHT

This exact order is also the logical order used by the SF2000-family local scanner in current UniFrog work.

## SF2000 comparison

Current UniFrog source defines the stock SF2000 local keypad as:

- data/load line: L23
- clock line: L24
- 4 us load pulse
- same data GPIO temporarily driven low, then switched back to input
- active-low samples
- clock low/high pulses around 3 us each
- 12 logical button samples

Therefore the XGO built-in P1 and wired P2 implementation is structurally the same type of shift-register interface as the SF2000 local keypad, merely moved to different GPIOs and duplicated for two player channels.

This is much stronger evidence than generic "serial controller" similarity.

## Stock SNES controller comparison

A stock SNES controller reports 16 serial bits. Manually read, the standard order begins:

1. B
2. Y
3. Select
4. Start
5. Up
6. Down
7. Left
8. Right
9. A
10. X
11. L
12. R
13-16. signature zeros

The SNES host interface uses **separate latch, clock, and data lines**. A latch pulse captures all buttons, then clock transitions advance the shift register while the host reads the data line.

The XGO differs in two important ways:

1. it does not expose a separately traced latch signal in the active wired scanner; instead, it drives the eventual data pin low and then releases it to input;
2. its 12-sample logical order differs materially from the SNES serial report order.

So an original SNES controller should **not** be assumed to work through a passive pin adapter.

It is still a useful candidate for an *active* adapter, because both sides are simple synchronous shift-register-style protocols.

## Stock NES controller comparison

A stock NES/Famicom controller uses the same basic three-signal architecture as SNES but reports only eight buttons in this order:

1. A
2. B
3. Select
4. Start
5. Up
6. Down
7. Left
8. Right

Again, the host provides a separate latch/strobe line, a separate clock line, and reads serial data from a third line.

The XGO P2 interface therefore does not directly match a stock NES controller either.

## Important comparison: SUP/Retro-FC-style micro-USB controllers

A separate family of inexpensive Famiclone handhelds uses a micro-USB connector for Player 2 even though **no USB protocol is involved**.

Published reverse engineering of SUP/Retro-FC-style handhelds shows the five micro-USB pins being repurposed for:

- power
- ground
- data from controller
- clock to controller
- latch to controller

These handhelds use the classic Famicom/NES controller protocol over the micro-USB shell. Standard USB controllers do not work, while a real NES controller can work through a passive rewiring adapter.

This is a very important precedent for interpreting the XGO Handle Interface: a micro-USB-shaped second-controller port absolutely can be a non-USB gamepad bus.

However, the known SUP/Famicom implementation is **not the same bus as the XGO scanner**, because SUP exposes the classic three-signal latch/clock/data protocol whereas the traced XGO scanner uses a bidirectional data/load line plus shared clock.

Therefore a generic SUP/Q2/Famicom-clone micro-USB controller is an interesting physical reference but should not presently be classified as XGO-compatible.

## Why the earlier USB experiments behave the way they do

The family comparison reinforces the conclusion that ordinary USB HID controllers are the wrong class of device for the stock Handle Interface.

A USB HID gamepad expects:

- differential D+/D- USB signaling
- enumeration
- descriptors
- host scheduling

The XGO wired scanner instead expects deterministic GPIO-level serial behavior every scan cycle.

This explains why DragonRise, Vilros, GP2040-as-HID, and other USB controllers do not become valid P2 devices merely because their connector fits through an adapter.

## Implication for original NES/SNES controllers

The user's original SNES and NES controllers remain useful, but the likely use case is now clearer:

### Passive adapter

**Not currently supported by the evidence.**

A passive SNES-to-XGO cable would require the XGO Handle Interface to provide a separate latch line and SNES-compatible bit timing/order. The active firmware scanner does not show that contract.

### Active protocol converter

**Technically plausible and low complexity.**

A microcontroller could:

1. read a real SNES or NES controller using its normal latch/clock/data interface;
2. cache the button state;
3. emulate the XGO/SF2000-style bidirectional data/load + clock response expected on P2;
4. reorder the buttons into the XGO's 12-bit sequence.

This would be far simpler than implementing USB host support on the stock XGO.

## Current compatibility ranking

### Very strong architectural match

- an original XGO accessory, if one can be identified
- an accessory using the same SF2000-style local keypad shift-register contract

### Potentially adaptable

- original SNES controller through an active translator
- original NES controller through an active translator
- GP2040-capable microcontroller running custom bus-emulation firmware

### Interesting but currently unproven

- SUP/Q2/Retro-FC micro-USB second-player controllers using classic Famicom signaling

### Very unlikely on stock firmware

- USB HID controllers
- Bluetooth controllers
- 8BitDo receivers presenting USB HID
- Xbox/PlayStation/Switch controllers

## Next hardware question

The most decisive remaining wired-P2 question is the exact Handle Interface pinout.

We now know the SoC-side logical signals that must reach the connector for the XGO scanner:

- P2 bidirectional data/load: L0
- shared controller clock: B7
- power
- ground
- one remaining connector contact or board function

Continuity from the connector pins to L0/B7 would determine whether the port exposes the scanner directly or passes through an intermediate transistor/switch circuit.

Until that mapping is known, do not assume USB pin names correspond to their normal USB functions.