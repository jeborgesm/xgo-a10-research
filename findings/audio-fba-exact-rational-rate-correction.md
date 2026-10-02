# FBA fixed-367 rate correction has an exact rational solution at the stock 60-Hz scheduler

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN/SRC + EXACT ARITHMETIC; DESIGN LEAD, NO CANDIDATE**

## Current XGO contract

Exact XGO binary:

```text
FBA source rate       = 22050 Hz
FBA batch per run     = 367 stereo source frames
XGO scheduler         = exactly 60 emulated frames/s
frontend quantum      = 576 source frames
stock low-rate path   = x2 frame repetition to 44100
lower cursor unit     = 4 stereo output frames
```

Thus FBA currently supplies:

```text
367 * 60 = 22020 source frames/s
```

against a declared 22050-Hz source clock.

## Exact ratio

The correction ratio is not approximate:

```text
22050 / 22020 = 735 / 734
```

This is unusually convenient.

Every two FBA callbacks contain:

```text
2 * 367 = 734 source frames
```

so the long-term rate deficit is exactly equivalent to needing:

```text
735 output-time source frames for each 734 supplied
```

at the current 60-Hz gameplay cadence.

This closes the arithmetic target for eliminating the fixed-367 deficit without changing the gameplay scheduler.

## If retaining 44.1-kHz hardware output

The exact conversion ratio from the actual 22020-frame/s producer to the 44100-frame/s drain is:

```text
44100 / 22020 = 735 / 367
```

So each 367-frame FBA callback corresponds to exactly:

```text
735 output frames
```

at a perfectly rate-matched 44.1-kHz stream.

Stock XGO instead produces:

```text
367 * 2 = 734 output frames
```

per callback-equivalent amount of source PCM.

That is the entire 60-output-frame/s deficit in one line:

```text
735 desired - 734 stock = 1 missing output frame per emulated frame
```

## Frontend 576-frame batching changes the implementation granularity

The converter does not receive individual 367-frame callbacks.

The frontend first aggregates source PCM into fixed 576-source-frame blocks.

For one 576-frame block, the exact rate-matched 44.1-kHz output amount is:

```text
576 * 735 / 367
= 1153.569482... output frames
```

The lower SND cursor is quantized in groups of two stereo frames.

Therefore a practical exact long-term correction at the proven lower unit boundary can alternate between:

```text
288 units = 1152 output frames
289 units = 1156 output frames
```

Across one complete 367-block phase:

```text
223 blocks * 288 units
144 blocks * 289 units
= 105840 lower units
```

which exactly equals the nominal 44.1-kHz drain over the corresponding 9.6 seconds:

```text
22050 lower units/s * 9.6 s = 211680 units
```

Stock uses 288 units for all 367 blocks:

```text
367 * 576 = 211392 units
```

hence the corrected deficit of 288 units per phase.

## If using native 22.05-kHz hardware output

Without x2 expansion, one 576-source-frame block is normally:

```text
576 frames = 288 lower units
```

The exact rate correction requires:

```text
576 * 735 / 734 = 576.784741... output frames
```

or:

```text
288.392370... lower units
```

Across 367 frontend blocks, exact correction is:

```text
295 blocks * 144 units
72 blocks  * 145 units
= 52920 lower units
```

which equals the nominal 22.05-kHz drain over the same source phase.

Thus native-rate playback does **not** remove the fixed-367 deficit by itself. It merely halves the data rate. A tiny fractional rate correction is still required for mathematically exact synchronization with the stock 60-Hz scheduler.

## Why this is valuable for CPS1

This separates two causes that were previously easy to conflate:

1. **gross conversion quality:** stock repeats every FBA source frame twice;
2. **small clock-rate mismatch:** fixed 367 at 60 Hz supplies 22020 rather than 22050 frames/s.

A better resampler can solve both in one controlled conversion stage:

```text
actual producer clock 22020
 -> rate conversion
 -> exact hardware clock 44100 or 22050
```

rather than treating the source as if it were already an exact 22050 stream.

## Important CPS timing caveat

The identified FB Alpha source family contains per-driver refresh rates, and CPS-family nominal video timing is not universally exactly 60 Hz.

XGO's frontend scheduler is nevertheless binary-proven to run the emulation loop on its 60-FPS 17/17/16-ms cadence.

This finding therefore targets **audio synchronization with the gameplay cadence XGO actually executes**.

Changing CPS emulation speed to nominal board timing would be a separate scheduler experiment and must not be bundled into the first audio test.

## Implementation-quality note

Simply duplicating one arbitrary sample at the correction interval would close the average rate but can introduce a small discontinuity.

A proper fractional linear/interpolating converter can distribute the correction smoothly while also replacing the stock zero-order hold.

Whether the CPU budget permits that converter in the heaviest CPS1 workloads must be measured; the arithmetic itself is now closed.

## Hardware gate

Not reached.
