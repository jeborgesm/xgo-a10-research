# Handle Interface Serial Protocol — Current Reconstruction

Status: **firmware protocol timing confirmed; physical connector routing not yet confirmed**.

## Why this exists

The XGO controller task contains a two-channel synchronous serial scanner that continuously produces Player 1 and Player 2 local/wired controller states. One stream is a strong candidate for the external `Handle Interface`.

This note records the electrical behavior visible directly in the XGO MIPS code so future testing can compare a logic-analyzer trace or candidate controller against the firmware rather than guessing from the micro-USB connector shape.

## GPIO roles observed in the XGO scanner

```text
B15  data channel 0   input register 0xb8800350 bit 15
L0   data channel 1   input register 0xb8800050 bit 0
B7   shared clock     output register 0xb8800354 bit 7
```

Direction/control registers used during the load phase:

```text
B bank direction/control: 0xb8800358
L bank direction/control: 0xb8800058
```

The two data streams are active-low: a low sample means the corresponding button bit is asserted.

## GPIO initialization

The controller/RF initialization routine at approximately `0x8035deb0` configures the same GPIO block used later by the serial scanner before running the RF self-test.

The relevant effects are consistent with the scan routine:

```text
B15 -> input at idle
L0  -> input at idle
B7  -> output
B7  -> driven high at idle
```

The initialization then continues into the RF GPIO setup and radio self-test. This shows the local serial bus and wireless input path are intentionally initialized together as parts of the controller subsystem.

## Load/reset phase

The firmware clears both software controller states, then performs this sequence:

```text
1. configure B15 as output
2. configure L0  as output
3. drive B15 low
4. drive L0  low
5. wait approximately 4 us
6. return B15 to input
7. return L0  to input
8. sample the first button bit
```

There is no separate dedicated latch signal visible in this routine. The host deliberately takes temporary ownership of the data lines and pulls them low. Any directly attached controller must therefore tolerate this behavior.

This is an important difference from treating the connector as a literal raw SNES-controller port.

## Bit clocking

After each pair of B15/L0 samples, the firmware pulses B7:

```text
clock high / idle
sample data
clock low
wait approximately 2 us
clock high
sample next data bit
```

The explicit delay is on the low phase. The high-phase duration is produced by normal instruction/interrupt-guard overhead before the next sample rather than by a matching explicit delay call.

The code performs the clock operation after the final sample as well.

## Twelve-bit order

Exactly twelve controller positions are accumulated per stream:

```text
sample 0   R       raw 0x1000
sample 1   Y       raw 0x2000
sample 2   X       raw 0x4000
sample 3   L       raw 0x0800
sample 4   A       raw 0x0080
sample 5   B       raw 0x0040
sample 6   SELECT  raw 0x0020
sample 7   START   raw 0x0010
sample 8   UP      raw 0x0008
sample 9   DOWN    raw 0x0004
sample 10  LEFT    raw 0x0002
sample 11  RIGHT   raw 0x0001
```

Both channels are sampled in parallel on every clock.

## Relationship to related HC15xx input buses

The protocol shape strongly resembles the local-controller scan currently reconstructed for GB300-family HC15xx hardware:

- multiple active-low serial data lines;
- host temporarily drives data low for the load phase;
- host switches the same lines back to input;
- a shared GPIO clock advances the stream;
- microsecond-scale load and clock delays.

Current UniFrog code uses this same unusual drive-low / return-to-input strategy for GB300 local controls. The XGO differs in GPIO assignment, exact timing, bit count, and — importantly — preserves the two streams as separate Player 1 and Player 2 states.

The XGO implementation therefore looks more like a relative of the HC15xx local-controller bus than a standard USB HID path or a literal SNES electrical interface.

## Polling behavior

The scanner is part of the persistent controller task and runs periodically without waiting for USB attachment or enumeration. A poll counter selects the scan phase approximately every fourth task phase.

This means the GPIO bus remains active even with no external controller attached.

## No software-side P2 connection gate found

A full disassembly search for direct accesses to the two local serial state words found the following pattern:

```text
gp - 0x0d2c   serial/local slot 0
gp - 0x0d28   serial/local slot 1
```

Direct accesses to those two words occur inside the serial scan routine itself: the function clears the words and sets button bits as B15/L0 are sampled. Outside that scanner, the states are consumed through the two-element array pointer and merged with RF P1/P2.

No separate flag was found that says "P2 connected", no branch skips the second serial channel when the connector is empty, and no USB-attach condition gates the scan. The firmware simply samples both data lines every scan cycle.

This strongly suggests that an absent second controller is represented electrically by an inactive/all-high serial stream rather than by a separate enumeration or connection event.

## Idle-line implication

Because an empty Player-2 channel is scanned continuously, its data input cannot be allowed to float randomly in normal operation. Something must hold the external-channel input at the inactive/high level when no controller is present.

The firmware scanner itself does not perform a per-scan pull-up configuration; it only changes direction and output latch state. Therefore the stable idle level is likely supplied by one of the following:

