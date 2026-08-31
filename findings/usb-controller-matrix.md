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

USB low-speed devices advertise attachment with a nominal 1.5 kOhm pull-up on **D-**.

## Powered data-line measurements

Using the non-OTG path and DC voltage mode, the accessible USB-A data contacts were measured relative to ground while the XGO was powered:

```text
                         D-       D+
nothing attached        0.01 V   0.01 V
DragonRise 0079:0006    3.20 V   2.80 V
```

This is a major new discriminator.

With no peripheral attached, both nominal USB data contacts sit essentially at ground potential. When the DragonRise board is attached and powered, **both data contacts rise strongly**, not only D-.

The 3.20 V level on D- is consistent in magnitude with a low-speed USB attach pull-up. The simultaneous ~2.80 V reading on D+ is not what a simple conventional idle low-speed USB bus would predict, where D+ should remain near the host-side low state.

Therefore the XGO Handle Interface should not be modeled as a straightforward standards-compliant USB host port based on these DC readings alone.

Possible explanations for the elevated D+ reading include:

- the XGO is actively driving or biasing the contact for its proprietary controller scan;
- the contact carries a fast digital waveform and the handheld multimeter is reporting only its time-averaged value;
- there is resistive/protection-network coupling between the DragonRise USB interface and XGO-side controller circuitry;
- the USB-shaped connector is electrically multiplexed between USB-like and proprietary-controller functions.

A multimeter cannot distinguish these waveform possibilities; oscilloscope/logic-analyzer capture would be required for direct timing proof.

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

The combination of these observations is important:

```text
DragonRise 0079:0006
    -> low-speed USB family
    -> D- reaches ~3.20 V when attached
    -> D+ simultaneously measures ~2.80 V

XGO serial scanner
    -> drives controller DATA low during load
    -> releases DATA
    -> immediately samples R

Observed
    -> R stays asserted while encoder is attached
```

A simple static `D- == active-low DATA` mapping would predict a high/inactive level from the USB pull-up, so the result should **not** be interpreted as a direct D-=DATA proof.

The stronger interpretation is that the DragonRise transceiver/pull network interacts dynamically with one or more contacts used by the XGO scanner during the drive-low / release / first-sample transition. A brief low interval can be captured as R even while a multimeter reports a high average DC level.

Because **both D- and D+ change substantially**, D- can no longer be singled out solely from the voltage experiment. D- remains notable because of the DragonRise low-speed pull-up, but D+ is clearly electrically active in the same attached state and may be a scan clock/control contact or a coupled signal.

## Revised interpretation

The experiment matrix disfavors:

- GP2040-specific incompatibility as the primary issue;
- generic USB HID being the intended Handle Interface protocol;
- a whole-system crash caused by OTG insertion;
- simple VBUS or mechanical insertion alone causing the OTG input failure;
- a naive model in which only one conventional USB data line changes while the other remains at a normal USB-host idle level.

The evidence now points to a **hybrid/multiplexed electrical overlap** model more strongly than before:

```text
micro-USB shell
    conventional USB contacts are physically present
    but D-/D+ electrical states are influenced by proprietary controller-scan circuitry
    and ID grounding affects the wider input subsystem
```

For the OTG case, ID grounding appears to disrupt the wider input subsystem.

For the DragonRise non-OTG case, both nominal USB data contacts become active/high in DC measurement while the first controller sample (R) is corrupted.

These effects may be produced by separate but overlapping hardware paths.

## Confidence

### CONFIRMED physically

- L + SELECT launches the bundled `Test.zsf` diagnostic;
- empty OTG adapter alone kills controller input while the test timer continues;
- non-OTG connection alone does not globally freeze controls;
- generic USB SNES-style controller through non-OTG is not recognized and does not globally freeze controls;
- PS-shaped generic USB controller through non-OTG is not recognized and does not globally freeze controls;
- GP2040-CE through non-OTG is not recognized and does not globally freeze controls;
- zero-delay USB encoder through non-OTG is not recognized but causes R to remain asserted in `Test.zsf`;
- the tested zero-delay encoder identifies as `VID_0079&PID_0006&REV_0107`;
- with nothing attached through the non-OTG path, D- and D+ each measure approximately 0.01 V;
- with the DragonRise board attached, D- measures approximately 3.20 V and D+ approximately 2.80 V.

### STRONG EVIDENCE

- `0079:0006` is a DragonRise `Generic USB Joystick` family device;
- the same VID/PID family enumerates as low-speed USB in independent host logs;
- low-speed USB places its attach pull-up on D-;
- generic USB HID is unlikely to be the intended Handle Interface protocol;
- the Handle Interface does not present a simple conventional USB-host idle electrical signature in this test;
- the OTG-specific micro-USB wiring difference is electrically meaningful to the XGO;
- the OTG failure is within the input subsystem rather than a general system hang;
- ordinary USB-device electrical state can influence the serial-input result;
- both D- and D+ participate electrically when the DragonRise board is connected.

### NOT YET CONFIRMED

- exact connector pinout beyond conventional shell/contact numbering;
- direct continuity from pin 4 to any controller GPIO;
- whether B15 or L0 is physically the external controller channel;
- which of D-/D+ corresponds to controller DATA, shared CLOCK, control, or only coupled/multiplexed signals;
- waveform shape on D-/D+ during the serial scan;
- whether OTG ID grounding changes pinmux, shared clock behavior, or other accessory-interface hardware.

## Best next discriminator

The most useful no-purchase comparison is now another already-available USB controller whose USB signaling differs from the DragonRise board.

The GP2040-CE is especially valuable because it previously produced **no R-stuck symptom** through the same non-OTG path. Measure D- and D+ in DC-voltage mode with the GP2040 connected under the same conditions.

If the GP2040 produces a different D-/D+ voltage pair while `Test.zsf` remains normal, that differential signature may tell us which contact/state correlates with the R-only corruption.

Do not use resistance/continuity mode on the powered XGO and do not bridge adjacent contacts.
