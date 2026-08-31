# USB Controller / Adapter Experiment Matrix

Status: **physical behavior confirmed; electrical pin mapping still unconfirmed**.

## Purpose

These tests separate ordinary USB-controller activity from the wiring difference introduced by a micro-USB OTG adapter on the XGO `Handle Interface`.

## Results

```text
Connection                                      Recognized?   Built-in controls
--------------------------------------------------------------------------------
normal/non-OTG micro-USB connection             n/a           normal
non-OTG + generic USB SNES-style controller     no            normal
non-OTG + inexpensive PS-shaped USB gamepad     no            normal
non-OTG + GP2040-CE                             no            normal
bare OTG adapter, USB-A side empty              n/a           freezes immediately
```

The freeze therefore does **not** require an attached USB peripheral and is not GP2040-specific.

Three substantially different active USB controller implementations can be attached through a non-OTG path without disturbing the XGO. They are simply ignored.

## Pin-4 observation

A micro-USB OTG adapter conventionally ties the ID contact (pin 4) to ground, while ordinary/non-OTG cables leave ID open.

Fine sewing-needle probe extensions were used to check the adapter unpowered. Resistance-mode probing produced a ground-related reading on pin 4. The short cable and two-hand probing setup made precision resistance measurement difficult, so this is recorded as qualitative confirmation rather than an exact resistance value.

## Interpretation

The experiment matrix strongly disfavors these explanations:

- GP2040-specific electrical incompatibility as the cause of the freeze;
- ordinary USB D+/D- traffic as the cause of the freeze;
- generic USB HID enumeration failure as the primary freeze trigger;
- VBUS or simple connector insertion alone as the cause.

The strongest remaining discriminator is the OTG-specific ID state.

Combined with firmware analysis showing that both local controller channels are continuously scanned with no software P2-present gate, the leading model is:

```text
ID/open-like state
    -> external serial channel remains electrically inactive/high
    -> normal built-in controls

ID grounded by OTG adapter
    -> an XGO-repurposed/coupled controller signal is forced asserted
    -> controller subsystem appears frozen
```

The strongest specific hypothesis is that micro-USB pin 4 is, or is electrically coupled to, the external/P2 active-low serial DATA line. Grounding it would then produce a continuously asserted input stream.

A lower-confidence alternative remains that ID grounding triggers a hardware-level USB/pinmux mode below the reconstructed application controller code.

## Confidence

### CONFIRMED physically

- empty OTG adapter alone freezes built-in controls;
- non-OTG connection alone does not freeze controls;
- generic USB SNES-style controller through non-OTG is not recognized and does not freeze controls;
- PS-shaped generic USB controller through non-OTG is not recognized and does not freeze controls;
- GP2040-CE through non-OTG is not recognized and does not freeze controls.

### STRONG EVIDENCE

- generic USB HID is unlikely to be the intended Handle Interface protocol;
- the OTG-specific micro-USB wiring difference is electrically meaningful to the XGO;
- pin 4 / ID is the leading physical discriminator.

### NOT YET CONFIRMED

- exact connector pinout;
- direct continuity from pin 4 to B15 or L0;
- whether B15 or L0 is P2;
- whether ID grounding creates a stuck-low P2 stream versus a lower-level mode change.

## Best next discriminator

Launch the bundled `Resources/Test.zsf` controller diagnostic and observe P1/P2 state while inserting the bare OTG adapter.

If P2 shows many/all buttons asserted, that would strongly support the stuck-low P2 DATA model. If the entire controller state stops updating, a lower-level mode/pinmux explanation becomes more plausible.
