# XGO Local / Wired Input Path — Disassembly Findings

Status: **confirmed two-channel serial input scan; physical Handle-Interface routing is strong but not yet electrically confirmed**.

## Summary

A deeper disassembly of the XGO input routine reveals a second, non-RF controller path that is substantially more interesting than the generic USB strings.

The firmware scans **two independent active-low serial button data lines in parallel**, using one shared clock. Each line builds a complete raw controller state using the same 12-button bitmap used by the SF2000 RF protocol. The two resulting states are preserved as separate controller slots and are later ORed, slot-for-slot, with the corresponding RF Player 1 / Player 2 states.

In other words, the firmware architecture is effectively:

```text
serial input channel 0 ----+
                           +--> Player 1 raw state --> button mapping
RF pipe / Player 1 --------+

serial input channel 1 ----+
                           +--> Player 2 raw state --> button mapping
RF pipe / Player 2 --------+
```

Because the XGO has only one built-in set of controls but exposes a dedicated external `Handle Interface`, the second serial channel is a strong candidate for the wired controller path. Physical trace continuity to the connector is still required before calling that assignment confirmed.

## State arrays and merge point

The main input function begins around `0x8035d4c4`.

It establishes two arrays:

```text
serial/local states: gp - 0x0d2c   (two 32-bit words)
RF states:           gp - 0x0d0c   (two 32-bit words)
```

At the per-player decode loop, firmware loads the corresponding word from each array and ORs them together before translating raw button bits:

```text
8035d524  addu  $a0,$t0,$s5      ; serial/local state[player]
8035d528  addu  $t1,$t0,$s7      ; RF state[player]
8035d52c  lw    $s4,0($a0)
8035d530  lw    $a2,0($t1)
8035d53c  or    $a2,$a2,$s4
```

The loop runs for exactly two player slots (`sltiu ..., 2`).

The RF receive code independently stores its packet into `gp - 0x0d0c + player*4`, confirming which array is RF. The other two-word array is therefore a distinct physical input source.

## Two-line synchronous serial scan

When the local/serial scan runs, firmware clears both state words:

```text
gp - 0x0d2c = 0
gp - 0x0d28 = 0
```

It then manipulates H1512 GPIO register groups directly.

Observed input lines:

```text
0xb8800350 bit 15  -> GPIO bank B bit 15 (B15)
0xb8800050 bit 0   -> GPIO bank L bit 0  (L0)
```

Observed shared clock:

```text
0xb8800354 bit 7   -> GPIO bank B bit 7 (B7)
```

The code first drives the two data lines low and then changes them back to input before sampling. It subsequently samples B15 and L0 together, records pressed bits independently into the two state words, and pulses B7 between samples.

This pattern is strikingly similar in *electrical shape* to the dual-data-line shift-register scan reconstructed for GB300-family controls: data lines are briefly driven low for the load phase, switched to input, then sampled while a common clock advances the shift register. The XGO pin assignment is different, and—critically—the XGO keeps the two data streams as separate Player 1 / Player 2 states instead of combining them.

### Host-driven load phase — important protocol detail

The scan does **not** look exactly like a standard SNES controller interface with a separate dedicated LATCH wire. The firmware itself briefly changes both controller data GPIOs from input to output, drives them low, then returns them to input before reading the first bit.

Representative sequence:

```text
B15 direction -> output
L0  direction -> output
B15 output    -> low
L0  output    -> low
short delay
B15 direction -> input
L0  direction -> input
sample both data lines
pulse B7 clock
```

This means any external controller connected directly to the serial path must tolerate the host temporarily pulling its DATA line low as part of the load/reset phase. That is closer to the related HC15xx/GB300 scan scheme than to a literal SNES electrical interface.

It therefore remains possible that a cheap SNES-style **USB** pad works through a separate supported USB path, but a native SNES controller should not yet be treated as a pin-compatible raw-serial accessory.

## Full 12-button sequence

The scan constructs the standard SF2000 raw button bitmap in this order:

```text
0x1000  R
0x2000  Y
0x4000  X
0x0800  L
0x0080  A
0x0040  B
0x0020  SELECT
0x0010  START
0x0008  UP
0x0004  DOWN
0x0002  LEFT
0x0001  RIGHT
```

For every position, firmware performs the same operation twice:

```text
if B15 is low -> set that button bit in serial state[0]
if L0  is low -> set that button bit in serial state[1]
pulse shared B7 clock
```

