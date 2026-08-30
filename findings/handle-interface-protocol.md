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

That matters when interpreting the earlier GP2040 test: a conventional USB controller connected through a passive/OTG adapter may drive connector contacts at the same time the XGO firmware is attempting to use its serial GPIO bus.

## What a compatible external controller would need to do

If the Handle Interface is physically wired to this scanner, a compatible controller must at minimum:

1. be safe when its data line is pulled low by the host for roughly 4 us;
2. release/drive an active-low serial data stream after the load phase;
3. present the first bit before the first clock pulse;
4. advance to the next bit on the host clock transition;
5. provide at least the 12 expected positions in the XGO order;
6. operate at whatever voltage is present on the actual connector, still to be measured.

A simple lightweight controller could absolutely implement this with inexpensive logic or a tiny ASIC. A low-power controller is therefore plausible, but connector and voltage compatibility must be established before trying arbitrary devices.

## Current confidence

### CONFIRMED from firmware

- two parallel active-low data streams;
- one shared clock;
- host-driven data-low load/reset phase;
- approximately 4 us explicit load delay;
- approximately 2 us explicit clock-low delay;
- twelve samples per stream in a known button order;
- periodic operation independent of USB attachment state;
- channel states merge directly into P1/P2 alongside RF input.

### STRONG EVIDENCE

- this is a hardware controller bus rather than an abstract emulator-only data structure;
- one stream is likely the built-in controls and the other the external Handle Interface;
- the protocol belongs to the same general HC15xx controller-bus family as related SF2000/GB300 hardware.

### NOT YET CONFIRMED

- whether B15 or L0 is the external stream;
- whether B7 reaches the Handle Interface connector directly;
- the micro-USB contact assignment;
- connector voltage and pull-up/pull-down network;
- whether an adapter's micro-USB ID contact affects operation;
- whether the Handle Interface also exposes a real USB mode in addition to the serial bus.

## Safest discriminator

The highest-value physical observation is now very small: with the XGO powered normally and no accessory attached, passively observe the Handle Interface contacts. If one non-power contact shows a repeating narrow clock-like pulse train and another sits at an input idle level, that would strongly connect the external connector to this reconstructed bus.

Until that routing is established, do not assume a normal USB pinout simply because the connector shell is micro-USB.
