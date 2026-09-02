# XGO vs SF2000 keypad/controller protocol equivalence

## Status
Direct protocol-level comparison between the reconstructed XGO controller scanner and the modern SF2000 implementation model used by FrogQEMU/UniFrog.

## Headline finding
The XGO controller scanner is not merely "similar" to the SF2000 local keypad scanner. It implements the same 12-button serial contract, including the exact button bit order and the same unusual load mechanism where the host temporarily drives the data line low, then switches it back to input before clocking samples.

The major XGO difference is topology: XGO scans **two data streams in parallel** on B15 and L0 using shared clock B7, while stock SF2000 scans one local keypad stream on L23 using clock L24 and handles wireless input separately.

## SF2000 open-source reconstruction
FrogQEMU models the stock SF2000 local keypad as:

- data: GPIO L23
- clock: GPIO L24
- active-low data
- 12 sampled buttons
- data line temporarily configured as output and driven low to reset/load the shift source
- data returned to input
- one sampled bit per rising clock progression

FrogQEMU defines the 12 positions in this exact order:

```text
0  R
1  Y
2  X
3  L
4  A
5  B
6  SELECT
7  START
8  UP
9  DOWN
10 LEFT
11 RIGHT
```

UniFrog independently implements the same SF2000 scanner in source code. Its hardened scan uses:

```text
KEY_SHIFTER_CLK_PIN = L24
KEY_SHIFTER_PL1_PIN = L23
load delay          = 4 us
settle delay        = 4 us
clock low           = 3 us
clock high          = 3 us
```

The sequence is:

1. configure L24 as output and drive clock high;
2. configure L23 as output;
3. drive L23 low;
4. wait 4 us;
5. switch L23 to input;
6. wait 4 us;
7. sample active-low bit;
8. drive clock low;
9. wait 3 us;
10. drive clock high;
11. wait 3 us;
12. repeat for 12 bits.

UniFrog documents that the explicit delays were added because this bus is timing-sensitive across SCPU frequency changes.

## XGO reconstructed scanner
XGO firmware statically reconstructs as:

- stream 0 data: GPIO B15
- stream 1 data: GPIO L0
- shared clock: GPIO B7
- active-low data
- 12 samples per stream
- both data lines temporarily configured as outputs and driven low
- approximately 4 us load delay
- both data lines returned to inputs
- shared clock pulses between samples
- approximately 2 us low delay in the stock XGO scanner
- both streams retained independently as two controller state words

The XGO 12-bit order is:

```text
0  R
1  Y
2  X
3  L
4  A
5  B
6  SELECT
7  START
8  UP
9  DOWN
10 LEFT
11 RIGHT
```

This is an exact positional match to the SF2000 local keypad contract modeled by FrogQEMU.

## Side-by-side comparison

| Property | SF2000 | XGO |
|---|---|---|
| serial controller class | active-low shift-register style | active-low shift-register style |
| data streams | 1 local stream | 2 parallel streams |
| data GPIO | L23 | B15 + L0 |
| clock GPIO | L24 | B7 |
| idle clock | high | high |
| load/reset method | data output low, then input | both data outputs low, then inputs |
| load delay | 4 us in UniFrog hardened implementation | ~4 us in stock XGO |
| settle delay | 4 us in UniFrog hardened implementation | no separately identified explicit delay yet |
| clock low delay | 3 us hardened | ~2 us stock XGO |
| clock high delay | 3 us hardened | no separately identified explicit delay yet / instruction overhead |
| bits sampled | 12 | 12 per stream |
| polarity | active-low | active-low |
| button order | R,Y,X,L,A,B,SELECT,START,UP,DOWN,LEFT,RIGHT | exact same order |

## Interpretation

### CONFIRMED
- XGO and SF2000 use the same 12-position logical serial button order.
- Both use the same nonstandard host-driven-low load/reset mechanism on the data line(s).
- Both use active-low serial sampling with a shared GPIO clock.
- XGO duplicates the serial data path into two simultaneous channels instead of SF2000's single local stream.

### STRONG INFERENCE
The XGO scanner is a board-specific derivative of the same HC15xx/SF2000 keypad protocol, not an independently invented but coincidentally similar interface.

A likely architectural evolution is:

```text
stock SF2000
  local keypad serial stream (L23/L24)
  + separate XN297 wireless controller path

XGO fork
  serial stream 0 (B15)
  serial stream 1 (L0)
  shared clock (B7)
  both merged by application as controller slots
```

This fits the already observed XGO software structure, where the two scanner result words are treated as a two-element controller array and merged with RF/controller state.

### Important consequence for the Handle Interface
Because the XGO external-player path uses the same logical 12-bit contract as stock SF2000 local keypad scanning, an X60/DY12/SF2000-family wired controller no longer needs to be treated as a vague compatibility candidate. The protocol-level evidence now says that a compatible accessory would only need the correct physical pin routing and electrical levels; the button serialization contract itself is already a direct match.

This substantially raises confidence that the XGO Handle Interface is a board-specific physical exposure of the same serial keypad bus family.

### OTG-adapter freeze interpretation
The empty-OTG-adapter freeze becomes more interesting under this model. If the micro-USB ID contact is wired to one of the XGO serial data paths, grounding it would hold that active-low stream asserted. Because a low data value means "pressed", a permanently grounded serial data pin would decode as every sampled button asserted on that stream.

This remains a hypothesis until the connector pinout is physically mapped, but it now sits on top of a confirmed protocol model rather than a generic USB guess.

## Remaining unknowns
- which XGO stream is physically local P1 and which reaches the Handle Interface;
- which micro-USB contact maps to B15, L0 or B7;
- whether XGO exposes power/reference on VBUS and at what voltage;
- whether micro-USB ID is one of the serial signals;
- whether X60/DY12 controller wiring is directly pin-compatible or only protocol-compatible;
- exact electrical pull-up/pull-down values and logic-high voltage.

## Sources
- `axgdev/frogqemu`, `qemu/hw/mips/sf2000.c`: defines SF2000 keypad L23 data, L24 clock, 12-bit active-low shift model, and exact button ordering.
- `axgdev/frogqemu`, `docs/SF2000.md`: documents active-low L23/L24 shift-register contract used to make stock launcher navigation work in QEMU.
- `axgdev/UniFrog`, `foundation/src/platform/sf2000/input/unifrog_input.c`: current open implementation of SF2000 and GB300 keypad scanners, including explicit 4 us load / 4 us settle / 3 us low / 3 us high timing.
- `axgdev/UniFrog`, `docs/clock-speed-resilience.md`: documents timing sensitivity of the SF2000 L23/L24 keypad bus.
