# External Controller / Player 2 Research

This remains the highest-priority hardware investigation, but the problem has now split into **three** identifiable input paths: built-in/wired serial controller scanning, stock SF2000-family RF P1/P2 support, and still-unresolved H1512 USB capability.

## Physical interface

Product-family documentation for closely matching XGO A10 hardware labels the small connector as **Handle Interface** — common translated terminology for a game controller. This is independent evidence that the port is intended for an external controller.

The exact connector pinout still needs to be established. Physical appearance alone must not be taken to mean standards-compliant USB HID.

## Physical experiment matrix

The adapter/controller tests now separate two behaviors that were originally conflated.

```text
normal micro-USB cable / non-OTG path
    -> built-in controls remain normal

non-OTG + generic USB SNES controller
    -> controller not recognized
    -> built-in controls remain normal

non-OTG + inexpensive PS-shaped USB controller
    -> controller not recognized
    -> built-in controls remain normal

non-OTG + GP2040-CE
    -> controller not recognized
    -> built-in controls remain normal

bare OTG adapter, nothing attached to USB-A side
    -> built-in controls freeze immediately
```

The original GP2040 experiment had used an OTG path and therefore initially suggested that an active USB controller could corrupt the XGO input subsystem. The new matrix shows that the GP2040 itself is not required: the empty OTG adapter is sufficient, while three active USB controllers through a non-OTG path are simply ignored.

This is strong evidence against generic USB-HID controller support on the tested Handle Interface path and strongly favors an electrical difference introduced by OTG wiring.

Unpowered probing of the OTG adapter with fine needle extensions produced a ground-related resistance reading on micro-USB pin 4, consistent with the normal OTG convention in which the ID pin is tied to ground. Because the physical setup was awkward, this is qualitative rather than precision measurement evidence.

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

See `findings/input-path.md` and `findings/handle-interface-protocol.md` for the disassembly and protocol details.

## Why pin 4 is now especially interesting

A conventional non-OTG USB cable or adapter leaves the micro-USB ID contact open. A conventional OTG adapter grounds it. The XGO's opposite behavior under those two conditions is now the cleanest physical discriminator we have.

The leading model is:

```text
ID open
    -> proprietary controller bus remains electrically idle
    -> built-in controls work

ID grounded
    -> an XGO-repurposed or electrically coupled signal is forced low/asserted
    -> controller subsystem appears frozen
```

Static application-firmware analysis found no software-side `P2 connected` gate, USB-attach gate, or controller-mode switch controlling whether the dual serial scan runs. Both local channels are scanned continuously.

That makes direct electrical interference with the existing serial controller bus more plausible than an application-level "enter controller mode" event.

One particularly strong hypothesis is that micro-USB pin 4 is, or is coupled to, the external/P2 active-low DATA signal. If so, grounding it would make the scanner observe a continuously asserted stream. This remains a hypothesis until connector routing or diagnostic input behavior confirms it.

## USB evidence — current interpretation

The XGO `bisrv.asd` contains strings such as:

```text
usb device attach
usb device detach
[FS]USB lun_num = %d
/dev/rda1
/mnt/rda1
```

These look primarily like storage/filesystem USB handling. No convincing `hid`, `usbhid`, controller-descriptor, or similar class-driver string has been found in the reconstructed controller path.

HC15xx hardware has native USB capability, so some USB functionality on the product cannot be ruled out. However, the tested Handle Interface does not recognize three different generic USB controller implementations through a non-OTG path.

Current ranking:

1. **proprietary synchronous serial controller interface over the micro-USB shell** — strongest model;
2. hybrid/multiplexed serial plus some lower-level USB/ID behavior;
3. narrow vendor-specific USB controller mode;
4. generic USB HID — now weakest.

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

The receive code treats status `0x40` as P1 and `0x42` as P2, matching independent SF2000-family observations.

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

## Test/diagnostic ROM

The XGO card includes `Resources/Test.zsf`, the SF2000 controller-test SNES ROM. Establishing a reproducible launch method would give us a useful P1/P2 diagnostic environment.

The highest-value behavioral discriminator is now to launch that test and insert the bare OTG adapter. If P2 suddenly presents many/all buttons as active while P1 remains otherwise alive, that would strongly favor the stuck-low P2 DATA model. If the entire scan stops updating, a lower-level mode/pinmux interaction becomes more plausible.

## Questions to answer

1. Which serial data line, B15 or L0, is the built-in controls?
2. Does the other data line physically reach the Handle Interface?
3. Which connector contact carries B7 or equivalent scan clock?
4. Is micro-USB pin 4 directly connected or coupled to the P2 serial data line?
5. What voltage and idle bias are present on each Handle Interface contact?
6. Is the RF IC physically populated on the main gaming PCB?
7. Can `Test.zsf` reliably display P1/P2 state during the OTG freeze?

## Rule for future testing

Do not connect unknown pins or inject voltages based solely on conventional USB or SF2000 reference-board pinouts. Generic USB-controller testing has now provided diminishing returns. The next useful work is passive signal mapping or diagnostic observation of the P2 state.
