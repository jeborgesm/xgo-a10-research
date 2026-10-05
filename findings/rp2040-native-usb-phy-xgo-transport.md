# RP2040 native-USB-PHY XGO transport — investigation checkpoint

## Status

This note records a new transport direction discovered after the hardware-proven P0/P1/P2 GPIO responder work. It does **not** replace those proofs. P2 remains the known-good behavioral reference.

The target is a clean single-cable controller:

```text
buttons / joystick
    -> GP2040-CE normalized GamepadState
    -> XGO output driver
    -> RP2040 native USB PHY in direct/single-ended mode
    -> Pico onboard micro-USB connector
    -> ordinary cable
    -> XGO Handle Interface / Player 2
```

No claim is made yet that this path works on XGO hardware. The next stage is passive hardware proof.

## Existing XGO hardware evidence [HW]

The GPIO prototype already established the transport contract independently of USB assumptions:

- XGO RED was the successful common/reference connection to Pico GND.
- XGO YELLOW is hardware timing-correlated with the shared scanner CLOCK.
- XGO GREEN is hardware timing-correlated with the P2 DATA/load conductor.
- Idle P2 transaction: host drives DATA low for about 7-8 us, releases it, then begins the clock sequence about 1 us later.
- Each transaction contains exactly 12 clock pulses.
- Clock is approximately 250 kHz, about 2 us low / 2 us high.
- Poll cadence is approximately 16.03 ms (~62.4 Hz).
- P1 proved fixed serial position 0/R injection using LOW-sink/high-Z DATA behavior.
- P2 proved arbitrary 12-position serialization in Contra using the same LOW-sink/high-Z electrical strategy.

These are the reference signatures for any native-USB-PHY experiment.

## Direct Pico power observation [HW]

Earlier testing connected the XGO Handle Interface directly to the same Raspberry Pi Pico with an ordinary micro-USB cable, with no OTG adapter or converter. The XGO powered the Pico/GP2040-CE board.

This establishes that the Handle Interface can provide usable power through the ordinary Pico micro-USB power path. Exact voltage/current margin is not yet characterized, but the basic question of whether this particular Pico can be powered from that port is already hardware-proven.

The same direct connection did not behave as a working controller and disturbed/froze XGO operation under the tested GP2040-CE firmware. That behavior must not be interpreted as USB-HID compatibility.

## RP2040 native USB PHY capability [SRC]

Current Raspberry Pi Pico SDK RP2040 register definitions expose low-level USB PHY controls relevant to XGO:

- `USBPHY_DIRECT.RX_DP` and `RX_DM` report physical D+/D- input state.
- `TX_DP` and `TX_DM` select direct output state.
- `TX_DP_OE` and `TX_DM_OE` expose output enable.
- With `TX_DIFFMODE=0`, the SDK/register description specifies independent single-ended output enable: an individual line may be Hi-Z or driving.
- `USBPHY_DIRECT_OVERRIDE` contains override enables for these PHY controls.
- `SIE_CTRL` also exposes `DIRECT_EN`, `DIRECT_DP`, and `DIRECT_DM`.

Raspberry Pi's own RP2040 USB enumeration workaround uses direct PHY/override controls while transitioning USB signaling, demonstrating that firmware-level direct PHY manipulation is an intentional silicon capability rather than an invented register interpretation.

### Consequence [INF]

The native PHY appears to expose the primitives needed to reproduce the already-proven P2 electrical model:

```text
P2 GPIO proof                 native-PHY candidate

GP26 input CLOCK       ->     RX_DP or RX_DM
GP27 output latch LOW  ->     corresponding TX_DP/TX_DM = LOW
GP27 OE disabled       ->     corresponding TX_*_OE = 0 / Hi-Z
GP27 OE enabled        ->     corresponding TX_*_OE = 1 / drive LOW
```

This is a strong implementation lead, **not yet XGO hardware proof**.

## GP2040-CE integration [SRC/INF]

Current GP2040-CE separates normalized controller state from output protocol drivers. The normal device path initializes TinyUSB on the native USB peripheral and drivers consume the processed gamepad state. GP2040-CE also has a distinct PIO-USB host path on configurable GPIOs.

The clean integration model is therefore an XGO-specific output transport/driver that consumes GP2040's normalized state while taking exclusive ownership of the native USB PHY in XGO mode. Normal USB modes continue using TinyUSB. XGO mode must not have TinyUSB simultaneously controlling the same native PHY.

This is preferable to making GP26/GP27 permanent external transport pins if the native-PHY experiment passes.

## Connector-mapping contradiction [OPEN]

Do not promote the earlier numeric micro-B pin labels to fact.

The loose breakout colors and behavior are hardware-proven (YELLOW=CLOCK behavior, GREEN=P2 DATA behavior, RED=working reference), but the earlier claim that YELLOW corresponds to conventional micro-B ID/pin 4 conflicts with the ordinary-cable single-connector hypothesis. Standard passive USB cables do not normally transport micro-B ID as a peer data conductor.

Possible explanations remain:

1. earlier contact numbering/orientation was wrong even though color-to-behavior mapping was right;
2. the XGO physical connector routing is nonstandard;
3. the cable/accessory convention is nonstandard;
4. XGO family members use different physical routing despite protocol similarity.

The next experiment should identify signals by waveform fingerprint through the Pico's **actual onboard connector**, avoiding reliance on visual pin numbering.

## P3-USBPHY passive experiment [PROPOSED]

First native-PHY candidate must be input-only.

1. Flash a firmware that does not initialize TinyUSB device operation.
2. Keep DP/DM transmit output enables disabled.
3. Disable device pull-up behavior so the Pico does not advertise as an ordinary USB device.
4. Read `RX_DP` and `RX_DM` only.
5. Power the Pico directly from XGO through the ordinary micro-USB cable.
6. Capture enough time to cover several ~16 ms polls.
7. Search both lines for the P0 hardware signatures:
   - exactly 12 ~250 kHz clock pulses per transaction;
   - ~16.03 ms repetition;
   - complementary P2 DATA/load behavior including the ~7-8 us host-low interval.

### Promotion rule

No active native-PHY output is authorized until passive capture proves which native USB line carries CLOCK and which carries DATA (if either) and confirms that the observed levels/timing agree with the GPIO P0 baseline.

If passive proof succeeds, the next active experiment is deliberately minimal: reproduce P1 fixed-R only through the appropriate native PHY line using LOW/Hi-Z behavior. A repeating P2 jump in Contra would then prove the single-cable native-PHY architecture.

## Timing feasibility [INF]

Measured XGO clock half-period is roughly 2 us. At the Pico's usual 133 MHz clock this is about 266 CPU cycles per half-period. A tight deterministic loop, IRQ handler, or dedicated-core implementation therefore appears feasible, but timing must be measured. Unlike PIO, USB PHY direct registers do not themselves provide the already-proven PIO state machine.

## Safety / preservation

- P2 GPIO responder remains the behavioral golden reference.
- Do not cut Pico traces.
- Do not connect the previous loose GP26/GP27 harness simultaneously with the direct micro-USB experiment.
- Passive P3-USBPHY must not drive DP or DM.
- Do not assume conventional USB semantics merely because the connector and cable are USB-shaped.
- Do not merge this research branch until the new transport is hardware-proven and cumulative scope is reviewed.
