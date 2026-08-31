# Player 2 revisit and Handle Interface architecture

## Summary

Revisiting the XGO input path with the accumulated physical experiments makes the Player 2 design clearer.

The strongest current model is:

```text
built-in P1 serial data  -> GPIO B15 --\
                                      +-- shared scanner / shared clock B7
Handle Interface P2 data -> GPIO L0  --/

optional RF P1/P2 states are ORed with the corresponding wired serial state
```

The external Handle Interface is therefore **not treated by the stock firmware as a generic USB HID host port**. It is a second controller serial channel sampled in parallel with the built-in controls.

This explains why ordinary USB controllers have consistently failed and why USB-style electrical behavior at the connector is misleading.

## Two serial controller channels are scanned together

The main input routine at `0x8035d4c4` operates over two player slots in a loop whose index is bounded by `< 2`.

For each player it combines two state sources:

```text
serial[player] OR rf[player]
```

and translates the resulting raw button word into the frontend/core event layout.

The local serial states are built from two independent GPIO data lines while using the same clock sequence:

- **P1 data:** GPIO B15 (`0xb8800350`, bit 15)
- **P2 data:** GPIO L0 (`0xb8800050`, bit 0)
- **shared clock:** GPIO B7 (`0xb8800354`, bit 7)

Both channels are sampled during every serial scan. There is no software-side USB enumeration, HID descriptor parser, or external-controller attach gate in this path.

## GPIO initialization confirms the roles

Initialization around `0x8035deb0` configures the corresponding GPIO groups so that B15 and L0 can serve as controller data inputs and B7 as the host-driven clock/output line.

The scanner then performs its host-driven load/reset/sampling sequence and collects the same 12-button layout from both channels.

The decoded raw order is:

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

Thus P2 is architecturally a peer of P1, not an afterthought added by a separate USB stack.

## Generic player accessor supports both P1 and P2

A particularly useful result from this revisit is the input accessor at `0x803526a0`.

It first snapshots the translated controller states via `0x8035e360`, then indexes the pair using:

```text
base = gp - 0xd34
state = base[player_index]
```

where `player_index` is multiplied by four before indexing.

This means the accessor is explicitly designed for at least:

- index 0 = Player 1
- index 1 = Player 2

So the firmware has a genuine two-player abstraction above the GPIO scanner.

## Frontend UI intentionally uses only Player 1

All currently traced direct calls to `0x803526a0` from the XGO menu/frontend pass `player_index = 0`.

Examples include the main menu, search/navigation paths, pause-related UI, and the hidden diagnostic-launch logic. The hidden L+SELECT check also reads the Player 1 snapshot directly.

This is important because it explains a design distinction:

- the **frontend is P1-driven**;
- the lower input layer and emulator-facing abstraction are **two-player capable**.

The existence of P2 therefore should not be judged by whether the second controller can navigate the XGO menu. A working P2 controller may only become useful once a game/core is running.

## Raw + RF merge is per player

The state builder keeps two serial words and two RF words. For each player it computes:

```text
combined[player] = serial[player] | rf[player]
```

This confirms that the retained SF2000 wireless-controller path and the wired Handle Interface are alternative sources for the same Player 2 logical slot.

There is no evidence that the Handle Interface is supposed to become USB HID and then be translated into P2. It feeds the same logical controller layer much lower down.

## Reinterpreting the OTG-adapter experiments

Physical experiments showed:

- an empty OTG adapter causes immediate controller-input failure;
- removing it restores controls;
- a normal/non-OTG micro-USB-to-USB adapter does **not** cause that failure;
- resistance testing showed the OTG adapter's defining difference is micro-USB **ID pin 4 tied to ground**;
- generic USB controllers connected through ordinary wiring are not recognized;
- DragonRise and Vilros USB controllers produce invalid/stuck behavior in the hidden controller diagnostic rather than normal P2 input;
- the connector's D+/D- voltages with a DragonRise board do not resemble a clean conventional USB-host negotiation.

