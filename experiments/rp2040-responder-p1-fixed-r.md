# RP2040 XGO Player-2 responder — P1 fixed-R proof

Status: implementation design after P0 hardware closure. This document does **not** authorize wiring or active hardware testing until the series-protection wiring below is reviewed and the firmware binary is audited.

## Hardware facts carried from P0

P0 simultaneously observed the Handle Interface with the RP2040 as a high-impedance sampler.

- RED -> Pico GND/reference worked without disturbing normal XGO operation.
- YELLOW -> GP26 produced the scanner clock.
- GREEN -> GP27 produced the P2 DATA/load waveform.
- three transactions in one 52.429 ms capture started 16.0456 ms and 16.0189 ms apart;
- each transaction: GREEN host-low approximately 6.8-7.5 us, release, approximately 0.9-1.3 us later exactly 12 YELLOW clocks;
- measured signal levels are approximately 3.3 V.

Evidence class for those measurements: HW.

## P1 objective

Make the smallest active proof possible: synthesize **R pressed only**, because R is serial position 0 and the previous OTG disturbance independently produced an R-only symptom.

Expected P2 state:

```text
position 0  R      LOW
positions 1-11     released/HIGH
```

No other button state is generated.

## Electrical rule

GREEN is a shared conductor. XGO drives it LOW during load/reset. RP2040 therefore must never drive GREEN HIGH.

RP2040 sink/release behavior:

```text
assert R     -> output latch already LOW; enable GPIO output (sink)
release R    -> disable GPIO output; pin becomes high impedance
never        -> output HIGH
```

YELLOW/GP26 remains input-only with pulls disabled.

For the first active test place a **1 kOhm series resistor** between Pico GP27 and XGO GREEN. This limits current if either side is accidentally configured contrary to the intended sink/release state while remaining small relative to a normal logic pull-up. RED remains common reference; YELLOW remains directly observed at GP26. Do not connect BLUE or BROWN.

Conceptual wiring:

```text
XGO RED ---------------- Pico GND
XGO YELLOW ------------- Pico GP26 (input only)
XGO GREEN --- 1k series - Pico GP27 (LOW sink / high-Z only)
BLUE, BROWN ------------- not connected
```

## Responder state machine

The host itself pulls GREEN LOW for load/reset, so GREEN cannot be used as an ordinary independent load-input while the responder may also sink it. P1 instead uses the already-proven YELLOW transaction timing to delimit the 12-position sequence.

Idle: GP27 high-Z.

On the first YELLOW falling edge of a transaction:
1. sink GP27 LOW to represent serial position 0 / R;
2. release GP27 on the following YELLOW rising edge;
3. leave GP27 high-Z for the remaining eleven positions;
4. count the remaining clock edges;
5. return to idle after the 12th position.

Important timing caveat: firmware reconstruction says XGO samples position 0 immediately after releasing DATA and **before** the first clock-low edge. Therefore asserting R only when the first YELLOW falling edge occurs would be too late for position 0. The active implementation must instead detect the load/release phase early enough to sink GREEN before the host's position-0 sample.

Because the responder shares GREEN with the host, detecting that phase solely through GREEN while also driving it requires careful GPIO ownership. A safe implementation strategy is:

- GP27 high-Z while waiting;
- observe GREEN LOW as input;
- observe GREEN return HIGH after host release;
- immediately set output latch LOW and enable output to assert R;
- release at the first YELLOW falling edge, after position 0 has been presented;
- remain high-Z for positions 1-11.

This uses no actively driven HIGH state. The measured P0 interval from GREEN release to first YELLOW fall (0.9-1.3 us) is the response budget.

## Implementation consequence

A polling/IRQ C handler may have marginal and variable latency against a ~1 us first-bit budget. P1 should therefore use PIO for deterministic GREEN release detection and sink/release timing, with GP27 output value permanently LOW and only PINDIRS/OE changing.

Before hardware use, inspect the generated PIO program and C setup to verify:
- no instruction can drive GP26;
- GP27 output latch is LOW before OE can be enabled;
- no instruction writes HIGH to GP27;
- GP27 returns input/high-Z no later than first YELLOW falling edge;
- timeout/error paths release GP27;
- BLUE/BROWN remain unused.

## P1 success criterion

In a known two-player game:
- built-in P1 remains normal;
- P2 reports R only;
- no other P2 direction/action appears;
- no XGO freeze or reset;
- unplugging/releasing the adapter returns P2 to neutral.

Only after this fixed-R proof should the responder advance to arbitrary 12-position states / GP2040 integration.