- a board-level pull-up resistor;
- a pin pull configured once elsewhere in pinmux/pad setup;
- intermediary accessory-interface logic.

## Cable/adapter differential experiment — very strong physical evidence

Two physically similar micro-USB attachments now produce opposite results:

```text
normal micro-USB male -> USB-A male cable
    inserted into Handle Interface
    -> built-in controls continue working normally

micro-USB OTG adapter -> USB-A female
    inserted empty, nothing connected to USB-A side
    -> built-in controls freeze immediately
```

This differential result is substantially more informative than the original GP2040 experiment.

A normal micro-USB cable typically leaves the micro-USB **ID** contact unconnected, while an OTG host adapter commonly grounds the ID contact to request host mode. Because the ordinary cable does not disturb the XGO but the OTG adapter does, the ID-contact difference is now the leading explanation for the freeze.

This does **not** yet prove that XGO micro-USB pin 4 is P2 DATA. It does, however, sharply reduce the likelihood that ordinary VBUS/D+/D-/GND contact presence alone causes the fault, because those conventional USB contacts are present on both cable types.

### Current leading electrical interpretation

The strongest working model is now:

```text
ordinary cable:
    ID open
    -> proprietary controller bus remains in normal idle state

OTG adapter:
    ID grounded
    -> an XGO-repurposed signal is forced/asserted
    -> controller subsystem becomes unusable / appears frozen
```

If that repurposed signal is the active-low external/P2 DATA line, grounding it would make all twelve P2 samples read as pressed. If instead it is a mode/control signal, grounding it could alter pinmux or controller behavior. The observed differential cannot distinguish these two mechanisms by itself.

### What is now strongly disfavored

- GP2040-specific incompatibility as the cause of the freeze;
- generic USB-HID enumeration failure as the primary trigger;
- simple mechanical insertion or VBUS presence as the sole cause;
- the idea that any micro-USB attachment disrupts the port.

## What a compatible external controller would need to do

If the Handle Interface is physically wired to this scanner, a compatible controller must at minimum:

1. be safe when its data line is pulled low by the host for roughly 4 us;
2. release/drive an active-low serial data stream after the load phase;
3. present the first bit before the first clock pulse;
4. advance to the next bit on the host clock transition;
5. provide at least the 12 expected positions in the XGO order;
6. operate at whatever voltage is present on the actual connector, still to be measured.

## Current confidence

### CONFIRMED from firmware

- two parallel active-low data streams;
- one shared clock;
- B15/L0 idle as inputs and B7 is initialized as the clock output;
- host-driven data-low load/reset phase;
- approximately 4 us explicit load delay;
- approximately 2 us explicit clock-low delay;
- twelve samples per stream in a known button order;
- periodic operation independent of USB attachment state;
- both serial slots are scanned unconditionally;
- no separate software-side P2 connection gate was found in the local-state path;
- channel states merge directly into P1/P2 alongside RF input.

### CONFIRMED physically

- inserting the bare micro-USB OTG adapter, with no USB peripheral attached, immediately causes the XGO controls to freeze;
- inserting a normal micro-USB male to USB-A male cable does **not** disturb the controls;
- therefore the GP2040 is not required to trigger the failure;
- not every micro-USB attachment triggers the failure.

### STRONG EVIDENCE

- this is a hardware controller bus rather than an abstract emulator-only data structure;
- one stream is likely the built-in controls and the other the external Handle Interface;
- the protocol belongs to the same general HC15xx controller-bus family as related SF2000/GB300 hardware;
- an absent external controller is likely represented by an idle/high data stream rather than USB-style enumeration;
- the empty external channel must have some stable-high bias mechanism rather than being left electrically floating;
- the OTG adapter is altering at least one electrically meaningful Handle-Interface contact even with its USB-A side empty;
- the distinguishing micro-USB ID behavior of OTG adapters is now the leading physical discriminator;
- ordinary USB connector semantics cannot safely be assumed for this port.

### LEADING HYPOTHESIS

- XGO connector pin 4 / micro-USB ID is repurposed or sensed by the controller subsystem;
- grounding it through an OTG adapter causes the freeze;
- one especially attractive possibility is that pin 4 is external/P2 DATA, but a mode/control role remains possible.

### NOT YET CONFIRMED

- whether B15 or L0 is the external stream;
- whether B7 reaches the Handle Interface connector directly;
- the exact micro-USB contact assignment;
- whether pin 4 is P2 DATA versus a mode/control signal;
- connector voltage and pull-up/pull-down network;
- whether the Handle Interface also exposes a real USB mode in addition to the serial bus.

## Safest discriminator

The highest-value next test is no longer another controller. It is to confirm the cable/adapter ID behavior electrically while unpowered, using a fine probe, needle, breakout, or sacrificial cable if available.

If the normal cable leaves ID open and the OTG adapter shorts ID to ground, the behavioral difference above becomes exceptionally strong evidence that XGO pin 4 is meaningful to the Handle Interface.

Until the routing is established, do not assume a normal USB pinout simply because the connector shell is micro-USB.
