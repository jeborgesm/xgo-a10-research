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

## Zero-delay encoder: why R matters

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

That gives the R-only result a plausible electrical explanation:

```text
XGO drives candidate DATA contact low
        -> releases it
        -> attached USB encoder / pull network delays its rise
        -> immediate sample 0 still reads low = R pressed
        -> line reaches high before later samples
        -> remaining buttons inactive
```

This is a timing hypothesis, not yet a pinout identification.

However, it means ordinary USB-contact electrical behavior is not completely irrelevant: a non-OTG USB device can perturb the serial scanner without ID grounding and without being recognized as USB HID.

Many inexpensive `DragonRise` / `Generic USB Joystick` zero-delay encoders are documented by Linux systems as **low-speed USB HID** devices. Low-speed USB devices advertise themselves with a 1.5 kOhm pull-up on D-, whereas full-speed devices use D+. The exact encoder in this experiment has not yet been enumerated and identified, so its USB speed should not be assumed from appearance alone.

If this particular board is also low-speed, the R-only symptom would make **D- an especially interesting connector contact to compare against the suspected serial DATA line**. If it is full-speed instead, D+ becomes the corresponding candidate. This can be resolved safely by enumerating the encoder on a PC or by passive voltage measurement.

## Revised interpretation

The experiment matrix now disfavors these explanations:

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

For the zero-delay non-OTG case, one ordinary USB data-line state appears able to perturb only the first serial sample.

These two effects need not have the same mechanism.

## Confidence

### CONFIRMED physically

- L + SELECT launches the bundled `Test.zsf` diagnostic;
- empty OTG adapter alone kills controller input while the test timer continues;
- non-OTG connection alone does not globally freeze controls;
- generic USB SNES-style controller through non-OTG is not recognized and does not globally freeze controls;
- PS-shaped generic USB controller through non-OTG is not recognized and does not globally freeze controls;
- GP2040-CE through non-OTG is not recognized and does not globally freeze controls;
- zero-delay USB encoder through non-OTG is not recognized but causes R to remain asserted in `Test.zsf`.

### STRONG EVIDENCE

- generic USB HID is unlikely to be the intended Handle Interface protocol;
- the OTG-specific micro-USB wiring difference is electrically meaningful to the XGO;
- the OTG failure is within the input subsystem rather than a general system hang;
- ordinary USB data-line electrical state can influence the serial-input result;
- the zero-delay board's R-only result is consistent with a transient/recovery effect at the first post-load sample.

### NOT YET CONFIRMED

- exact connector pinout;
- direct continuity from pin 4 to any controller GPIO;
- whether B15 or L0 is physically the external controller channel;
- whether D+ or D- overlaps/couples to serial DATA;
- whether OTG ID grounding changes pinmux, shared clock behavior, or other accessory-interface hardware.

## Best next discriminator

Two safe options now have unusually high value:

1. enumerate the exact zero-delay board on a PC and record its VID/PID and USB speed; or
2. with the XGO powered, use only high-impedance DC-voltage measurements to compare the micro-USB contacts across: empty port, non-OTG cable, zero-delay encoder, and bare OTG adapter.

Do not use resistance/continuity mode on the powered XGO and do not bridge adjacent micro-USB contacts.
