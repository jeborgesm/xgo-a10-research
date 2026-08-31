# SF2000 wired controller cross-compatibility evidence

## Status
Strong comparative evidence relevant to the XGO Handle Interface.

## Summary
4PDA reverse-engineering discussions document that stock SF2000-family hardware supports a **non-USB wired controller protocol on USB-shaped connectors**. Community reverse engineer `bnister` reports that:

- ordinary USB wired gamepads cannot work because USB data is not implemented for this purpose;
- an **Hamy Max** wired controller works after replacing/rewiring its connector to the SF2000 connector;
- controllers supplied with **X60** or **DY12** also work through an adapter using their **micro-USB** connector.

Independent X60 retail specifications explicitly list **External Controller Interface: Micro USB**, while its charging interface is listed separately as **Mini USB**. This removes an important ambiguity: on at least this X60 variant, micro-USB is deliberately the controller connector rather than merely a charging/data port.

A particularly valuable 2023 X60 owner report goes further: the owner physically connected the supplied X60 wired controllers to SF2000 through an adapter and confirmed that they were detected as **Player 2**. The same owner measured unusual approximately **3 V** behavior on the controller-facing connectors of both devices and explicitly concluded that ordinary OTG/USB expectations do not apply.

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

More importantly, a 2023 X60 owner (`dc_ScAn`) reported the following physical test after owning both an X60 and an SF2000:

- the X60 was supplied with two wired controllers;
- the owner observed unusual approximately **3 V** on the controller-facing connectors of both X60 and SF2000, and stated that normal OTG assumptions therefore do not apply;
- the owner then connected the X60 wired controllers through an adapter to SF2000;
- the SF2000 recognized the wired X60 controller as **second player**;
- wireless SF2000 controller could remain Player 1 while X60 wired controller operated as Player 2.

This is stronger than a compatibility claim based on retail description: it is a direct cross-device accessory test performed by an owner of both devices.

## X60 platform-level comparator evidence

The same 4PDA exchange provides unusually specific hardware/firmware evidence for X60:

- `bnister`, who had an X60 and exposed its UART for development, described X60 and SF2000 as the **same platform** at the core level;
- X60 lacks the SF2000 XN297 wireless-controller transceiver;
- X60 uses a different display;
- the local buttons are scanned on a **different GPIO pin**;
- at least two X60 hardware/display revisions existed;
- an X60-specific `bisrv.asd` was sufficient to run an SF2000-style card/software stack on X60 with minimal board-specific changes.

The forum hosted:

- `X60_to_SF2000.zip` (4.45 MB), containing an X60-specific firmware/`bisrv.asd` adaptation;
- `X60_bios_res.zip` (18.11 MB), uploaded by an X60 owner with its `bios` and `Resources` directories.

This materially strengthens the relevance of X60 as a comparator for XGO. It shows that within the same broad firmware family, input GPIO selection is explicitly board-specific while the higher software stack remains highly compatible.

## Interpretation for XGO

### CONFIRMED EXTERNALLY
- SF2000-family wired controller input is not standard USB HID.
- USB-shaped connector contacts can carry a proprietary simplified controller protocol.
- Hamy Max wired controller can operate with SF2000 after connector rewiring.
- X60 and DY12 supplied controllers have been reported to operate with SF2000 through a micro-USB adapter.
- An X60 owner directly tested X60 wired controllers on SF2000 and confirmed they are recognized as **Player 2**.
- The same owner observed approximately **3 V** behavior on the relevant connectors, inconsistent with treating them as ordinary USB/OTG controller ports.
- At least one documented X60 retail variant explicitly uses **micro-USB as its external-controller interface**, distinct from its Mini-USB charging connector.
- X60 and SF2000 share the same core platform closely enough that replacing `bisrv.asd` handles board-specific display/input differences.
- X60 local buttons are scanned from a different GPIO than SF2000, demonstrating board-specific input routing in firmware.

### CONFIRMED ON XGO
- XGO uses a micro-USB physical connector labeled/documented as `Handle Interface`.
- Generic GP2040-CE USB controller does not work as P2.
- XGO firmware scans two active-low synchronous serial controller streams using B15/L0 data and B7 shared clock.
- Inserting a bare micro-USB OTG adapter freezes XGO built-in controls, while a normal micro-USB cable does not.

### STRONG INFERENCE
The XGO Handle Interface is likely part of the same broader OEM concept as SF2000/X60/DY12: a USB-shaped connector carrying a proprietary controller bus rather than USB HID.

The X60 lead is now substantially stronger than a generic form-factor resemblance: a sibling `frog`-family handheld is explicitly sold with **micro-USB designated as the external-controller interface**, and its supplied controller has been physically demonstrated to work on SF2000 as Player 2 through an adapter.

The roughly 3 V connector observation is especially interesting beside XGO's active-low GPIO scanner and the OTG-adapter freeze experiment. It makes a low-voltage GPIO-style controller bus a much better fit than ordinary USB signaling.

This makes an X60 controller one of the best currently known candidate accessories for electrically probing XGO.

### NOT YET CONFIRMED
- XGO is electrically pin-compatible with X60 or DY12 controllers.
- XGO uses the same exact clock/data timing or bit order as SF2000/X60 wired input.
- Which XGO micro-USB pin corresponds to B15, L0, or B7.
- Whether micro-USB ID is data, clock, detect, or another coupled signal.
- The exact X60-to-SF2000 adapter wiring.
- Whether Hamy Max, X60 and DY12 controllers share identical internal encoder circuitry.

## Research consequence
The highest-value accessory/firmware search should now prioritize:

1. recovering `X60_to_SF2000.zip` and `X60_bios_res.zip` from 4PDA or mirrors;
2. disassembling the X60 `bisrv.asd` and locating its wired-controller scanner;
3. comparing X60 scanner GPIO/timing against XGO B15/L0/B7;
4. recovering the exact micro-USB-to-Type-C adapter wiring used by X60 owners;
5. X60/DY12 controller PCB/pinout;
6. Hamy Max controller PCB/pinout.

A recovered X60 `bisrv.asd` may let us answer the protocol question without owning the controller at all. If its scanner is homologous to XGO's, the diff should reveal which board-specific GPIOs route to the external connector and may provide the missing bridge from firmware to physical pinout.

## Sources
- 4PDA SF2000 discussion, X60 hardware/platform and firmware adaptation, posts around #398: `https://4pda.to/forum/index.php?showtopic=1067862&st=380`
- 4PDA SF2000 discussion, X60 card files and direct controller-on-SF2000 test, post #404: `https://4pda.to/forum/index.php?showtopic=1067862&st=400`
- 4PDA SF2000 discussion, post #2468 (`bnister`), 2024-04-01: `https://4pda.to/forum/index.php?showtopic=1067862&st=2460`
- 4PDA SF2000 discussion, post #2856 (`bnister`), 2024-09-30: `https://4pda.to/forum/index.php?showtopic=1067862&st=2840`
- 4PDA SF2000 technical summary: `https://4pda.to/forum/index.php?showtopic=1067862&st=3300`
- Hamy Max 4PDA discussion: `https://4pda.to/forum/index.php?showtopic=1108072`
- Hamy Max controller listing: `https://showgames.ru/gamepad-hamy-max`
- X60 product metadata identifying Micro USB as external controller interface: `https://uquid.com/shop/product/2023-new-version-handheld-game-player-8gb-rom-portable-retro-x60-video-game-console-player-built-in-4849-games-for-md-gba-cps1-color-2-iOVATEzlxKwtX`
