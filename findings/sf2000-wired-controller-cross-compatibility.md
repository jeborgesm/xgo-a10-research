# SF2000 wired controller cross-compatibility evidence

## Status
Strong comparative evidence relevant to the XGO Handle Interface.

## Summary
4PDA reverse-engineering discussions document that stock SF2000-family hardware supports a **non-USB wired controller protocol on USB-shaped connectors**. Community reverse engineer `bnister` reports that:

- ordinary USB wired gamepads cannot work because USB data is not implemented for this purpose;
- an **Hamy Max** wired controller works after replacing/rewiring its connector to the SF2000 connector;
- controllers supplied with **X60** or **DY12** also work through an adapter using their **micro-USB** connector.

Independent X60 retail specifications explicitly list **External Controller Interface: Micro USB**, while its charging interface is listed separately as **Mini USB**. This removes an important ambiguity: on at least this X60 variant, micro-USB is deliberately the controller connector rather than merely a charging/data port.

This is directly relevant to XGO because its external `Handle Interface` is physically micro-USB and its firmware contains a two-stream synchronous GPIO controller scanner rather than a conventional USB HID input path.

## External evidence

### SF2000 USB-shaped controller bus
The SF2000 4PDA technical summary states that the USB Type-C data contacts are repurposed to poll a wired gamepad using a simplified proprietary protocol. Standard USB wired controllers are not supported at hardware level.

The same summary warns that these actively polled lines can interact badly with higher-voltage charging schemes, reinforcing that they are electrically active GPIO-like signals rather than a dormant USB data pair.

### Hamy Max controller interoperability
On 2024-04-01, `bnister` answered which wired controller could be connected to SF2000:

- Hamy Max controller works after cutting off/replacing its connector and wiring it to Type-C;
- USB itself is not routed/implemented for controller use in the SF2000 `bisrv.asd`.

On 2024-09-30, `bnister` repeated that his Hamy Max controller had been rewired and worked successfully.

Hamy Max retail controllers use a 9-pin proprietary connector and expose D-pad, A/B/C/X/Y/Z, Start and Select. The physical 9-pin connector therefore does not imply a fundamentally different input protocol; at least one implementation can be electrically adapted to SF2000.

### X60 / DY12 micro-USB controllers
In the same 2024-04-01 answer, `bnister` states that included controllers from X60 or DY12 also work with SF2000 through a **micro-USB adapter**.

Independent X60 product metadata describes the device with:

- `EXTERNAL CONTROLLER INTERFACE: Micro USB`
- `CHARGING INTERFACE TYPE: Mini USB`

Product imagery also shows X60 sold with one or two wired controllers.

This is especially significant for XGO because XGO's Handle Interface is itself a micro-USB receptacle.

## Interpretation for XGO

### CONFIRMED EXTERNALLY
- SF2000-family wired controller input is not standard USB HID.
- USB-shaped connector contacts can carry a proprietary simplified controller protocol.
- Hamy Max wired controller can operate with SF2000 after connector rewiring.
- X60 and DY12 supplied controllers have been reported to operate with SF2000 through a micro-USB adapter.
- At least one documented X60 retail variant explicitly uses **micro-USB as its external-controller interface**, distinct from its Mini-USB charging connector.

### CONFIRMED ON XGO
- XGO uses a micro-USB physical connector labeled/documented as `Handle Interface`.
- Generic GP2040-CE USB controller does not work as P2.
- XGO firmware scans two active-low synchronous serial controller streams using B15/L0 data and B7 shared clock.
- Inserting a bare micro-USB OTG adapter freezes XGO built-in controls, while a normal micro-USB cable does not.

### STRONG INFERENCE
The XGO Handle Interface is likely part of the same broader OEM concept as SF2000/X60/DY12: a USB-shaped connector carrying a proprietary controller bus rather than USB HID.

The X60 lead is now substantially stronger than a generic form-factor resemblance: a sibling `frog`-family handheld is explicitly sold with **micro-USB designated as the external-controller interface**, and its supplied controller has been reported to work on SF2000 through an adapter.

This makes an X60 controller one of the best currently known candidate accessories for electrically probing XGO.

### NOT YET CONFIRMED
- XGO is electrically pin-compatible with X60 or DY12 controllers.
- XGO uses the same exact clock/data timing or bit order as SF2000 wired input.
- Which XGO micro-USB pin corresponds to B15, L0, or B7.
- Whether micro-USB ID is data, clock, detect, or another coupled signal.
- Whether Hamy Max, X60 and DY12 controllers share identical internal encoder circuitry.

## Research consequence
The highest-value accessory search should now prioritize:

1. X60 wired controller / supplied gamepad;
2. DY12 wired controller / supplied gamepad;
3. micro-USB adapter wiring used to connect X60/DY12 controllers to SF2000;
4. Hamy Max controller PCB/pinout;
5. SF2000 Type-C wired-controller pinout.

A recovered X60/DY12 controller or documented adapter wiring could potentially map the physical connector directly onto the protocol already reconstructed from XGO firmware.

## Sources
- 4PDA SF2000 discussion, post #2468 (`bnister`), 2024-04-01: `https://4pda.to/forum/index.php?showtopic=1067862&st=2460`
- 4PDA SF2000 discussion, post #2856 (`bnister`), 2024-09-30: `https://4pda.to/forum/index.php?showtopic=1067862&st=2840`
- 4PDA SF2000 technical summary: `https://4pda.to/forum/index.php?showtopic=1067862&st=3300`
- Hamy Max 4PDA discussion: `https://4pda.to/forum/index.php?showtopic=1108072`
- Hamy Max controller listing: `https://showgames.ru/gamepad-hamy-max`
- X60 product metadata identifying Micro USB as external controller interface: `https://uquid.com/shop/product/2023-new-version-handheld-game-player-8gb-rom-portable-retro-x60-video-game-console-player-built-in-4849-games-for-md-gba-cps1-color-2-iOVATEzlxKwtX`
