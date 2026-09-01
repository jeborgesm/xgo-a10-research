# Controller connector electrical model narrowing

## Status
Comparison of XGO firmware/physical behavior against SF2000, X60 and DY12 evidence after confirming XGO/SF2000 serial keypad protocol equivalence.

## Headline
The remaining Handle Interface problem is now primarily **physical routing**, not protocol identification.

XGO firmware implements the same 12-position active-low serial button contract as SF2000, but exposes two parallel data streams (B15 and L0) on shared clock B7. External evidence independently shows that X60/DY12 wired controllers interoperate with SF2000 as Player 2 through a connector adapter, and X60 uses micro-USB specifically as an external-controller connector.

The strongest current model is therefore that the XGO micro-USB Handle Interface exposes some subset of the XGO GPIO scanner signals directly. The exact micro-USB contact mapping remains unconfirmed.

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
- empty OTG adapter freezes controls
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

## Pinout hypotheses ranked

### H1 — D-/D+ carry DATA/CLOCK, ID is detect or coupled control
**Plausibility: moderate.**

This is the most obvious OEM reuse because standard USB cables expose D-/D+, and SF2000 descriptions specifically refer to USB-shaped "data contacts" being polled as controller signals.

Problem: on XGO, a bare OTG adapter differs from a normal cable primarily by grounding micro-USB ID. If ID were electrically irrelevant, the observed immediate control freeze is difficult to explain.

### H2 — ID is directly one of the serial-bus signals
**Plausibility: strong for XGO specifically.**

Grounding ID with an OTG plug would then clamp DATA or CLOCK.

If ID is the external active-low DATA line, every sample would read low and therefore decode all 12 buttons as pressed on that stream. This provides a direct mechanism for the observed apparent UI freeze.

If ID is CLOCK, grounding it would instead hold the shared or external clock low and disrupt scanning. Which behavior better matches the firmware depends on whether B7 is physically exposed and whether the external accessory drives or only receives that clock.

### H3 — ID selects/pinmuxes an external-controller mode below the application scanner
**Plausibility: possible but currently weaker.**

No convincing application-level XGO path has been found that checks USB/OTG attach before running the B15/L0/B7 scanner; scanner initialization and polling are unconditional. A lower-level HC15xx pinmux/USB block response to ID remains possible, but direct electrical interference currently requires fewer assumptions.

## Strongest testable prediction

If XGO micro-USB ID is the external DATA stream and OTG grounds it, the hidden `Resources/Test.zsf` diagnostic should show the affected player as **all/most buttons continuously asserted** while the OTG adapter is inserted.

That result would be much more specific than simply observing a frozen menu and would strongly identify ID as DATA or a signal immediately coupled to DATA.

If instead the diagnostic stops updating both streams or built-in P1 disappears without an all-buttons P2 state, CLOCK/pinmux interference becomes more likely.

## Safe physical mapping sequence

No power injection is required.

1. Run hidden controller diagnostic (`L + SELECT`).
2. Insert empty OTG adapter and observe P1/P2 bit state.
3. With XGO powered off, continuity-test micro-USB shell/pin 5 to board ground.
4. Identify which connector contacts show continuity toward the controller-side circuitry/test pads if accessible.
5. Powered measurement only with high-impedance meter/logic analyzer: record idle voltage on pins 1-4 relative to GND.
6. Look for B7-style periodic clock activity and active-low data activity during button polling.
7. Do not connect 5 V or a conventional USB host/device until the proprietary mapping is known.

## What would constitute pinout confirmation

A connector pin can be assigned to an XGO GPIO only after at least one of:

- direct PCB continuity from connector contact to SoC/test-point net;
- logic-analyzer waveform matching reconstructed B7 clock timing;
- data waveform matching the 12-bit active-low scanner and known button presses;
- controlled grounding/pull test in diagnostic mode producing the predicted bitstream behavior.

## Research consequence

The firmware/protocol question is substantially solved. Highest-value work is now:

- recover/analyze the user's X60 card backup when available;
- locate X60 controller scanner and compare its GPIO topology to XGO;
- recover exact X60-to-SF2000 adapter wiring;
- map XGO micro-USB contacts experimentally using the hidden diagnostic;
- only then build an adapter or controller emulator.

## Sources
- `axgdev/UniFrog`, `foundation/src/platform/sf2000/input/unifrog_input.c`
- `axgdev/frogqemu`, `docs/SF2000.md`
- `axgdev/frogqemu`, `docs/DEVICE_FAMILY.md`
- 4PDA SF2000 posts #394/#398/#404: X60 platform, ~3 V connector observation, X60 controller -> SF2000 P2 test
- 4PDA SF2000 post #2468: Hamy Max and X60/DY12 wired-controller compatibility
- XGO firmware scanner reconstruction and physical OTG-vs-normal-cable experiment documented in this repository
