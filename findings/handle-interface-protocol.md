# Handle Interface Serial Protocol — Current Reconstruction

Status: **firmware protocol timing confirmed; physical connector routing not yet confirmed**.

## Headline

The XGO firmware contains a continuously running two-channel synchronous serial controller scanner. It is not USB HID. The scanner uses two active-low DATA inputs in parallel with one shared CLOCK and produces two independent controller-state words.

The serial contract is now strongly tied to the SF2000/HC15xx family: XGO uses the exact SF2000 12-position logical button order and the same unusual host-driven-low load/reset mechanism. Its physical topology, however, is dual-data like the GB300-family scanner.

The external `Handle Interface` is physically micro-USB, but the connector-to-GPIO mapping remains unconfirmed.

## GPIO roles confirmed from XGO firmware

```text
B15  DATA channel 0   input register 0xb8800350 bit 15
L0   DATA channel 1   input register 0xb8800050 bit 0
B7   shared CLOCK     output register 0xb8800354 bit 7
```

Direction/control registers:

```text
B bank direction/control: 0xb8800358
L bank direction/control: 0xb8800058
```

Initialization near `0x8035deb0` establishes:

```text
B15 -> input at idle
L0  -> input at idle
B7  -> output
B7  -> high at idle
```

This setup is unconditional in the controller initialization path. No external-controller-present test is performed before configuring B15/L0/B7.

## Load/reset phase

The scanner clears both software controller states and performs:

```text
1. B15 -> output
2. L0  -> output
3. B15 = low
4. L0  = low
5. wait about 4 us
6. B15 -> input
7. L0  -> input
8. immediately sample bit 0
```

There is no separate latch line visible in the reconstructed XGO routine. The host temporarily takes ownership of both DATA lines and drives them low.

## Clocking

B7 is high at idle. After each pair of samples the scanner performs approximately:

```text
sample DATA0 + DATA1
CLOCK low
wait about 2 us
CLOCK high
sample next pair
```

The explicit delay is on the low phase. There is no separately identified post-release settle delay before the first XGO sample.

## Exact 12-position logical order

Both streams use:

```text
0   R       raw 0x1000
1   Y       raw 0x2000
2   X       raw 0x4000
3   L       raw 0x0800
4   A       raw 0x0080
5   B       raw 0x0040
6   SELECT  raw 0x0020
7   START   raw 0x0010
8   UP      raw 0x0008
9   DOWN    raw 0x0004
10  LEFT    raw 0x0002
11  RIGHT   raw 0x0001
```

This is position-for-position identical to the SF2000 local keypad serialization reconstructed by FrogQEMU.

## Polling and software state

The scanner runs periodically from the persistent controller task, approximately every fourth task phase. It does not wait for USB attach/enumeration.

Representative scheduling path:

```text
0x8035d50c  load poll counter
0x8035d510  counter & 3
0x8035d514  if zero -> scanner near 0x8035d770
...
0x8035d6c8  load counter
0x8035d6cc  increment
0x8035d6d0  store
```

The two serial state words are:

```text
gp - 0x0d2c   serial/local slot 0
gp - 0x0d28   serial/local slot 1
```

Direct references to these words are confined to the scanner. Elsewhere they are consumed as a two-element controller array and merged with RF/controller state. No separate software P2-connected flag or USB gate has been found.

## Relationship to SF2000 and GB300

XGO combines two traits that the current open-source family reconstruction shows separately:

### SF2000-like logical contract

- 12 samples
- active-low
- host drives DATA low, then returns it to input
- exact order `R,Y,X,L,A,B,SELECT,START,UP,DOWN,LEFT,RIGHT`
- high-idle clock and sample-then-pulse rhythm

### GB300-like physical topology

- two DATA lines
- one shared CLOCK
- both DATA lines driven low together for the load phase
- both DATA lines switched back to input together
- simultaneous active-low sampling

XGO differs from current UniFrog GB300 behavior in important ways:

- GB300 scans 16 shift positions; XGO scans 12;
- GB300 uses L27/L25 DATA and L26 CLOCK; XGO uses B15/L0 DATA and B7 CLOCK;
- GB300's current UniFrog normalizer ORs the two physical streams into one local-button mask; XGO preserves its two streams independently as controller slots;
- GB300 drives its clock low during the load phase in the current reconstruction, while XGO's B7 is initialized high and the reconstructed XGO load sequence only requires both DATA lines low.

The best description is therefore **SF2000 logical protocol implemented with a GB300-like dual-data topology**, not simply "the GB300 protocol".

## Cable/adapter physical evidence

Confirmed physical observations:

```text
normal micro-USB male -> USB-A male cable
    inserted into Handle Interface
    -> controls remain normal

empty micro-USB OTG adapter -> USB-A female
    inserted with nothing attached
    -> normal UI appears unusable

hidden controller diagnostic with that OTG adapter
    -> R is asserted
    -> not all buttons
```

