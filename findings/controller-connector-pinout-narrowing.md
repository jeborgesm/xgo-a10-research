# Controller connector electrical model narrowing

## Status
Comparison of XGO firmware/physical behavior against SF2000, X60 and DY12 evidence after confirming XGO/SF2000 serial keypad protocol equivalence.

## Headline
The remaining Handle Interface problem is now primarily **physical routing**, not protocol identification.

XGO firmware implements the same 12-position active-low serial button contract as SF2000, but exposes two parallel data streams (B15 and L0) on shared clock B7. External evidence independently shows that X60/DY12 wired controllers interoperate with SF2000 as Player 2 through a connector adapter, and X60 uses micro-USB specifically as an external-controller connector.

The strongest current model is therefore that the XGO micro-USB Handle Interface exposes or couples into some subset of the XGO GPIO scanner signals directly. The exact micro-USB contact mapping remains unconfirmed.

## Important correction: OTG diagnostic result is R-only, not all-buttons

A previous version of this note carried an obsolete prediction that grounding micro-USB ID through an OTG adapter would hold an external DATA line low and therefore assert all twelve buttons.

That prediction is contradicted by the already-observed hidden controller diagnostic.

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

R-only means the disturbance is specific to the **first sampled bit** of the serial transaction. A simple permanently grounded DATA line is therefore no longer a good model.

This is substantially more informative than the original menu-freeze observation.

## Important new comparator: reference USB wiring is not retail controller wiring

Current FrogQEMU documentation contains the HC15xx DB-B210-V1.1 **reference-board** USB schematic mapping:

- USB0PP/USB0PN -> reference micro-USB connector
- USB1PP/USB1PN -> reference USB-A connector
- these are genuine HC15xx USB-controller signals on the reference design

However, the same project explicitly warns that the reference schematic is **not guaranteed to match retail boards**. Runtime probes on tested retail hardware are treated as authoritative.

This matters because independent SF2000 retail reverse-engineering says its Type-C data contacts are used for a proprietary wired-gamepad poll rather than ordinary USB HID, and X60 retail hardware explicitly dedicates micro-USB to the external controller while charging uses a separate Mini-USB connector.

Therefore we must not infer XGO Handle Interface pinout from the DB-B210 reference USB schematic. The OEM family demonstrably repurposes USB-shaped connectors and changes board routing between products.

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

Modern FrogQEMU device-family notes also list direct hardware LCD captures for `X60`, `DY12`, `DY12_MY2024`, `DY19`, Q19 and related boards, reinforcing that these are being treated as board variants inside the same HC15xx/SF2000 family rather than unrelated products.

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

## Minimum electrical signals required

For one external XGO serial stream, the protocol needs at minimum:

1. DATA — bidirectional at the host during load/reset, then input while sampling
2. CLOCK — host output
3. GND/reference

A controller may additionally require a power/reference supply, making four useful conductors.

A micro-USB receptacle provides five contacts:

1. VBUS
2. D-
3. D+
4. ID
5. GND

Therefore the connector has enough contacts for this proprietary bus with one spare/detect contact even without using it as USB.

## What R-only tells us about the electrical disturbance

The XGO transaction sequence is important:

1. host configures both DATA lines as outputs;
2. host drives both DATA lines low;
3. waits about 4 us;
4. switches both DATA lines back to input;
5. **samples bit 0 (R) immediately**;
6. pulses the shared clock;
7. samples bit 1 (Y), then subsequent bits.

Unlike the hardened UniFrog SF2000 implementation, where a separate 4 us input-settle delay is intentionally inserted after returning DATA to input, no equivalent explicit settle delay has yet been identified in the XGO stock scanner.

That makes the R-only OTG result especially significant.

### Strong inference: delayed DATA release / first-sample contamination

If grounding ID through the OTG adapter is electrically coupled to one XGO DATA path through a resistor, transistor, protection structure, mux, pull network, or other board circuitry, the host-driven-low load phase may not release cleanly when the GPIO switches back to input.

A short low-going tail lasting only until the first sample would produce exactly:

```text
bit 0 R      = low  -> pressed
bit 1 Y      = high -> released
bit 2 X      = high -> released
...
bit 11 RIGHT = high -> released
```

This is a much better fit for the observed R-only diagnostic state than a permanently grounded DATA line.

The fact that XGO apparently samples immediately after the direction change, while the modern SF2000 open implementation deliberately adds a settle delay, provides a concrete timing mechanism for such a one-bit artifact.

### Alternative: first-bit load/reset state is being altered

