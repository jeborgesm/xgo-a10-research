# RP2040 XGO Player-2 adapter — research checkpoint

## Goal

Implement the smallest useful controller path:

```text
direct arcade buttons / joystick
        -> RP2040 / GP2040-style normalized input state
        -> XGO 12-bit serial responder
        -> XGO Handle Interface
        -> native Player 2 path
```

USB host, Bluetooth and translation of commercial controllers are explicitly deferred.

## Evidence already closed

### XGO firmware [BIN]

- The input task contains two independent active-low synchronous serial streams.
- P1 serial data is GPIO B15.
- P2 serial data is GPIO L0.
- GPIO B7 is the shared scan clock.
- Both streams use the same 12-button raw bitmap.
- P2 survives as a separate state and reaches the native/libretro Player-2 path.
- The scanner is periodic and does not require a USB attach event.
- Host firmware performs the load/reset/sample sequence; the accessory is a responder.
- Stock scanner timing includes an approximately 2 us low delay.

### Protocol-family comparison [UP/INF]

- XGO's logical 12-bit scan contract matches the stock SF2000 keypad contract.
- Independent SF2000 owner reports show a wired X60 controller recognized as Player 2 through a passive Type-C/micro-USB adapter.
- Independent SF2000 community reports also identify X60/DY12 bundled wired controllers as compatible through an adapter, and Hamy Max as compatible after connector rewiring.
- These observations support a low-voltage GPIO-style synchronous controller bus, not generic USB HID.

### Connector narrowing [INF]

The exact XGO micro-B pinout is still OPEN.

Current strongest model:

- GND is ordinary ground.
- D+ and D- are the leading pair for P2 DATA and shared CLOCK because the known passive cross-connector adapter path necessarily carries these contacts and the family controller works through it.
- micro-B ID is more likely detect/load/gating/bias/coupling than the primary DATA/CLOCK pair.
- VBUS may provide controller power/reference, but its exact XGO voltage and role remain unproven.
- Do **not** assume standard USB signaling or connect an RP2040 directly until the electrical mapping is closed.

The empty OTG adapter freezing XGO controls is consistent with the ID-to-ground strap perturbing this repurposed controller interface.

## RP2040 architecture

The first firmware does not need GP2040 USB output. It only needs a normalized button state and an XGO responder.

Recommended split:

1. GP2040-style GPIO/input layer maintains the current logical buttons.
2. Translate those buttons to the XGO/SF2000 12-bit bitmap.
3. A tiny deterministic responder presents the correct active-low bit stream when the XGO polls.
4. RP2040 PIO is a strong implementation candidate once exact edge/bit timing is frozen.
5. Start with Player 2 only.

## Hardware-safety rule

Until connector voltage and pin mapping are established:

- no RP2040 output may be connected to an unknown Handle Interface contact;
- do not use an OTG adapter as the wiring model;
- do not inject 5 V or 3.3 V into the XGO connector;
- prefer a passive/family-evidence solution for identifying DATA/CLOCK before active driving.

For the eventual first prototype, the RP2040 should only need to drive the P2 DATA function; XGO CLOCK should be observed as an input. An open-drain/open-collector-style interface is preferred if compatible with the recovered electrical contract.

## Remaining blockers

1. Map XGO micro-B contacts to P2 DATA / CLOCK / GND / power-or-reference / ID-or-control.
2. Recover exact 12-bit button serialization order and idle/load semantics in implementation-ready form.
3. Confirm voltage/logic-high expectation from family hardware evidence or a trustworthy schematic/PCB source.
4. Then implement the minimal RP2040 responder and test in a known two-player game.

## Scope discipline

Do not expand v1 into USB-host/Bluetooth controller translation. Direct buttons + joystick -> RP2040 -> XGO P2 is sufficient to prove the interface.