Taken together with the firmware, this substantially changes the interpretation of the connector.

### Strong hypothesis: USB-shaped connector, non-USB controller signaling

The Handle Interface appears to use a micro-USB-shaped connector while repurposing at least some pins for the XGO/SF2000-family controller serial interface.

The OTG ID-to-ground strap likely forces one of those repurposed electrical lines into an invalid state or causes contention with the controller scanner. Exactly which physical micro-USB pin maps to B15/L0/B7 has **not** yet been continuity-confirmed, so the individual connector-pin assignment remains open.

What can now be said with much more confidence is that grounding the USB ID pin is meaningful to this nonstandard interface and should **not** be interpreted as ordinary USB host-mode negotiation.

## Why an empty OTG adapter can disrupt input

The software continuously scans both controller channels and has no external-device presence gate.

Therefore a connector-side electrical condition that holds a controller signal at an invalid level can be seen continuously by the scanner. Because P1 and P2 share the scan timing/clock machinery, electrical contention or a stuck shared/control line can disturb normal input even when no actual controller is attached.

This is more consistent with the observed immediate input loss than a failed USB enumeration would be. A normal USB host stack should not normally make the built-in controls disappear merely because an empty OTG adapter is present.

The exact mechanism remains to be physically proven; possibilities include:

- the OTG ID-ground strap directly loading a repurposed controller signal;
- the connector wiring coupling to the shared clock/load sequence;
- a board-level switch/transistor that changes the controller bus when the ID-related line is grounded.

Do not pick one without continuity or oscilloscope evidence.

## Implication for controller experiments

Generic USB gamepads are now considered the wrong protocol family for the Handle Interface unless an active protocol-conversion adapter is built.

The more productive targets are:

1. identify the physical connector-pin mapping for P2 data, shared clock/load/control, power, and ground;
2. reproduce the expected 12-bit serial response electrically;
3. test P2 inside an actual two-player game rather than relying on frontend navigation;
4. if desired, build a small microcontroller adapter that translates a modern USB/gamepad protocol into the XGO's expected serial controller stream.

A GP2040-class microcontroller could potentially serve as such a translator, but **not by presenting itself as USB HID directly to the Handle Interface**. It would need custom firmware that emulates the XGO controller bus timing.

## Current confidence table

### CONFIRMED

- stock firmware has two controller/player slots;
- P1 and P2 are scanned in the same low-level routine;
- P1 serial data is B15;
- P2 serial data is L0;
- B7 is the shared scan clock;
- each player receives a 12-button raw serial state;
- RF state is ORed with the corresponding serial state per player;
- the generic input accessor supports player indices 0 and 1;
- traced frontend/menu calls use player index 0 only;
- no generic USB HID enumeration exists in the active P2 scanner path.

### STRONG EVIDENCE

- the Handle Interface is a USB-shaped connector carrying a proprietary/SF2000-family controller serial interface rather than ordinary USB HID;
- the OTG ID-ground strap interferes with the repurposed controller bus rather than simply enabling a USB host controller;
- P2 is primarily intended for gameplay/core use, while the frontend remains P1-controlled.

### OPEN

- exact mapping from micro-USB connector pins 1-5 to power/ground/B7/L0/other controller signals;
- exact external controller electrical circuit and shift-register/protocol implementation;
- whether any original XGO-branded controller/accessory existed for this Handle Interface;
- whether P2 works correctly in each individual embedded emulator/core;
- exact electrical reason an empty OTG adapter disrupts input.

## Recommended next experiment

The highest-value low-risk test is now **software-first**: choose a known two-player NES/SNES/Arcade title, launch it normally, enter a two-player mode using P1, and observe the game's P2 behavior while changing only the Handle Interface electrical condition.

For hardware reverse engineering, the next decisive measurement would be continuity from the five Handle Interface connector pins to the known controller GPIOs **L0 and B7** (and ground/power). That would turn the current bus model into a concrete connector pinout. Until then, avoid treating the connector as standard micro-USB merely because of its physical shell.