# External Controller / Player 2 Research

This remains the highest-priority hardware investigation, but the problem has now split into **three** identifiable input paths: built-in/wired serial controller scanning, stock SF2000-family RF P1/P2 support, and still-unresolved H1512 USB capability.

## Physical interface

Product-family documentation for closely matching XGO A10 hardware labels the small connector as **Handle Interface** — common translated terminology for a game controller. This is independent evidence that the port is intended for an external controller.

The exact connector pinout still needs to be established. Physical appearance alone must not be taken to mean standards-compliant USB HID.

## Physical experiment: GP2040-CE

A GP2040-CE controller was connected to the XGO's small controller port.

Observed:

- the controller received 5 V power;
- no usable Player 2 input was obtained;
- while connected, the XGO's own controls became unresponsive/froze;
- unplugging the controller restored normal behavior.

A separate PC-side experiment also produced USB detection followed by `USB\DEVICE_DESCRIPTOR_FAILURE`.

Originally this looked like possible narrow/failed USB-host behavior. New disassembly gives us a stronger alternative explanation: the XGO has a **two-channel synchronous serial gamepad scan path** at the GPIO level, and one of those channels is a strong candidate for the Handle Interface.

## Newly confirmed: two serial controller channels

The XGO input routine maintains two non-RF raw controller state words and scans them from two active-low GPIO data lines in parallel.

Observed GPIO structure:

```text
B15 data line 0
L0  data line 1
B7  shared scan clock
```

The firmware briefly drives both data lines low for a load phase, switches them back to input, samples both, pulses the shared clock, and repeats across the full 12-button gamepad bitmap.

Each data line independently builds:

```text
R, Y, X, L, A, B, SELECT, START, UP, DOWN, LEFT, RIGHT
```

using the same raw button bits as the SF2000 RF protocol.

Most importantly, these two serial states are kept separate as **controller slot 0 and controller slot 1**. At the decode stage the firmware ORs them slot-for-slot with the RF states:

```text
serial[0] OR RF[0] -> Player 1
serial[1] OR RF[1] -> Player 2
```

This is executable-code evidence, not inference from strings.

Because the XGO has only one built-in control set but has a dedicated external `Handle Interface`, the natural hardware hypothesis is now:

```text
serial scan channel 0 -> built-in controls / P1
serial scan channel 1 -> Handle Interface / P2
```

The B15/L0 assignment to built-in versus external is not yet known, and continuity to the connector has not been measured, so the physical mapping remains **strong evidence rather than confirmed**.

See `findings/input-path.md` for the disassembly details.

### Why the GP2040 result now makes more sense

A five-contact micro-USB connector does not have to carry USB D+/D-. It can physically carry power, ground, clock, controller data, and another control/ID line.

If the XGO expects a simple synchronous controller scan but a GP2040 actively drives what it believes are USB data lines, the scan bus can be corrupted. Since the two serial controller channels share timing/control resources, that provides a plausible explanation for why the XGO's built-in controls stop responding while the GP2040 is attached.

This is not yet proof of the connector pinout, but it currently fits the firmware and observed behavior better than the generic-HID hypothesis.

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

SF2000/H1512 platform research still matters: the HC15xx platform has **two host/peripheral-capable USB controllers**. In the DB-B210-V1.1 reference design, micro-USB is wired to USB0 while USB-A is wired to USB1.

That does not prove the XGO uses the same wiring, and a direct XGO-binary scan has not exposed a clear USB HID path or straightforward hard-coded USB0/USB1 controller bases.

Current ranking after the dual-serial discovery:

1. **proprietary synchronous serial controller interface over the micro-USB connector** — now strongest firmware-side hypothesis;
2. native USB host with a narrow vendor-specific controller protocol;
3. limited HID/OTG behavior that rejects or conflicts with the tested GP2040.

Physical continuity or passive logic analysis is required to choose among them.

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

Independent protocol documentation identifies these as XN297L-family link parameters: 5-byte addresses, two-byte payloads, two receive pipes, and four hop channels around 2404, 2429, 2449, and 2479 MHz.

The receive code treats status `0x40` as P1 and `0x42` as P2, matching independent SF2000 hardware observations.

## Physical RF hardware remains uncertain

The transparent case initially seemed to argue against RF hardware, but the clearest exposed rear PCB region appears dominated by wireless-charging/power-bank circuitry. The LCD hides much of the likely gaming board.

Therefore no RF antenna/chip is currently visible with confidence, but RF hardware elsewhere on the main gaming PCB also cannot be ruled out.

## Current input architecture model

```text
                 +--------------------------+
serial channel 0 |                          | RF pipe 0
---------------->+---- OR ----> Player 1 <--+<----------------
                 |                          |
                 |    XGO input layer       |
                 |                          |
serial channel 1 |                          | RF pipe 1
---------------->+---- OR ----> Player 2 <--+<----------------
                 +--------------------------+

likely: built-in controls        likely/possible: Handle Interface
        on one serial line                         on the other
```

This architecture explains why both wired/local and wireless paths can coexist without emulator changes: they converge before the internal button mapping.

## Test/diagnostic ROM

The XGO card includes `Resources/Test.zsf`, the SF2000 controller-test SNES ROM. Establishing a reproducible launch method would give us a useful P1/P2 diagnostic environment for the Handle Interface once its electrical behavior is known.

## Questions to answer

1. Which serial data line, B15 or L0, is the built-in controls?
2. Does the other data line physically reach the Handle Interface?
3. Which connector contact carries B7 or equivalent scan clock?
4. Is there a separate load/control contact, or is the data-line drive-low phase used for load as in related HC15xx designs?
5. Does any Handle-Interface contact route to native USB0 as well, or is the connector purely GPIO/proprietary?
6. Is the RF IC physically populated on the main gaming PCB?
7. Can `Test.zsf` reliably display P1/P2 state?

## Rule for future testing

Do not connect unknown pins or inject voltages based solely on SF2000 reference-board pinouts. The next useful experiment is **passive continuity/logic observation**, not another random USB controller.
