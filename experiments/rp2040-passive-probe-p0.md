# RP2040 passive probe — Test P0 plan

Status: READY FOR BUILD DESIGN; no XGO connection authorized until the exact RP2040 board and passive input network are selected.

## Purpose

Use an RP2040 as a passive digital instrument before using it as a controller.

P0 must never drive an XGO Handle Interface signal. All XGO-facing RP2040 GPIOs remain inputs/high-impedance for the entire run.

## Signals of interest

Observe the three unresolved micro-B contacts simultaneously:

- D-
- D+
- ID

Ground is shared only after the passive protection/front-end design is fixed.

VBUS is **not** connected to an RP2040 GPIO in P0.

## Questions P0 can answer

1. Which of D-/D+ carries the periodic XGO scanner clock?
2. Which carries the host-driven-low load/reset plus serial DATA behavior?
3. Does ID transition during ordinary polling?
4. What changes when the previously tested empty OTG adapter grounds ID?
5. Does the OTG R-only condition correlate with a prolonged low state on DATA across sample position 0?
6. What are the observed clock/load durations and polling interval?

P0 cannot safely determine analog voltage magnitude. It is a digital timing/correlation instrument, not a DMM or oscilloscope.

## Capture architecture

Preferred implementation:

```text
D-  -- passive protected input --\
D+  -- passive protected input ----> RP2040 PIO sampler -> DMA/RAM -> USB serial/file
ID  -- passive protected input --/
```

Use contiguous RP2040 GPIOs if the chosen board permits it so one PIO IN instruction can sample all three lines.

Initial capture should use fixed-rate sampling rather than edge IRQ timestamps. A 5-10 MHz digital sample rate is already far above the reconstructed XGO microsecond-scale timing and keeps analysis simple.

At 10 MHz:

```text
1 sample = 100 ns
~2 us clock-low phase = ~20 samples
~4 us load phase      = ~40 samples
```

This is sufficient to distinguish the expected scanner waveform without requiring analog reconstruction.

## Firmware safety invariants

At boot and throughout P0:

- XGO-facing pins initialized as inputs;
- output-enable never asserted;
- internal pull-ups/pull-downs disabled unless a later controlled test explicitly requires them;
- no PIO SET/PINDIRS instruction may target observed pins;
- no firmware mode switch to output is present in the P0 binary;
- VBUS is not sampled through a raw GPIO;
- capture continues even if no recognizable waveform is found.

This should be a separate diagnostic UF2 from the eventual responder firmware.

## Capture sequence

### P0-A — Handle Interface empty

Capture D-/D+/ID while XGO is:

1. at normal UI;
2. in hidden controller diagnostic if practical.

Expected discriminator:

- one D line may show B7-like periodic clock bursts;
- the other may show the DATA load/release behavior;
- ID may remain static.

### P0-B — normal non-OTG plug/cable

Repeat with the known normal micro-B cable condition that does not disturb controls.

This checks whether passive connector insertion changes the observed lines.

### P0-C — OTG R-only condition

Repeat the already-known empty-OTG condition while capturing.

Correlate the phantom R report with:

- ID grounded/static change;
- DATA low duration around load release;
- first sample timing;
- any change in CLOCK.

A DATA low tail that crosses only sample position 0 would directly support the current delayed-release/first-sample-contamination model.

## Automatic decoder

After raw capture is validated, host-side analysis should:

1. identify each line's transition count;
2. find repeated low/high pulse widths;
3. detect ~4 us load candidates;
4. identify ~2 us clock-low pulses;
5. segment candidate 12-position transactions;
6. print per-line timing statistics;
7. compare normal vs OTG captures.

Do not assume D+=CLOCK or D-=CLOCK in the decoder. Score both hypotheses from the capture.

## Promotion gate to active responder

No RP2040 output toward XGO until P0 evidence establishes:

- a CLOCK candidate;
- a DATA candidate;
- stable digital levels through the protected front end;
- no evidence that either observed contact is an unsafe supply rail;
- an interface strategy that avoids contention during XGO's host-driven-low DATA load phase.

Only then create P1: fixed-pattern responder.

## P1 preview

P1 should first expose a harmless, unmistakable fixed serial pattern, using sink/release behavior rather than push-pull drive.

Suggested initial pattern:

```text
SELECT + START only
positions 6 and 7 active-low
all other positions released
```

The XGO hidden diagnostic can then validate serialization before gameplay testing.

## RP2040/GP2040 relationship

Do not fork GP2040-CE for P0. P0 is instrumentation and should remain tiny and auditable.

Once P1/P2 prove the bus, integrate the responder with GP2040-CE's normalized gamepad state. GP2040-CE already centralizes controller state in its GamepadState architecture, making the later transport adapter a clean integration target.
