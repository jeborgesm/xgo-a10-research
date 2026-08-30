# External Controller / Player 2 Research

This remains the highest-priority hardware investigation, but the problem is now split into two distinct paths: a **confirmed stock SF2000-family RF controller path in firmware** and the still-unresolved wired **Handle Interface**.

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

Interpretation: **the test failed as a generic USB-controller test, but the port is not behaving like an inert power-only connector.** More protocol-level investigation is needed.

## USB evidence — corrected interpretation

The XGO `bisrv.asd` contains strings such as:

```text
usb device attach
usb device detach
[FS]USB lun_num = %d
/dev/rda1
/mnt/rda1
```

These now look much more like storage/filesystem USB handling than controller HID evidence. No convincing `hid`, `usbhid`, gamepad-descriptor, or similar class-driver string has yet been found.

Therefore the firmware currently provides **no direct evidence that the Handle Interface is generic USB HID**.

## Confirmed RF Player 1 / Player 2 path

Disassembly of the XGO firmware has now established a complete stock-SF2000-like wireless-controller path:

```text
H1512 GPIO bit-bang bus
        -> RF IC init/self-test
        -> stock SF2000 address/config tables
        -> channel set 04 / 1d / 31 / 4f
        -> status register 0x07
        -> two-byte payload from 0x61
        -> status bit 0x02 selects controller slot 0/1
        -> button decode
        -> P1/P2 input state
```

The XGO contains the exact radio tables currently used by UniFrog's reconstructed stock SF2000 path:

```text
0a 6d 67 9c 46
f6 37 5d
dc a8 f3 6b 74
b2 9d 59 4f e3
```

and the exact stock channel sequence:

```text
04 1d 31 4f
```

The receive code treats status `0x40` as controller slot 0 / P1 and status `0x42` as controller slot 1 / P2, matching independent SF2000 hardware observations.

This means the XGO firmware retained the **actual SF2000-family wireless-controller protocol implementation**, not merely emulator-side Player 2 options.

## Physical RF hardware remains uncertain

The transparent enclosure provides a partial PCB view. At the current photo resolution:

- no obvious antenna or populated radio IC is confidently identifiable;
- one small unpopulated QFN-like footprint is visible;
- XN297L exists in a 3 x 3 mm QFN20 package, making that footprint an interesting inspection target, but package similarity is not identification.

A very plausible architecture is therefore:

```text
Built-in controls -------------------+
                                     +--> input subsystem --> emulators
Stock SF2000 RF path (firmware) -----+    [physical radio may be omitted]
                                     |
Handle Interface --------------------+--> ???
```

It is entirely possible that XGO reused the SF2000 firmware platform, left its RF implementation intact, but omitted the RF section on this PCB revision and provided the wired Handle Interface instead.

## Compatibility prediction

If the radio hardware is populated and connected, the exact firmware tables/channels strongly predict compatibility with SF2000/SF900-class controllers using the same protocol.

If the RF hardware is absent, the confirmed driver is simply dormant inherited code and the Handle Interface becomes the practical Player 2 mechanism to reverse engineer.

## Test/diagnostic ROM

The XGO card includes `Resources/Test.zsf`. SF2000 documentation identifies this as a controller-test SNES ROM. A controller-test screen was reached experimentally once during earlier button/USB testing. Establishing a reproducible launch method would give us a useful Player 2 diagnostic environment.

## Questions to answer

1. Is the RF IC physically populated anywhere on the XGO PCB?
2. Is the visible unpopulated QFN-like footprint related to the omitted RF section or something unrelated?
3. What electrical signals are present on the Handle Interface?
4. Does the Handle Interface use USB signaling, serial/UART-like signaling, GPIO/shift-register signaling, or another proprietary protocol?
5. What causes generic GP2040 attachment to suppress local controls?
6. Which XGO routines consume Handle-Interface data?
7. Can `Test.zsf` reliably display P1/P2 state?

## Rule for future testing

Do not connect unknown pins or inject voltages based solely on SF2000 pinouts. Establish XGO electrical behavior first.