The adapter was probed with fine needle extensions and showed behavior consistent with micro-USB pin 4 / ID being tied to ground, as expected for an OTG host adapter. Treat this as qualitative confirmation, not precision resistance characterization.

## Critical correction: OTG produces R-only, not all-buttons

Older analysis predicted that if ID directly grounded an active-low DATA line, every serial sample would be low and all twelve buttons would appear pressed.

That prediction is contradicted by the real controller diagnostic: **only R is observed asserted**.

Because R is serial position 0, the OTG effect is a first-sample artifact, not a simple continuously grounded DATA stream.

Do not use the obsolete `ID -> hard DATA -> all buttons` model as the active hypothesis.

## What R-only implies

The XGO scanner returns both DATA pins to input and then takes the first sample immediately. Modern UniFrog deliberately inserts a 4 us settle delay after that direction change on both its SF2000 and GB300 scanners.

This gives a concrete mechanism for R-only behavior: grounding ID may be electrically coupled to DATA/load/reset circuitry so that one DATA path remains low only briefly after release.

Possible transaction:

```text
host drives DATA low during load
host changes DATA to input
external/coupled circuit releases slowly
sample 0: low  -> R pressed
line recovers high
sample 1+: released
```

This is a **strong inference**, not yet a measured waveform.

Other still-possible explanations are a disturbed load/reset state or a start-of-frame/clock disturbance that only corrupts position 0.

## Current connector model

The strongest family-level model is that ordinary USB-shaped contacts carry the proprietary controller transport while micro-USB ID participates in detect/load/gating/bias or is otherwise electrically coupled to the controller interface.

A plausible mapping class is:

```text
D- / D+  -> DATA + CLOCK in unknown order
GND      -> reference
VBUS     -> controller supply/reference, voltage not yet confirmed
ID       -> detect/load/gate/bias/coupled control
```

This is not yet a pinout assignment. Which of D-/D+ maps to B7 and which to B15 or L0 remains unknown.

## Confirmed vs inference

### CONFIRMED from firmware

- two parallel active-low DATA streams;
- B15 and L0 are the two DATA inputs;
- B7 is the shared CLOCK output;
- B7 idle high;
- both DATA lines are driven low during load/reset;
- about 4 us explicit load delay;
- immediate first sample after returning DATA to input;
- about 2 us explicit clock-low delay;
- 12 samples per stream;
- exact SF2000 logical order;
- both streams are scanned unconditionally;
- no application-level P2 connection gate found;
- two streams remain independent software controller slots.

### CONFIRMED physically

- generic GP2040-CE USB controller does not function as P2;
- normal micro-USB cable does not disturb controls;
- empty OTG adapter does disturb controls;
- hidden diagnostic shows **R-only** under the anonymous OTG adapter;
- therefore the OTG behavior is not an all-buttons event.

### STRONG INFERENCE

- Handle Interface belongs to the same HC15xx/SF2000-family proprietary serial controller-bus lineage;
- XGO is a hybrid of SF2000 logical serialization and GB300-like dual-data topology;
- one serial stream is likely built-in controls and the other external Handle Interface;
- ID grounding perturbs the first-sample/load-release condition rather than permanently grounding the serial DATA stream;
- D-/D+ are stronger candidates for the main DATA/CLOCK transport than ID itself.

### NOT YET CONFIRMED

- whether B15 or L0 is the external stream;
- exact micro-USB contact assignment;
- which of D-/D+ is CLOCK;
- which of D-/D+ is external DATA;
- what ID is electrically connected to;
- connector logic/supply voltage and pull network;
- whether any conventional USB mode coexists with the proprietary bus.

## Highest-value next discriminator

Do not repeat the already-completed OTG resistance or controller-test experiments unless resolving a contradiction.

The next decisive evidence is electrical correlation of connector contacts with the reconstructed scanner:

1. measure pins 1-4 relative to ground with nothing inserted;
2. compare normal cable vs empty OTG adapter;
3. identify D-/D+ activity during controller polling;
4. with a logic analyzer, look for one pin matching B7's clock burst and the other matching a 12-bit active-low DATA stream;
5. inspect the DATA release immediately before bit 0 to test the R-only delayed-release model.

A periodic shared clock on either D- or D+ would reduce the remaining Handle Interface pinout problem to essentially one DATA assignment and one stream-role assignment.

## Sources

- XGO `bios/bisrv.asd` static reconstruction documented in this repository.
- `axgdev/frogqemu`, `qemu/hw/mips/sf2000.c` and `docs/SF2000.md`.
- `axgdev/UniFrog`, `foundation/src/platform/sf2000/input/unifrog_input.c`.
- XGO physical cable/OTG/controller-diagnostic experiments documented in the project history.
