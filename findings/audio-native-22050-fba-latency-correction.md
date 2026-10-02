# Native 22050 does not inherently double FBA latency; 482 is an admission ceiling, not a forced preload

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **CORRECTION / EXACT QUEUE MODEL**

## Correction

Earlier native-rate notes correctly observed that the fixed 482-unit admission threshold represents twice as much wall-clock audio at 22050 as at 44100:

```text
44100 -> 43.72 ms
22050 -> 87.44 ms
```

That arithmetic is true.

However, wording that suggested native 22050 would therefore *cause* roughly double FBA latency was too strong.

The 482 value is a **maximum admission threshold**, not a required startup preload or target occupancy.

Actual queue depth is determined by the burst schedule and hardware drain.

## Exact rate-corrected FBA model at native 22050

Keep:

```text
FBA producer       367 frames/callback
scheduler          60 Hz
frontend quantum   576 source frames
hardware rate      22050
lower unit         2 stereo frames
admission ceiling  482 units
```

Correct the 22020->22050 producer mismatch exactly.

One 576-source-frame frontend block then averages:

```text
288.392... lower units
```

and can be represented exactly over the 367-block phase as:

```text
295 blocks * 144 units
72 blocks  * 145 units
```

The minimum ideal backlog required to bridge the deterministic burst pattern is:

```text
478.6 lower units
```

At native 22050:

```text
478.6 * 2 / 22050 ~= 43.41 ms
```

This is essentially the same **time** requirement as the 44.1-kHz rate-corrected model, where the equivalent backlog is 957.2 units.

For the same wall-clock backlog, the cursor-unit count halves when the sample rate halves because each cursor unit still represents two PCM frames.

## Admission threshold is not binding in this model

At native 22050 the required burst-bridging backlog remains below:

```text
482-unit admission ceiling
```

Therefore the unchanged 482 threshold does not force the queue to fill to 43.72 ms.

It merely permits that much queued audio before blocking additional submissions.

For normal deterministic FBA production, the queue can operate materially below the ceiling.

## Consequence for first native-rate experiment

This removes a major concern about a clean native-22050 test.

A first experiment can plausibly keep:

- stock 960 hardware count;
- stock 482 admission predicate;
- stock 576 frontend quantum;

while changing only:

- selected hardware rate 44100 -> 22050;
- x2 conversion -> 1x.

That experiment would not *by definition* double latency.

Actual hardware queue occupancy still needs observation/listening, but the software queue arithmetic does not require an 87-ms preload.

## Why threshold rescaling should remain deferred

Changing the 482 threshold still means decoupling it from the 960 hardware-count parameter.

Since the exact FBA model does not require that change merely to avoid a latency doubling, there is even less reason to bundle threshold surgery into the first native-rate fidelity test.

This improves experimental isolation.

## Smaller frontend quantum at native rate

The same time-domain behavior holds when reducing the frontend quantum.

Rate-corrected native-22050 ideal burst-bridging requirements are approximately:

```text
quantum 576 -> 239.3 units -> 43.41 ms
quantum 384 -> 191.3 units -> 34.70 ms
quantum 288 -> 167.3 units -> 30.35 ms
quantum 192 -> 143.3 units -> 26.00 ms
```

All remain below the 482 admission ceiling.

Thus queue-latency improvement can later be pursued by reducing the frontend batching quantum without first altering the lower threshold.

## Evidence discipline

- 482 semantics: **BIN**
- cursor unit = two stereo frames: **BIN**
- exact FBA burst phase: **BIN/SRC + arithmetic**
- backlog values: **deterministic ideal model**
- physical DAC/startup occupancy: **OPEN/HW**

## Revised conclusion

Native 22050 is now a cleaner CPS1 fidelity experiment than previously thought.

It may reduce conversion/copy workload and remove x2 zero-order hold without inherently imposing a doubled software queue latency.

## Hardware gate

Not yet crossed; implementation patch surface and mono behavior are still being closed.
