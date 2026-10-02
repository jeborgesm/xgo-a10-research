# Stock SNES cadence proves fixed-183 long-term rate mismatch

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN + EXACT ARITHMETIC — MISMATCH CLOSED**

## Question

Could stock XGO's actual emulator pacing compensate for the built-in SNES core producing a fixed 183 source frames per normal NTSC emulated frame?

The break-even cadence would be:

```text
11025 / 183 = 60.24590163934426 Hz
```

If XGO paced SNES at that rate, fixed 183 would produce exactly 11025 source frames/s.

## Stock scheduler cadence [BIN]

Existing direct disassembly of `run_emulator @ 0x8035ED48` already closed the XGO NTSC pacing state:

```text
target_fps @ 0x80C2D128 = 60
active integer frame period @ 0x80C2D118
NTSC cadence = 17 ms, 17 ms, 16 ms
```

The local modulo-3 counter implements:

```text
17 + 17 + 16 = 50 ms for 3 frames
```

which is exactly:

```text
3 / 0.050 = 60.000 frames/s
```

at the scheduler's integer timing model.

The family-0x08 SNES special runtime still enters this common `run_emulator` pacing machinery after its special 11025-Hz sound initialization. No separate 60.2459-Hz SNES pacing path has been recovered.

## Production rate [BIN + arithmetic]

With:

```text
183 source frames / emulated frame
60 emulated frames / second
```

stock production is:

```text
183 * 60 = 10,980 source frames/s
```

Nominal source rate supplied to the sound path is:

```text
11,025 frames/s
```

Deficit:

```text
11025 - 10980 = 45 source frames/s
45 / 11025 = 0.00408163265 = 0.408163%
```

After the exact x4 zero-order-hold converter:

```text
10980 * 4 = 43,920 output frames/s produced
hardware-facing nominal drain = 44,100 frames/s
deficit = 180 output frames/s
```

The proportional deficit remains 0.408163%.

## Correction to earlier approximate estimate

An earlier note used a Snes9x2005-lineage refresh approximation near 60.1 Hz and obtained a ~0.24% mismatch.

That estimate is superseded for the **stock XGO scheduler** by the binary-proven 60-FPS 17/17/16 pacing model.

The relevant baseline mismatch is therefore approximately **0.408%**, not 0.24%.

## What is now closed

The previously considered downstream compensation possibilities have already been excluded:

- callback count stays fixed at 183;
- frontend 576-frame batching does not create source frames;
- x4 conversion repeats each source frame exactly four times;
- lower queue admission changes timing/occupancy but not frame count.

This pass excludes scheduler cadence as compensation too.

Therefore the stock XGO software path has a genuine nominal-rate mismatch:

```text
SNES PCM production equivalent: 43,920 output frames/s
configured SND clock:           44,100 output frames/s
```

[BIN + arithmetic]

## What this does and does not prove

It proves a long-term producer/drain mismatch in the recovered software contract.

It does **not yet prove**:

- a measured 0.408% pitch shift at the speaker;
- the exact audible symptom;
- how often the lower queue reaches underrun;
- whether SND underrun fade masks the resulting depletion;
- whether emulator CPU/audio synthesis itself is perceptually clocked in a way that changes the interpretation of pitch.

Those require further queue/driver or hardware correlation.

## Queue depletion scale

The mismatch is:

```text
180 output frames/s
```

At 44.1 kHz, that is 90 lower-SND cursor units per second because one cursor unit represents two stereo output frames.

For a lower queued depth Q cursor units, the mismatch alone would reduce that depth at approximately:

```text
90 units/s
```

unless burst submission/phase behavior replenishes it.

Examples purely as depletion arithmetic:

```text
482-unit admission-threshold depth / 90 ~= 5.36 s
1152-unit SNES converted block / 90     ~= 12.80 s
```

These are **not** predicted underrun intervals, because the queue is continuously refilled in bursts and its actual phase/starting occupancy matters.

They show only that the mismatch is large enough to matter over seconds rather than hours.

## Fidelity-design implication

There are now two separable SNES fidelity issues:

1. **conversion quality** — each 11.025-kHz frame is repeated four times;
2. **rate accuracy** — fixed 183-at-60 production corresponds to 10.980 kHz, while the driver is told 11.025 kHz and drains at nominal 44.1 kHz after x4 conversion.

A future quality experiment should avoid accidentally fixing both at once unless the test is explicitly designed to measure both.

Potential software strategies to evaluate later include:

- restore fractional source-frame accumulation like maintained family Snes9x2005;
- derive a conversion ratio from the actual production cadence;
- or otherwise reconcile producer and hardware clocks.

No strategy is selected yet.

## Next target

Model the exact SNES lower-queue burst recurrence:

```text
183 source frames/callback
frontend transfer whenever >=576
each 576 source transfer -> 1152 lower cursor units after x4
hardware drains 22050 lower cursor units/s at 44.1k / 2 frames per unit
```

Combine the deterministic 183/576 frontend phase with lower drain to determine the queue's long-term sawtooth and whether the 0.408% deficit necessarily creates periodic lower underrun/restart behavior.

## Hardware gate

Not reached.
