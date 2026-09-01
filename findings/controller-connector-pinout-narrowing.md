# Controller connector electrical model narrowing

## Status
Comparison of XGO firmware/physical behavior against SF2000, X60 and DY12 evidence after confirming XGO/SF2000 serial keypad protocol equivalence.

## Headline
The remaining Handle Interface problem is now primarily **physical routing**, not protocol identification.

XGO firmware implements the same 12-position active-low serial button contract as SF2000, but exposes two parallel data streams (B15 and L0) on shared clock B7. External evidence independently shows that X60/DY12 wired controllers interoperate with SF2000 as Player 2 through a connector adapter, and X60 uses micro-USB specifically as an external-controller connector.

The strongest current model is that the XGO micro-USB Handle Interface exposes or couples into some subset of the XGO GPIO scanner signals directly. The exact micro-USB contact mapping remains unconfirmed.

## Important correction: OTG diagnostic result is R-only, not all-buttons

**Confirmed physical observation:** with the anonymous empty OTG adapter inserted, the controller diagnostic reports **R pressed**, not all buttons pressed.

Because the confirmed serial order is:

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

R-only means the disturbance is specific to the **first sampled bit** of the serial transaction. A simple permanently grounded DATA line is therefore not a good model.

## New narrowing from the X60 -> SF2000 adapter test

The X60 owner `dc_ScAn` reported using a normal Type-C-to-micro-USB adapter to connect an X60 wired controller to an SF2000; the SF2000 recognized it as Player 2.

That matters because a standards-compliant USB Type-C to USB 2.0 Micro-B passive cable/adapter carries:

- VBUS
- D-
- D+
- GND

while the Micro-B **ID pin is not part of the ordinary transport path**. USB-IF Type-C wiring tables explicitly show Micro-B pin 4 (ID) separate from the D+/D-/VBUS/GND conductors.

Therefore, assuming the owner's adapter was an ordinary passive consumer adapter rather than a specially rewired one, the working X60 -> SF2000 path strongly implies that the controller protocol itself travels over the contacts corresponding to **D+ and D- plus power/reference/ground**, not through Micro-B ID.

This is not yet a literal pinout proof because the adapter was not opened and traced, but it materially lowers the probability that ID is one of the actual serial transport wires.

### Consequence for XGO

The XGO OTG result should now be interpreted differently:

- the controller bus is most likely carried on **D-/D+** as DATA/CLOCK;
- Micro-B **ID is more likely detect, reset/load, gating, bias, or a coupled control input**;
- grounding ID with an OTG plug perturbs the first-bit timing/state and produces R-only.

This fits the family evidence better than treating ID itself as DATA or CLOCK.

## Important comparator: reference USB wiring is not retail controller wiring

Current FrogQEMU documentation contains the HC15xx DB-B210-V1.1 **reference-board** USB schematic mapping:

- USB0PP/USB0PN -> reference micro-USB connector
- USB1PP/USB1PN -> reference USB-A connector

However, FrogQEMU explicitly warns that the reference schematic is **not guaranteed to match retail boards**. Runtime probes on retail hardware are treated as authoritative.

Independent SF2000 retail reverse-engineering says its Type-C data contacts are used for a proprietary wired-gamepad poll rather than ordinary USB HID, and X60 retail hardware explicitly dedicates micro-USB to the external controller while charging uses a separate Mini-USB connector.

Therefore the OEM family demonstrably reuses USB-shaped connectors and the nominal USB D+/D- contacts for non-USB controller signaling.

## Family evidence convergence

### SF2000
Confirmed/open reconstruction:

- local serial keypad data L23
- serial keypad clock L24
- active-low
- host drives data low for load/reset, then returns it to input
- 12 serial positions
- exact logical order R,Y,X,L,A,B,SELECT,START,UP,DOWN,LEFT,RIGHT

Retail/community evidence:

- Type-C data contacts poll a simplified proprietary wired controller protocol
- standard USB wired controllers do not work
- Hamy Max wired controller works after connector rewiring
- X60/DY12 bundled controllers work through an adapter

### X60
Community hardware evidence:

- same core platform as SF2000
- board-specific display and input GPIO routing
- no SF2000 XN297 wireless receiver on the examined X60
- retail external-controller connector is micro-USB on documented variants
- controller-facing connector observed at roughly 3 V rather than ordinary USB expectations
- supplied wired controller tested successfully on SF2000 and recognized as Player 2
- test used a Type-C/micro-USB adapter, strongly suggesting the interoperable signal path is carried on the ordinary passive adapter conductors

### XGO
Confirmed:

- Handle Interface is physically micro-USB
- generic GP2040-CE USB controller does not operate as Player 2
- normal micro-USB cable does not disturb controls
- empty OTG adapter changes controller behavior
- hidden controller diagnostic shows **R asserted** with the anonymous OTG adapter
- firmware scanner uses B15 DATA0 + L0 DATA1 + shared B7 CLOCK
- both streams are active-low and loaded by host-driven-low pulse
- exact SF2000 12-button serial ordering

## What R-only tells us about the electrical disturbance

The XGO transaction sequence is important:

1. host configures both DATA lines as outputs;
2. host drives both DATA lines low;
3. waits about 4 us;
4. switches both DATA lines back to input;
5. **samples bit 0 (R) immediately**;
6. pulses the shared clock;
7. samples bit 1 (Y), then subsequent bits.

