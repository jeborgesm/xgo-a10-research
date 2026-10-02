# Stock FBA has a smaller fixed-integer audio-rate mismatch too

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN/SRC + EXACT ARITHMETIC; EMPTY-GAP MODEL CONDITIONAL**

## Discovery

The fixed-integer rate-accuracy problem is not unique to the built-in SNES path.

Stock FBA uses:

```text
source rate = 22050 Hz
audio producer batch = 367 source frames per emulated video frame
stock XGO NTSC scheduler = 60 frames/s
```

Therefore actual source PCM offered per second is:

```text
367 * 60 = 22020 source frames/s
```

while the sound path is configured as:

```text
22050 source frames/s
```

Deficit:

```text
22050 - 22020 = 30 source frames/s
30 / 22050 = 0.136054%
```

After stock x2 zero-order-hold conversion:

```text
22020 * 2 = 44040 output frames/s supplied
hardware-facing drain = 44100 output frames/s
deficit = 60 output frames/s
```

or:

```text
15 lower cursor units/s
```

because one lower cursor unit represents four stereo output frames.

## Break-even scheduler cadence

Fixed 367 would exactly represent 22050 Hz only at:

```text
22050 / 367 = 60.081743869... frames/s
```

The stock scheduler is 60 FPS, so scheduler cadence does not compensate for the fixed integer producer.

## Relationship to FBA2012 lineage

The maintained/public FBA2012 lineage uses a fixed sound-segment length corresponding to the same 367-frame stock-family contract.

Thus this is not a frontend batching artifact.

The XGO frontend receives the fixed producer count, aggregates it into 576-frame blocks, and the x2 converter duplicates the supplied frames without restoring the missing fractional production.

## Exact 367/576 source phase

Already closed:

```text
P = 367
C = 576
gcd(P,C) = 1
phase cycle = 576 emulated frames
duration at 60 FPS = 9.6 s
consumer transfers = 367
```

Across one complete cyclic phase, inter-transfer callback gaps are:

```text
158 gaps of 1 emulated frame
209 gaps of 2 emulated frames
total = 367 gaps
```

## Long-term lower deficit over one phase cycle

PCM supplied:

```text
211392 source frames
x2 -> 422784 output frames
     -> 105696 lower cursor units
```

Nominal 44.1-kHz drain over 9.6 s:

```text
44100 * 9.6 = 423360 output frames
               105840 lower cursor units
```

Deficit:

```text
144 lower cursor units per 9.6-s phase cycle
= 15 units/s
```

Again this exactly matches the per-second arithmetic.

## Conditional empty-gap model

Using the hardware-clamp model constrained by the recovered commit/playback cursor contract:

```text
playback +0x3A drains toward commit +0x38
at empty, hardware does not allow playback to run past commit
new commit later resumes consumption
```

and assuming immediate resume plus no extra scheduler delay, deterministic simulation reaches empty in a subset of the two-frame source gaps.

In steady phase:

```text
31 short empty intervals per 9.6 s
total empty time = 13.06122449 ms
individual intervals roughly 0.143 .. 1.143 ms
```

The total again equals the missing lower PCM:

```text
144 units / 11025 units/s = 13.06122449 ms
```

This is a **conditional hardware-behavior model**, not a measured speaker waveform.

## Comparison with SNES

### FBA

```text
rate deficit      0.136%
conditional gaps  31 / 9.6 s
gap scale         sub-ms to ~1.14 ms
```

### SNES

```text
rate deficit      0.408%
conditional gaps  9 / 3.2 s
gap scale         ~0.29 to ~3.53 ms
```

SNES therefore has the larger fixed-integer mismatch and longer individual depletion intervals under the same clamp model.

## Relevance to observed Arcade audio

This supplies a plausible mechanism that could contribute to rough/choppy Arcade audio, especially when combined with:

- x2 zero-order-hold conversion;
- frontend 576-frame batching;
- scheduler load;
- underrun-fade behavior.

It does **not** establish that the 0.136% mismatch is the dominant cause of any particular game's audible problem.

## Fidelity-design implication

Rate accuracy should now be treated as a general fixed-integer-producer lane, not a SNES-only curiosity.

Potential future fixes differ by core:

- SNES family source already demonstrates fractional accumulation;
- FBA needs its own producer-rate reconciliation strategy.

Do not silently fix producer cadence while evaluating only resampler quality, or the experiment will change two fidelity mechanisms at once.

## Hardware gate

Not reached.
