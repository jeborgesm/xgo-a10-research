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

A separate PC-side experiment also produced USB detection followed by `USB\DEVICE_DESCRIPTOR_FAILURE`. This shows some USB-like electrical behavior occurred, but descriptor failure is not sufficient to prove a standards-compliant USB device implementation.

## USB evidence — current interpretation

The XGO `bisrv.asd` contains strings such as:

```text
usb device attach
usb device detach
[FS]USB lun_num = %d
/dev/rda1
/mnt/rda1
```

These look primarily like storage/filesystem USB handling. No convincing `hid`, `usbhid`, controller-descriptor, or similar class-driver string has yet been found.

However, SF2000/H1512 platform research adds an important architectural clue: the HC15xx platform has **two host/peripheral-capable USB controllers**. In the DB-B210-V1.1 reference design, micro-USB is wired to USB0 while USB-A is wired to USB1.

That does **not** prove the XGO uses the same wiring, but it means the XGO Handle Interface can plausibly be a genuine native USB port even though generic HID support has not been found.

Current wired-interface possibilities, in descending order of interest rather than confidence:

1. native USB host with a narrow vendor-specific controller/descriptor expectation;
2. native USB host with limited HID support that rejects the tested GP2040 presentation;
3. USB peripheral/OTG role switching or ID/VBUS interaction that conflicts with the local input path;
4. non-USB serial/GPIO-style protocol over a micro-USB connector.

A direct scan of the XGO application image has not yet exposed obvious hard-coded USB0/USB1 controller base addresses or a clear HID class implementation. That negative result is useful but not decisive because USB controller addresses may be supplied indirectly through platform configuration/driver tables.

## Confirmed RF Player 1 / Player 2 path

Disassembly of the XGO firmware has established a complete stock-SF2000 wireless-controller path:

```text
H1512 GPIO bit-bang bus
        -> RF IC init/self-test
        -> XN297L-style calibration/address setup
        -> channels 04 / 1d / 31 / 4f
        -> status register 0x07
        -> two-byte payload from 0x61
        -> status bit 0x02 selects controller slot 0/1
        -> button decode
        -> P1/P2 input state
```

The XGO contains the exact radio tables used by current SF2000/SF900 protocol research:

```text
BB_CAL:     0a 6d 67 9c 46
RF_CAL:     f6 37 5d
RX_ADDR_P0: dc a8 f3 6b 74
RX_ADDR_P1: b2 9d 59 4f e3
channels:   04 1d 31 4f
```

Modern independent documentation identifies these as XN297L-family link parameters: 5-byte addresses, two-byte payloads, two receive pipes, and four hop channels corresponding to approximately 2404, 2429, 2449, and 2479 MHz.

The receive code treats status `0x40` as controller slot 0 / P1 and status `0x42` as controller slot 1 / P2, matching independent SF2000 hardware observations.

This means the XGO firmware retained the **actual SF2000/SF900 wireless-controller protocol implementation**, not merely emulator-side Player 2 options.

## Physical RF hardware remains uncertain

The transparent case initially seemed to argue against RF hardware, but the photographs need a more careful interpretation.

The clearest exposed rear PCB region sits directly beneath the wireless-charging coil and contains a large `2R2` inductor and power components. It appears to be primarily the **power-bank / charging board**, not necessarily the main gaming PCB. The LCD obscures a large portion of the likely gaming board on the front side.

Therefore:

- no RF antenna/chip is currently visible with confidence;
- the earlier unpopulated QFN-like footprint on the rear board is no longer a strong RF candidate;
- RF hardware could still exist on the main board beneath/around the LCD;
- RF omission remains plausible, but the transparent case alone does not settle it.

## Compatibility prediction

If the radio hardware is populated and connected, the firmware configuration now strongly predicts compatibility with SF2000/SF900-class controllers using the documented XN297L protocol.

If the RF hardware is absent, the confirmed RF implementation is dormant inherited code and the Handle Interface becomes the practical Player 2 mechanism to reverse engineer.

## Test/diagnostic ROM

The XGO card includes `Resources/Test.zsf`. SF2000 documentation identifies this as a controller-test SNES ROM. A controller-test screen was reached experimentally once during earlier button/USB testing. Establishing a reproducible launch method would give us a useful Player 2 diagnostic environment.

## Questions to answer

1. Is the RF IC physically populated on the main gaming PCB under/around the LCD?
2. Does the Handle Interface route to H1512 USB0, or to another controller/interface block?
3. What electrical signals appear on D+/D-/ID when no accessory is present and when a controller is attached?
4. Does the expected accessory enumerate with a narrow VID/PID/report format or use a vendor-specific transfer protocol?
5. What causes GP2040 attachment to suppress the local controls?
6. Which XGO routines consume Handle-Interface data?
7. Can `Test.zsf` reliably display P1/P2 state?

## Rule for future testing

Do not connect unknown pins or inject voltages based solely on SF2000 reference-board pinouts. Establish XGO electrical behavior first.