This is not a one-off accessory status signal. Both lines carry a complete gamepad-sized 12-button stream.

## Poll scheduling — serial scan is part of the core input loop

A further pass resolved an important ambiguity: the two-channel serial scanner is **not entered only after a USB attach event**.

The main input loop keeps a poll counter at `gp - 0x5f0c`. Its low bits schedule work inside the same persistent controller task. When `(poll_counter & 3) == 0`, firmware branches directly into the two-line serial scan at approximately `0x8035d770`. Other phases process the already-collected controller state and service the RF path.

Later in the same loop the counter is incremented and execution repeats:

```text
8035d6c8  lw     ..., -0x5f0c($gp)
8035d6cc  addiu  ..., ..., 1
8035d6d0  sw     ..., -0x5f0c($gp)
...
8035d50c  lw     ..., -0x5f0c($gp)
8035d510  andi   ..., ..., 3
8035d514  beqz   ..., 0x8035d770   ; run serial scan every fourth phase
```

This materially strengthens the direct-GPIO interpretation. The serial channels are continuously serviced as part of the normal controller task; no USB attach state is required to activate the scanner.

The same task also interleaves RF polling, which explains the architecture cleanly: periodic local/wired scan plus periodic wireless receive, followed by per-player OR/merge.

## Why this matters for the Handle Interface

This is currently the strongest firmware-side clue about the wired controller port.

The XGO has:

- one built-in physical control set;
- two complete serial controller channels in firmware;
- a dedicated external `Handle Interface` connector;
- separate RF P1/P2 states that are merged slot-for-slot with those serial channels;
- a serial scanner that runs periodically in the normal controller task without requiring USB attach state.

A very plausible mapping is therefore:

```text
serial channel 0 (B15) -> built-in controls / P1
serial channel 1 (L0)  -> Handle Interface / P2
shared B7 clock         -> common scan clock
```

The reverse assignment of B15/L0 is also possible; the important point is that there are two distinct serial controller streams.

### Confidence

**CONFIRMED**

- two separate 32-bit non-RF controller state words exist;
- the firmware scans two active-low GPIO data lines in parallel;
- one shared GPIO clock advances the scan;
- each data line independently produces the full 12-button SF2000 raw bitmap;
- these two states map to Player 1 / Player 2 positions and are ORed with RF P1 / P2 respectively;
- the serial scan is scheduled periodically inside the normal controller loop rather than being conditionally enabled by a USB attach event;
- the host temporarily drives both data lines low before sampling them.

**STRONG EVIDENCE**

- one serial stream is the built-in controls and the second is the wired external-controller mechanism;
- the Handle Interface likely carries, directly or through very small intermediary logic, this synchronous controller scan protocol rather than requiring a general-purpose USB HID stack.

**NOT YET CONFIRMED**

- whether B15 or L0 is the built-in-control data line;
- whether the other line physically reaches the Handle Interface;
- which connector contact carries data and which carries the shared clock/load behavior;
- whether the connector also exposes any H1512 USB-controller functionality in parallel or in another mode.

## GP2040 experiment reinterpretation

The GP2040 result now has a plausible electrical explanation.

A micro-USB shell provides five contacts, but the connector does not have to carry USB D+/D-. A proprietary gamepad interface could use power, ground, clock, data, and another control/ID contact. If an ordinary USB gamepad drives contacts that XGO firmware expects to use as an active-low serial scan bus, the scan can be corrupted. Because the two serial channels share timing/control resources, that could also interfere with the built-in controls until the accessory is removed.

The periodic/unconditional nature of the serial scan makes this contention model more plausible than before. The firmware continues manipulating its serial GPIOs whether or not a USB accessory has enumerated.

This interpretation fits the observed `5 V present + no controller input + local controls freeze` behavior better than a simple unsupported-HID model, but physical pin tracing is still required.

## Best next physical test

Without applying any external voltage, continuity/logic analysis can answer the remaining question:

1. identify micro-USB ground and 5 V;
2. trace the remaining contacts to H1512-side GPIO or intermediary logic;
3. observe whether one contact carries a repeating clock during normal menu operation;
4. observe whether another contact is sampled active-low as button data;
5. compare activity while built-in buttons are pressed and while the Handle Interface is empty.

A passive logic-analyzer capture is preferable to further random controller attachment until the pinout is known.
