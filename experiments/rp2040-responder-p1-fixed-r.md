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


## Local P1 build identity — pre-hardware

User locally configured and built the P1 target successfully with Pico SDK 1.5.1 / GNU Arm 10.3.1 from branch ending at `31cb3b5c900230b0e2cdfdfe162c3fa529321d10`.

```text
file:   xgo_p1_fixed_r.uf2
size:   47,616 bytes
SHA256: 54F640E7E8916ACD308C9840A6A1B3E27BB1B626A9F5B4D417FF6552EAF393A9
```

Source re-audit before hardware:
- PIO has no `set pins`, `out pins`, or sideset operation.
- the only output-control instructions are `set pindirs,1` and `set pindirs,0`;
- SET pin base/count is GP27/1;
- GP27 output latch is explicitly initialized LOW before the state machine is enabled;
- GP26 is included in the explicit input/high-Z pindir mask and is never in the PIO SET range;
- GP27 starts/re-enters high-Z while waiting for host load;
- responder asserts GP27 only after observing host GREEN low -> high;
- responder releases GP27 at the first YELLOW falling edge.

Hardware activation remains gated pending generated-header/disassembly verification and final decision on direct-vs-protected GP27 connection.


## Generated-code audit — PASS

The locally generated `xgo_fixed_r.pio.h` was inspected before hardware activation. It contains exactly ten instructions:

```text
0x2020 wait 0 pin,0
0x20a0 wait 1 pin,0
0xe081 set pindirs,1
0x201a wait 0 gpio,26
0xe080 set pindirs,0
0x209a wait 1 gpio,26
0xe02a set x,10
0x201a wait 0 gpio,26
0x209a wait 1 gpio,26
0x0047 jmp x--,7
```

There is no generated `SET PINS`, `OUT PINS`, sideset, or other pin-value write in the PIO program. The only active bus operation is changing the configured SET pin's direction.

ARM disassembly also confirms the initialization calls are present before SM enable: `pio_sm_set_pins_with_mask` with value 0 establishes the GP27 output latch LOW, and `pio_sm_set_pindirs_with_mask` establishes the GP26/GP27 high-Z/input state. A second pindir-high-Z call occurs immediately before enabling the state machine.

Generated-code audit result: **PASS** for the intended LOW-sink/high-Z architecture. This does not itself constitute a hardware result.


## Clock-count audit and correction

The first generated P1 candidate loaded X=10 after completing clock #1. RP2040 PIO `JMP X--` branches based on the pre-decrement value, so an initial X=10 executes the loop 11 times. That would consume clocks #2 through #12 plus one extra clock before rearming.

Correct requirement after clock #1 is exactly eleven remaining clocks (#2..#12). Because the loop body must execute 11 times, X must start at **9**: executions see pre-decrement X values 9,8,...,0 and the final X=0 iteration falls through after clock #12.

The PIO source was corrected from `set x,10` to `set x,9` in commit `9051f405198c841095b8a027fb9cdf0242b6cb58`.

The previously built UF2 SHA256 `54F640E7E8916ACD308C9840A6A1B3E27BB1B626A9F5B4D417FF6552EAF393A9` is therefore **REJECTED / DO NOT FLASH**. A new build identity and generated-header audit are required before P1 hardware use.


## Corrected P1 build — generated-header audit PASS

User rebuilt after the clock-count correction.

```text
SHA256: 74A5D33BAC1AD12E1272E98F94C9BB49224AC155E2383DE232C71BFA2B35EE22
```

Generated `xgo_fixed_r.pio.h` confirms instruction 6 is now `0xe029 // set x,9`. The remaining generated instruction stream is unchanged: host GREEN low/high wait, GP27 PINDIR sink, first YELLOW falling-edge wait, GP27 PINDIR release, then eleven remaining clock cycles and rearm.

The previous SHA256 `54F640E7E8916ACD308C9840A6A1B3E27BB1B626A9F5B4D417FF6552EAF393A9` remains rejected.

Corrected generated-header audit: **PASS**. Hardware behavior remains unproven until an explicit P1 hardware test.


## P1 hardware result — PASS

With the corrected P1 UF2 (SHA256 `74A5D33BAC1AD12E1272E98F94C9BB49224AC155E2383DE232C71BFA2B35EE22`) running on the RP2040 and the live three-wire harness actually connected:

- XGO RED -> Pico GND
- XGO YELLOW -> GP26
- XGO GREEN -> GP27
- BLUE/BROWN disconnected

Contra was already running in 2-player mode. On reconnecting the harness, Player 2 began **constantly jumping**. The existing mapper maps XGO raw R to the FC/Contra A action, so this is the expected visible behavior for the fixed serial-position-0 R responder.

An earlier no-action observation is invalid because the temporary harness had mechanically disconnected during an unnecessary XGO power cycle; it must not be treated as a protocol failure.

**HW conclusion:** P1 fixed-R responder PASS. The RP2040 can electrically and temporally synthesize XGO Handle Interface Player-2 serial position 0 using the measured GREEN DATA/load and YELLOW CLOCK conductors with a LOW-sink/high-Z GP27 strategy. This proves the first active RP2040 -> XGO P2 input injection on this specimen.

This proof establishes position 0 only. Arbitrary 12-button serialization remains the next experiment.
