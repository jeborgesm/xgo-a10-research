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


### GREEN phantom-input specificity follow-up

A follow-up gameplay observation tightened the GREEN behavioral result. With the DSO-TC3 reference on RED and signal probe attached to GREEN in the same configuration that causes the phantom input, Player 2 was observed without intentional controller input.

Result: **the phantom action was consistently jump only**. No spontaneous left/right movement, crouch, shooting, Start, or other action was observed. In the first run Player 2 eventually fell into the water, where jumping no longer produced useful movement. After rebooting the game and starting a fresh 2-player session, attaching/probing GREEN again reproduced the repeated jump-only behavior.

Observed behavior across sessions:

```text
GREEN probed -> repeated P2 jump only
no other P2 actions observed
P2 falls into water -> jump ineffective
fresh 2P session + GREEN probed -> repeated P2 jump returns
```

Evidence class: **HW** for the repeatable gameplay behavior. Interpretation remains **INF**: the action specificity is consistent with GREEN perturbing a particular sampled state/serial position rather than producing arbitrary P2 noise. This strengthens GREEN as the P2 DATA candidate but does **not** yet prove GREEN is DATA or establish the electrical mechanism.


### GREEN-to-RED direct-short behavioral finding

An accidental manual contact test produced a stronger behavioral result than the oscilloscope-loading experiment. With the XGO running a 2-player game, physical harness GREEN was momentarily shorted/touched directly to physical harness RED. Player 2 generated game inputs. Repeated brief GREEN-to-RED contacts produced different P2 actions, including **shooting** and at times **left/right movement**.

Observed sequence, as reported during the live hardware session:

```text
GREEN touched/shorted to RED -> P2 input generated
repeated brief contacts       -> shooting and sometimes left/right movement
continued poking              -> different P2 actions from successive contacts
```

Evidence class: **HW** for the physical contact and resulting P2 gameplay actions. Interpretation: **INF**. This substantially strengthens the conclusion that GREEN is electrically coupled to the live P2 serial-input path and is consistent with an active-low DATA conductor: asynchronous manual grounding can overlap different scanner sample windows and therefore decode as different button positions. However, this does not yet constitute timing-correlated proof that GREEN is DATA.

This result also explains why the earlier oscilloscope connection could yield a repeatable jump-only disturbance while direct manual grounding yields multiple actions: the scope presents a different electrical load, whereas brief direct contacts can span arbitrary portions of the polling transaction. This explanation remains **INF** until simultaneous GREEN/YELLOW capture.

**Safety gate:** do not intentionally repeat direct GREEN-to-RED shorts. The observation is already sufficient to preserve; subsequent characterization should use the passive RP2040 capture. No active RP2040 output is authorized by this finding.


## HW checkpoint — first passive RP2040 simultaneous capture (2026-10-03)

Status: **HW PASS for passive correlation; capture file is serial-output truncated but contains a complete observed polling transaction.**

P0 was locally built for Raspberry Pi Pico/RP2040 from branch head `7ad03b8` with Pico SDK 1.5.1 / GNU Arm Embedded 10.3.1. The flashed UF2 was 67,072 bytes, SHA-256:

`42FD0BA6DFE6783B45FCA8C0F898E8885E46A0720B4719CC1DD0450EAAF325B8`

The Pico enumerated as a USB serial device on COM5. For the first live passive capture only these XGO harness contacts were connected:

```text
RED    -> Pico GND
YELLOW -> Pico GP26 (input only)
GREEN  -> Pico GP27 (input only)
```

BLUE and BROWN remained disconnected. Pico power came independently from the PC USB connection. The P0 firmware contains no XGO-facing output operation.

The host capture script reported a timeout before receiving `END XGO_P0`, but inspection of the saved file shows that this was an **output-transfer timeout, not a failed acquisition**. The file begins with the valid firmware header:

`BEGIN XGO_P0 rate=10000000 words=16384`

and contains 12,483 complete 32-bit capture words (199,728 two-bit samples, about 19.973 ms at 10 MHz) before truncating during the serial dump. At 115200 baud, dumping all 16,384 text-formatted words necessarily takes longer than the script's 10-second read timeout.

Most importantly, the retained portion contains a clean simultaneous transaction:

- GREEN is normally high, then has one low interval of approximately **7.2 us**.
- GREEN returns high before the clock sequence.
- Approximately **8.5 us after the start of the GREEN low interval**, YELLOW begins a burst.
- YELLOW contains exactly **12 low pulses** in the observed burst.
- Individual YELLOW low widths are approximately **2.4-3.0 us** at this fixed-rate digital sampling resolution.
- Successive YELLOW low pulses are separated by roughly the expected microsecond-scale scanner period.
- GREEN remains high throughout the 12 YELLOW clock pulses in this captured idle/no-P2-button transaction.

Counts over the retained partial capture:

```text
complete capture words: 12483
samples:                199728
YELLOW low samples:     330
YELLOW edges:           24
YELLOW low runs:        12
GREEN low samples:      72
GREEN edges:            2
GREEN low runs:         1
```

Evidence classification:

- **HW:** simultaneous passive capture shows GREEN host-driven-low/release behavior followed by an exactly 12-pulse YELLOW burst.
- **BIN/SRC correlation:** this matches the independently reconstructed XGO scanner contract in which the DATA lines are driven low for load/reset, released to input, and then sampled across 12 positions under the shared clock.
- **Conclusion:** YELLOW is now strongly timing-correlated as the scanner CLOCK and GREEN is strongly timing-correlated as the Handle Interface / Player-2 DATA conductor. This is materially stronger than connector-convention inference or the earlier phantom-input observations.

The serial truncation should be fixed before button-state captures by allowing sufficient dump time or by changing the host reader so timeout is applied only to stalled reads rather than the total transfer. It does not invalidate the transaction already present in this file.

This checkpoint satisfies the core passive-correlation purpose of P0. **It does not authorize push-pull drive.** Any first active responder must still use sink/release behavior so the XGO host can own the DATA conductor during its load/reset phase without contention.
