# RP2040 XGO live GPIO controller

Minimal "Neanderthal controller" layered directly on the hardware-proven native Pico Micro-B XGO Player-2 responder.

## Status

**GOLDEN HARDWARE PASS: all 12 XGO input slots confirmed using Street Fighter II.**

The native transport and complete human-input path are hardware-proven. All 12 exposed GPIO inputs were confirmed on the physical XGO using Street Fighter II.

CI build is reproducible. Candidate UF2:

- `xgo_live_controller.uf2`
- size: 18,944 bytes
- SHA-256: `313d9aefc078c09ffa363f6357b6a78f1c2582c5fce5333d88ec5a102a2ad503`

## Button wiring

Each button is a normally-open switch from the listed Pico GPIO to GND. Firmware enables the RP2040 internal pull-up, so released is HIGH and pressed is LOW.

| XGO slot | Button | Pico GPIO | HW status |
|---:|---|---:|---|
| 0 | R | GP2 | PASS |
| 1 | Y | GP3 | PASS |
| 2 | X | GP4 | PASS |
| 3 | L | GP5 | PASS |
| 4 | A | GP6 | PASS |
| 5 | B | GP7 | PASS |
| 6 | SELECT | GP8 | PASS |
| 7 | START | GP9 | PASS |
| 8 | UP | GP10 | PASS |
| 9 | DOWN | GP11 | PASS |
| 10 | LEFT | GP12 | PASS |
| 11 | RIGHT | GP13 | PASS |

```text
button ---- Pico GPIO
   |
  [NO]
   |
  GND
```

The XGO transport uses only the Pico's native Micro-B connector:
- DP = XGO DATA/load-like
- DM = XGO CLOCK-like
- DATA output is LOW-sink/high-Z only
- CLOCK is never driven
- no USB HID/TinyUSB

Do not connect GP26/GP27 to the XGO; those pins belong only to the earlier loose-wire proof.

## Cable: the Frankie discovery

The working cable topology was discovered accidentally.

The original handmade "Frankie V1" used stiff Ethernet conductors soldered to DIY Micro-B connectors. It worked, but the construction was mechanically poor and eventually broke at a connector pad. During reconstruction as Frankie 3, the decisive observation was that the working Pico-side connector had two physical contacts electrically common. Without that relationship the Pico still powered and executed its three-blink startup signature, but successful XGO frame heartbeat did not begin and buttons did not work. Restoring the bridge immediately restored the live controller.

That accident has since been reproduced deliberately with **Frankie V2 Jr**, so the result is no longer dependent on the original accidental cable.

### Frankie V2 Jr — reproducible physical wiring

V2 Jr uses one ordinary four-conductor Micro-B-to-USB-A cable half (USB-A end cut off) and a 5-pad Micro-B connector salvaged from Frankie V1.

**Record this by physical solder-pad orientation, not assumed USB pin names.** With the replacement connector at the top and the three top-connector pads appearing at the bottom, the user-recorded pad positions are:

```text
            connector
          [ Micro-B ]
             top

physical pad 1 ---- BLACK
physical pad 2 ---- WHITE ----+
physical pad 3 ---- GREEN     |
physical pad 4 ---- WHITE ----+
physical pad 5 ---- RED

       2 and 4 share WHITE
```

Hardware result: **PASS**. LEFT and RIGHT operate XGO Player 2 correctly.

The important proven fact is the physical construction above. Do not silently translate these pad-position labels into conventional USB pin numbers, D+/D-/ID names, or OTG semantics until connector orientation and numbering are independently verified. Earlier color/pin assumptions proved unreliable.

### What failed

A four-conductor "Frankie 2" wired without the special shared-contact relationship powered the Pico and produced the three startup blinks, but then had no successful-frame heartbeat and no live controls. Swapping/crossing the two signal conductors did not repair it.

Commercial Micro-B-to-Micro-B cables also did not reproduce the working behavior and in some cases disrupted XGO controls. Do not infer their internal pin-4 wiring without continuity measurement.

### Why the accident matters

Frankie V1's poor construction accidentally exposed a cable-side electrical condition that conventional USB assumptions had hidden. Frankie 3 isolated the unusual shared-contact condition; Frankie V2 Jr then reproduced it intentionally on a fresh cable. The discovery was accidental, but the result is now independently reproducible hardware evidence.

## LED signatures

- three quick blinks at startup = live-controller firmware booted
- continuing/toggling heartbeat = successful XGO frames
- three blinks followed by dark LED = firmware booted but responder is not completing XGO polling frames

## Golden-promotion check

Before freezing this exact build as the full live-controller golden reference, hardware-test all 12 GPIOs and confirm:
1. every button maps to exactly the expected XGO action;
2. P1 remains unaffected;
3. all-released produces no phantom input;
4. at least one direction+action combination works simultaneously;
5. the known-working Frankie V2 Jr/Frankie 3 cable produces continuous successful-frame heartbeat.

Do not modify serializer timing or native USB-PHY transport while completing this test.


## Final hardware validation — 2026-10-07

All 12 mapped GPIO inputs were confirmed on physical hardware using Street Fighter II. This closes the input-map hardware gate for the minimal live-controller golden reference.

During final testing, the connector donated by Frankie V1 developed an intermittent BLACK-to-GREEN short that shut the XGO down. The connector was reinforced with conformal coating and heat-shrink tubing. Treat this as a mechanical connector fault, not a serializer/transport fault.

Historical correction: one Frankie V1 connector was salvaged for Frankie V2 Jr. The other V1 connector became unusable after excessive soldering heat damaged one pad.
