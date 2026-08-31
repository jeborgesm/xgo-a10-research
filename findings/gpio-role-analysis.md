# GPIO Role Analysis — P1/P2 Serial Channels

Status: **firmware role assignment is now stronger; physical connector routing remains unconfirmed**.

## Key observation

The XGO controller task scans two serial button streams in fixed software slots:

```text
B15 -> serial state[0]
L0  -> serial state[1]
B7  -> shared clock
```

These are later merged slot-for-slot with RF controller states:

```text
serial[0] OR RF[0] -> player slot 0
serial[1] OR RF[1] -> player slot 1
```

The RF decoder independently establishes slot 0/slot 1 using the stock SF2000 P1/P2 status behavior, so the serial slots are not arbitrary scratch buffers.

## Startup GPIO initialization

The same controller/RF initialization routine around `0x8035deb0` configures the serial GPIOs before the RF self-test.

Relevant setup behavior reconstructed from the register masks:

```text
B15 direction -> input
L0  direction -> input
B7  direction -> output
B7  output    -> high/idle
```

This is consistent with the later periodic scan routine, which temporarily changes B15/L0 to outputs for the load phase and then returns them to input.

The fact that these pins are explicitly initialized in the main controller subsystem before RF setup further supports that they are intentional board-level controller signals.

## Which channel is probably built-in P1?

The strongest current assignment is:

```text
B15 -> built-in controls / Player 1
L0  -> external Handle Interface / Player 2
B7  -> shared serial clock
```

Why this assignment is stronger now:

1. B15 populates serial slot 0.
2. L0 populates serial slot 1.
3. RF slot 0/1 corresponds naturally to P1/P2.
4. The XGO's built-in controls operate as the primary player controls in normal use.
5. The device exposes one additional dedicated connector labeled `Handle Interface`, naturally matching the otherwise unexplained second local/wired slot.

This still stops short of physical confirmation because the board trace from L0 to the micro-USB-looking connector has not been observed directly. In principle, intermediary logic or an unusual remap could exist.

## Other nearby GPIO activity

A separate read of `0xb8800050` with mask `0x20000000` appears in the same broad controller task, but control flow leads to LCD/TV mode handling rather than controller decoding. It should not be treated as Handle Interface detection.

This removes one nearby false lead and keeps the controller bus itself narrowly defined around B15, L0, and B7.

## Relationship to RF initialization

The controller and RF GPIO setup share the same initialization function. This does **not** mean B7 is an RF clock. The RF bit-banged bus uses the previously identified high-order GPIO masks (`0x08000000`, `0x10000000`, `0x20000000`). B7 is separately configured as a low-order bit in the B-bank output register and is used by the serial controller scanner.

This mixed initialization is consistent with a single joystick/input subsystem bringing up both wired/local and wireless input hardware together.

## Current confidence

### CONFIRMED from executable code

- B15 feeds serial controller state slot 0.
- L0 feeds serial controller state slot 1.
- B7 clocks both streams.
- B15 and L0 are initialized as inputs by the controller subsystem.
- B7 is initialized as an output and driven to its idle state.
- the two serial slots merge with the two RF slots position-for-position.

### VERY STRONG INFERENCE

- B15 is the built-in Player 1 stream.
- L0 is the external Player 2 stream intended for the Handle Interface.

### NOT YET PHYSICALLY CONFIRMED

- L0 continuity to a specific Handle Interface contact.
- B7 continuity to a specific Handle Interface contact.
- connector supply voltage and ground pin assignment.
- whether any connector contact is also tied to H1512 USB0/USB1 or OTG-ID logic.

## Practical implication

The next physical test can now target only the likely P2 side. If the Handle Interface exposes the reconstructed serial bus directly, one non-power contact should correspond to L0 data and another to B7 clock. Passive probing or continuity should be enough to distinguish this from ordinary USB before connecting additional controllers.
