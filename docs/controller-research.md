# External Controller / Player 2 Research

This is currently the highest-priority hardware investigation.

## Physical interface

Product-family documentation for closely matching XGO A10 hardware labels the small connector as **Handle Interface** — common translated terminology for a game controller. This is independent evidence that the port is intended for an external controller.

The exact connector/protocol still needs to be established. Physical appearance alone must not be taken to mean standards-compliant USB HID.

## Physical experiment: GP2040-CE

A GP2040-CE controller was connected to the XGO's small controller port.

Observed:

- the controller received 5 V power;
- no usable Player 2 input was obtained;
- while connected, the XGO's own controls became unresponsive/froze;
- unplugging the controller restored normal behavior.

Interpretation: **the test failed as a generic controller test, but the port is not behaving like an inert power-only connector.** More protocol-level investigation is needed.

## Firmware evidence

The XGO `bisrv.asd` contains explicit Player 2 configuration strings, including:

```text
fba-neogeo-controls-p2
Neo Geo P2 gamepad scheme; classic|newgen
fba-lr-controls-p2
L/R P2 gamepad scheme; normal|remap to R1/R2
fba-controls-p2
```

It also contains USB/device-management strings including:

```text
usb device attach
usb device detach
[FS]USB lun_num = %d
```

This proves that Player 2 concepts and USB handling code exist in the firmware image. It does **not** yet prove that the Handle Interface presents Player 2 as generic USB HID.

## SF2000 comparison

Stock SF2000-family hardware supports external controllers through a 2.4 GHz receiver path. Modern UniFrog source code exposes this implementation in detail and decodes distinct controller ports.

A useful model for XGO research is therefore:

```text
SF2000:
local controls + RF receiver -> input subsystem -> P1/P2 -> emulator

XGO:
local controls + Handle Interface -> ??? -> P1/P2 -> emulator
```

The `???` is the primary target.

## Test/diagnostic ROM

The XGO card includes `Resources/Test.zsf`. SF2000 documentation identifies this as a controller-test SNES ROM. A controller-test screen was reached experimentally once during earlier button/USB testing. Establishing a reproducible launch method would give us a useful Player 2 diagnostic environment.

## Questions to answer

1. What electrical signals are present on the Handle Interface?
2. Does XGO expect USB host/device operation, or a proprietary protocol over a USB-shaped connector?
3. Does the original XGO accessory controller identify with a specific VID/PID or packet protocol?
4. What causes generic GP2040 attachment to suppress local controls?
5. Which routines in XGO `bisrv.asd` consume external-controller data?
6. Did XGO replace the SF2000 RF input path or merely add another path?
7. Can `Test.zsf` reliably display P1/P2 state?

## Rule for future testing

Do not connect unknown pins or inject voltages based solely on SF2000 pinouts. Establish XGO electrical behavior first.