The accessory/ID contact may participate in the controller encoder's parallel-load/reset behavior rather than being DATA itself. Grounding it could force only the freshly loaded bit-0 state low, after which ordinary clocking shifts high values through the remaining positions.

This also predicts R-only without requiring DATA to remain clamped.

### Alternative: clock/start-of-frame disturbance

A disturbed clock/load edge could cause the scanner to sample a stale low state at position zero before the serial source reaches its normal idle state. This remains possible, especially if B7 or a load-equivalent signal is exposed or coupled through the connector.

## Pinout hypotheses ranked after the R-only observation

### H1 — ID is coupled to DATA/load circuitry and causes first-bit contamination
**Plausibility: strong.**

This now best explains all current observations:

- normal cable: ID open -> no disturbance;
- OTG adapter: ID grounded -> disturbance;
- diagnostic: only first serial position R becomes active;
- scanner: first sample follows immediately after output-low -> input transition.

This does **not** require ID to be a hard direct connection to DATA. A resistive/transistor/protection or detect coupling is sufficient.

### H2 — D-/D+ carry DATA/CLOCK, ID affects reset/load/detect
**Plausibility: strong.**

The main controller transport could still use D-/D+ while ID participates in controller presence, reset, load, or electrical gating. This fits the family tendency to reuse USB-shaped data contacts while also explaining why the OTG-specific ID state matters.

### H3 — ID is CLOCK or directly perturbs CLOCK
**Plausibility: moderate.**

A clock/start-of-frame disturbance can produce an incorrect first sample, but a simple hard-low clock model would normally be expected to disrupt the whole transaction rather than cleanly generate R-only. More complex coupling remains possible.

### H4 — ID selects/pinmuxes an external-controller mode below the application scanner
**Plausibility: possible but weaker.**

No convincing application-level XGO path has been found that checks USB/OTG attach before running the B15/L0/B7 scanner; scanner initialization and polling are unconditional. A lower-level HC15xx pinmux/USB block response to ID remains possible, but the clean bit-0 artifact is now easier to explain as direct electrical/timing coupling.

### Discarded simple model — ID hard-grounded DATA
**Plausibility: poor / contradicted.**

A permanently grounded active-low DATA stream predicts all twelve sampled positions asserted. The hidden diagnostic instead reports R-only. Do not use the all-buttons prediction as the active model unless new contradictory physical evidence appears.

## Strongest next measurements

The R-only result already gives us a temporal fingerprint. The best next measurements are therefore electrical rather than repeating the diagnostic:

1. measure idle DC voltage on micro-USB pins 1-4 relative to GND with no cable;
2. repeat with a normal micro-USB plug inserted but otherwise disconnected;
3. repeat with the empty OTG adapter inserted;
4. look specifically for a contact whose voltage changes only under OTG/ID-ground condition;
5. with a logic analyzer, trigger on the B7-like polling burst and inspect whether one connector contact stays low only through the first sample window;
6. compare the first DATA release edge against subsequent clock edges.

A waveform showing DATA low through sample 0 and high before sample 1 would almost directly explain the observed R-only state.

## What would constitute pinout confirmation

A connector pin can be assigned to an XGO GPIO only after at least one of:

- direct PCB continuity from connector contact to SoC/test-point net;
- logic-analyzer waveform matching reconstructed B7 clock timing;
- data waveform matching the 12-bit active-low scanner and known button presses;
- controlled pull test producing a deterministic known bit position in diagnostic mode.

## Research consequence

The firmware/protocol question is substantially solved. The OTG behavior should no longer be treated as a generic freeze or an all-buttons event. It is a **bit-0/R-specific timing clue**.

Highest-value work is now:

- recover exact X60-to-SF2000 adapter wiring;
- recover/analyze X60 or DY19 firmware when available;
- map XGO micro-USB contacts electrically;
- compare connector waveforms to the known B15/L0/B7 scanner;
- only then build an adapter or controller emulator.

## Sources
- `axgdev/UniFrog`, `foundation/src/platform/sf2000/input/unifrog_input.c`
- `axgdev/frogqemu`, `docs/SF2000.md`
- `axgdev/frogqemu`, `docs/DEVICE_FAMILY.md`
- 4PDA SF2000 posts #394/#398/#404: X60 platform, ~3 V connector observation, X60 controller -> SF2000 P2 test
- 4PDA SF2000 post #2468: Hamy Max and X60/DY12 wired-controller compatibility
- XGO firmware scanner reconstruction and physical OTG/controller-diagnostic experiment documented in this repository
