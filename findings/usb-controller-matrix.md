# USB Controller / Adapter Experiment Matrix

Status: **physical behavior confirmed; electrical pin mapping still unconfirmed**.

## Purpose

These tests separate ordinary USB-controller activity from the wiring difference introduced by a micro-USB OTG adapter on the XGO `Handle Interface`.

## Results

```text
Connection                                      Recognized?   Input behavior
------------------------------------------------------------------------------------------
normal/non-OTG micro-USB connection             n/a           built-in controls normal
non-OTG + generic USB SNES-style controller     no            built-in controls normal
non-OTG + inexpensive PS-shaped USB gamepad     no            built-in controls normal
non-OTG + GP2040-CE                             no            built-in controls normal
non-OTG + zero-delay USB arcade encoder         no            Test.zsf shows R stuck on
bare OTG adapter, USB-A side empty              n/a           all controller input stops
```

The OTG symptom therefore does **not** require an attached USB peripheral and is not GP2040-specific.

Several substantially different active USB controller implementations can be attached through a non-OTG path without producing a global input failure. They are not recognized as usable controllers.

The zero-delay encoder is the first non-OTG device to expose a specific perturbation in the diagnostic: **R remains asserted**.

## Hidden diagnostic confirmation

Firmware analysis identified **L + SELECT** as an exact hidden trigger for `%s/Resources/Test.zsf`.

This was physically reproduced on the tested unit. The diagnostic allows all Player 1 controls to be observed normally with no accessory attached.

When the bare OTG adapter is inserted while this diagnostic is running:

- controller input stops responding;
- no new button acknowledgements appear;
- the on-screen timer continues advancing.

Therefore the apparent `freeze` is specifically an **input freeze**, not a CPU/emulator/application hang.

This weakens the simple `pin 4 grounded -> P2 DATA stuck low` model because P1 also becomes unusable while the program continues running.

## Pin-4 observation

A micro-USB OTG adapter conventionally ties the ID contact (pin 4) to ground, while ordinary/non-OTG cables leave ID open.

Fine sewing-needle probe extensions were used to check the adapter unpowered. Resistance-mode probing produced a ground-related reading on pin 4. The short cable and two-hand probing setup made precision resistance measurement difficult, so this is recorded as qualitative confirmation rather than an exact resistance value.

## Zero-delay encoder identification

Windows identifies the tested zero-delay encoder as:

```text
Generic USB Joystick
HID\VID_0079&PID_0006&REV_0107
```

This establishes:

```text
VID  = 0x0079  DragonRise Inc.
PID  = 0x0006
bcdDevice/revision = 1.07
```

Independent Linux reports for the same `0079:0006` / revision-family device enumerate it as **low-speed USB HID**. This is not inferred merely from the friendly name; it is supported by host enumeration logs for the same VID/PID family.

USB low-speed devices advertise attachment with a nominal 1.5 kOhm pull-up on **D-**. Therefore the tested encoder contributes a known D- bias/state when powered.

## Why R matters

The reconstructed XGO serial scan samples buttons in this order:

```text
0  R
1  Y
2  X
3  L
4  A
5  B
6  SELECT
7  START
8  UP
9  DOWN
10 LEFT
11 RIGHT
```

The firmware drives both serial DATA lines low for roughly 4 microseconds, releases them to input, and **immediately reads sample 0 / R**. Only afterward does it begin the shared-clock sequence for the remaining samples.

The combination of these two observations is now important:

```text
DragonRise 0079:0006
    -> known low-speed USB device family
    -> D- has the low-speed attach pull-up/state

XGO serial scanner
    -> drives DATA low during load
    -> releases DATA
    -> immediately samples R

Observed
    -> R stays asserted while encoder is attached
```

A simple static `D- == active-low DATA` mapping would actually predict a high/inactive level from the USB pull-up, so the result should **not** be overinterpreted that way.

The stronger interpretation is that the DragonRise transceiver/pull network interacts with a contact used by the XGO scanner during the host-drive-low / release transition. A delayed recovery, transceiver clamp, protection network, or multiplexed path could leave the first post-release sample low while later samples recover high.

Thus **D- is now the strongest ordinary-USB-contact candidate for electrical coupling to the controller scan**, but direct pin mapping is still unconfirmed.

## Revised interpretation

The experiment matrix disfavors:

- GP2040-specific incompatibility as the primary issue;
- generic USB HID being the intended Handle Interface protocol;
- a whole-system crash caused by OTG insertion;
- simple VBUS or mechanical insertion alone causing the OTG input failure.

The evidence now points to a **hybrid electrical overlap** model more strongly than before:

```text
micro-USB shell
    conventional USB contacts exist electrically
    but one or more contacts are also coupled to / shared with
    the HC15xx-style controller scan or its supporting pinmux/interface circuitry
```

For the OTG case, ID grounding appears to disrupt the wider input subsystem.

For the DragonRise non-OTG case, the known low-speed D- electrical state perturbs specifically the first serial sample.

These two effects need not have the same mechanism.

## Confidence

### CONFIRMED physically

- L + SELECT launches the bundled `Test.zsf` diagnostic;
- empty OTG adapter alone kills controller input while the test timer continues;
- non-OTG connection alone does not globally freeze controls;
- generic USB SNES-style controller through non-OTG is not recognized and does not globally freeze controls;
- PS-shaped generic USB controller through non-OTG is not recognized and does not globally freeze controls;
- GP2040-CE through non-OTG is not recognized and does not globally freeze controls;
- zero-delay USB encoder through non-OTG is not recognized but causes R to remain asserted in `Test.zsf`;
- the tested zero-delay encoder identifies as `VID_0079&PID_0006&REV_0107`.

### STRONG EVIDENCE

- `0079:0006` is a DragonRise `Generic USB Joystick` family device;
- the same VID/PID family enumerates as low-speed USB in independent host logs;
- low-speed USB places its attach pull-up on D-;
- generic USB HID is unlikely to be the intended Handle Interface protocol;
- the OTG-specific micro-USB wiring difference is electrically meaningful to the XGO;
- the OTG failure is within the input subsystem rather than a general system hang;
- ordinary USB data-line electrical state can influence the serial-input result;
- D- is currently the leading ordinary-USB contact to investigate for coupling with the serial scanner.

### NOT YET CONFIRMED

- exact connector pinout;
- direct continuity from pin 4 to any controller GPIO;
- whether B15 or L0 is physically the external controller channel;
- whether D- is directly connected, resistively coupled, multiplexed, or only indirectly affecting serial DATA;
- whether OTG ID grounding changes pinmux, shared clock behavior, or other accessory-interface hardware.

## Best next discriminator

The next high-value test should distinguish **D- from D+ without shorting either line**.

A safe method is a high-impedance DC-voltage comparison at the Handle Interface while powered, using a breakout or otherwise stable fine probes if available:

```text
state A: nothing attached
state B: non-OTG adapter only
state C: non-OTG + DragonRise 0079:0006
state D: bare OTG adapter
```

The DragonRise case should create a distinctive D- bias if ordinary USB pin numbering is preserved. Comparing which XGO contact changes in that state can identify the electrically relevant data contact without deliberately grounding it.

Do not use resistance/continuity mode on the powered XGO and do not bridge adjacent micro-USB contacts.