Unlike the hardened UniFrog SF2000 implementation, where a separate 4 us input-settle delay is deliberately inserted after returning DATA to input, no equivalent explicit settle delay has yet been identified in the XGO stock scanner.

### Strong inference: delayed DATA release / first-sample contamination

If grounding ID through the OTG adapter is electrically coupled to one XGO DATA/load path through a resistor, transistor, protection structure, mux, pull network, or detect circuit, the host-driven-low load phase may not release cleanly when the GPIO switches back to input.

A short low-going tail lasting only until the first sample would produce exactly:

```text
bit 0 R      = low  -> pressed
bit 1 Y      = high -> released
bit 2 X      = high -> released
...
bit 11 RIGHT = high -> released
```

The lack of an explicit settle delay makes this one-bit artifact technically plausible.

## Pinout hypotheses ranked after the adapter evidence

### H1 — D-/D+ carry DATA/CLOCK; ID affects detect/load/gating
**Plausibility: strongest current model.**

This now fits both device-family interoperability and XGO behavior:

- X60 controller works through an ordinary-looking Type-C/micro-USB adapter;
- passive adapters carry D+/D-, VBUS and GND as the useful cross-connector conductors;
- SF2000 documentation says its USB-shaped data contacts are used for controller polling;
- normal XGO cable with ID open is harmless;
- OTG plug grounds ID and produces the R-only first-bit artifact.

### H2 — ID is coupled to DATA/load circuitry and causes first-bit contamination
**Plausibility: strong as a control/coupling mechanism, not as the primary transport wire.**

This explains why grounding ID changes only bit 0 without requiring ID to carry the serial stream.

### H3 — ID directly carries DATA or CLOCK
**Plausibility: reduced.**

The X60 -> SF2000 passive-adapter interoperability makes ID-as-primary-transport harder to reconcile because ordinary Type-C/Micro-B adapters do not use Micro-B ID as one of the USB 2.0 data conductors.

It remains possible only if the specific adapter was nonstandard or if the devices exploit some unusual internal connection.

### H4 — lower-level pinmux/USB-OTG mode response
**Plausibility: possible but weaker.**

No convincing application-level XGO path has been found that gates the B15/L0/B7 scanner on USB/OTG state. A lower-level hardware effect remains possible, but direct electrical coupling now requires fewer assumptions.

### Discarded simple model — ID hard-grounded DATA
**Plausibility: poor / contradicted.**

A permanently grounded active-low DATA stream predicts all twelve sampled positions asserted. The hidden diagnostic instead reports R-only.

## Current working physical model

The best-supported model to test is now:

```text
micro-USB D- / D+   -> proprietary DATA / CLOCK (order unknown)
micro-USB GND       -> controller reference
micro-USB VBUS      -> controller supply/reference, likely ~3 V family behavior rather than normal USB semantics
micro-USB ID        -> detect/load/gate/bias or coupled control; grounding it perturbs sample 0
```

The D-/D+ DATA/CLOCK assignment remains unordered. Either could be B7 clock or the external B15/L0 data stream.

## Strongest next measurements

1. measure idle DC voltage on micro-USB pins 1-4 relative to GND with nothing inserted;
2. repeat with a normal micro-USB plug inserted but otherwise disconnected;
3. repeat with the empty OTG adapter inserted;
4. logic-analyze D- and D+ while the controller diagnostic is running;
5. identify which line has periodic shared-clock activity and which carries active-low serial samples;
6. compare DATA release immediately after the 4 us load pulse with the first R sample;
7. inspect ID simultaneously to see whether grounding it lengthens the first DATA-low interval.

A D+/D- waveform showing one clock line and one 12-bit active-low data line would effectively solve the Handle Interface transport mapping.

## What would constitute pinout confirmation

A connector pin can be assigned to an XGO GPIO only after at least one of:

- direct PCB continuity from connector contact to SoC/test-point net;
- logic-analyzer waveform matching reconstructed B7 clock timing;
- data waveform matching the 12-bit active-low scanner and known button presses;
- controlled pull test producing a deterministic known bit position in diagnostic mode.

## Research consequence

The firmware/protocol question is substantially solved. The new adapter evidence narrows the likely transport from five micro-USB contacts to the ordinary passive-adapter path, with **D+/D- now the leading DATA/CLOCK pair** and ID demoted to a control/coupling role.

Highest-value work is now:

- map XGO D+/D- electrically;
- recover exact X60-to-SF2000 adapter wiring if possible;
- recover/analyze X60 or DY19 firmware;
- compare connector waveforms to the known B15/L0/B7 scanner;
- only then build an adapter or controller emulator.

## Sources
- USB-IF, USB Type-C Cable and Connector Specification, Type-C to USB 2.0 Micro-B cable assembly wiring table
- `axgdev/UniFrog`, `foundation/src/platform/sf2000/input/unifrog_input.c`
- `axgdev/frogqemu`, `docs/SF2000.md`
- `axgdev/frogqemu`, `docs/DEVICE_FAMILY.md`
- 4PDA SF2000 posts #394/#404: X60 ~3 V connector observation and X60 controller -> SF2000 P2 through Type-C/micro adapter
- 4PDA SF2000 post #2468: Hamy Max and X60/DY12 wired-controller compatibility
- XGO firmware scanner reconstruction and physical OTG/controller-diagnostic experiment documented in this repository
