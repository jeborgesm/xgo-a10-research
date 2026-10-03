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


## HW checkpoint — DSO-TC3 Handle Interface characterization (2026-10-03)

Status: **HARDWARE OBSERVED; preserve exact observations separately from interpretation.**

A five-contact DIY micro-B breakout was built and continuity-tested before connection. All ten pairwise conductor combinations tested open/no-beep on the DSO-TC3 continuity function, establishing no detectable solder bridges.

Harness color map used during the experiment:

```text
RED    = micro-B pin 1
BLUE   = micro-B pin 2
GREEN  = micro-B pin 3
YELLOW = micro-B pin 4
BROWN  = micro-B pin 5
```

Important: these are physical micro-B contact numbers/colors only. Do **not** apply ordinary USB electrical semantics to them.

### DC observations during running game

The DSO-TC3 voltage function was sanity-checked against an AA cell and read approximately 1.3 V with correct polarity; reverse polarity displayed 0 V. During XGO gameplay, the breakout showed approximately 3.1 V with BROWN positive relative to RED. Subsequent oscilloscope measurements with RED used as reference showed:

- BLUE: approximately 0 V / essentially flat in the tested condition.
- GREEN: approximately 3.26-3.27 V steady high in representative captures (about 3.23-3.30 V min/max, ~0.05-0.06 Vpp).
- YELLOW: approximately 3.29 V high when idle between bursts.
- BROWN: approximately 3.2 V high relative to RED.

These observations show that the Handle Interface does not follow the initially assumed ordinary USB VBUS/GND polarity/behavior. RED was therefore treated only as the measured low/reference contact for subsequent scope work.

### YELLOW periodic burst — strong CLOCK candidate

With the XGO game continuously running and DSO-TC3 configured approximately:

```text
1 V/div
X1 probe
10 us/div
DC coupling
RUN
scope reference -> RED
scope signal    -> YELLOW
```

YELLOW intermittently produced a clear full-amplitude digital burst. Captured frames reported approximately:

- high level around 3.3-3.5 V;
- low level near 0 V;
- frequency approximately 252.6 kHz in a captured burst;
- period approximately 0.004 ms (~4 us);
- duty approximately 50%.

The visible waveform therefore corresponds approximately to ~2 us low / ~2 us high phases. This is a strong hardware match to the microsecond-scale shared-clock timing reconstructed independently from firmware. YELLOW is consequently a **strong CLOCK candidate**, but retain “candidate” until correlated against another signal or active responder test.

The user observed that the visible bursts appeared in pairs. Meaning of the pairing remains OPEN.

### BLUE observation

A roughly 28-second scope recording of BLUE relative to RED showed no comparable full-amplitude burst at the tested settings. BLUE remained essentially flat/near 0 V in that capture. Do not promote BLUE to DATA from connector convention alone.

### GREEN causes repeatable Player-2 phantom input

A particularly important behavioral observation occurred while probing GREEN. With the game running, Player 2 began jumping spontaneously while the GREEN measurement connection was attached. Removing the GREEN measurement cable from the harness stopped the spontaneous jumping. Reattaching GREEN reproduced the spontaneous Player-2 jumping. Removing it again stopped the behavior.

Observed sequence:

```text
GREEN measurement connection attached -> P2 spontaneous jumping
GREEN connection removed              -> P2 stops
GREEN connection reattached           -> P2 spontaneous jumping returns
GREEN connection removed              -> P2 stops again
```

This is **HW evidence of repeatable behavioral coupling** between physical micro-B pin 3 / GREEN and the live Player-2 input path.

Do not yet claim that GREEN is definitively DATA. The present evidence establishes that loading/biasing/measurement of GREEN can perturb the P2 decoded state. Because the reconstructed protocol is active-low serial input, DATA-line loading is a strong interpretation, but the exact mechanism and affected serial position remain to be proven.

### Instrument-control lesson

On this DSO-TC3 firmware, pressing OK/MENU from the oscilloscope screen invokes AUTO and can overwrite carefully selected scale/coupling settings. During manual captures, use the directional controls for selected parameters and avoid OK/MENU unless AUTO is explicitly desired.

### Updated promotion gate

Before any active RP2040 drive toward XGO:

1. preserve RED as the presently measured reference only, not a USB-semantic assumption;
2. correlate YELLOW bursts with firmware CLOCK timing and, ideally, simultaneous capture;
3. characterize GREEN with a higher-impedance/simultaneous digital capture to determine whether it is P2 DATA;
4. determine why the measurement connection on GREEN produces the repeatable phantom jump;
5. identify the affected raw serial/button position if possible;
6. design sink/release drive so the XGO host-driven load phase cannot contend with the responder.

No push-pull RP2040 connection is authorized by this checkpoint.
