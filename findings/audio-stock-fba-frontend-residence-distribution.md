# Stock FBA frontend residence distribution — exact 367/576 phase model

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN/SRC-GROUNDED ARITHMETIC MODEL**

## Inputs already closed

Stock FBA path:

```text
source rate              22050 Hz
producer callback        367 stereo frames per emulated video frame
frontend consumer block  576 source frames
```

The producer cadence is one audio batch per `retro_run()` / emulated frame.

This note computes the deterministic batching residence correctly; it supersedes any earlier unverified detailed FBA residence calculation.

## Exact phase cycle

```text
P = 367
C = 576
gcd(P,C) = 1
```

Therefore the frontend phase returns after 576 producer callbacks.

Across that cycle:

```text
367 * 576 = 211392 source frames
211392 / 576 = 367 exact consumer transfers
```

The residual returns to zero.

## Residence definition

For every source PCM frame, record the producer callback at which it enters the frontend FIFO and the callback at which the 576-frame consumer transfer containing it becomes eligible.

Residence is expressed as number of later FBA callback/video-frame intervals.

Exact counts over one complete phase cycle:

```text
same callback / +0 intervals :  67,528 frames
+1 callback interval         : 122,128 frames
+2 callback intervals        :  21,736 frames
total                         : 211,392 frames
```

Percentages:

```text
0 intervals : 31.944%
1 interval  : 57.773%
2 intervals : 10.282%
```

Mean:

```text
0.7833787466 video-frame intervals
```

Maximum:

```text
2 video-frame intervals
```

## Approximate wall-clock scale

Using the stock FBA cadence of approximately 59.94 Hz:

```text
one video interval  ~= 16.683 ms
mean residence      ~= 13.07 ms
phase maximum       ~= 33.37 ms
```

These are frontend-batching residence values measured from arrival at the libretro batch callback to eligibility of the 576-frame frontend transfer.

They do **not** include:

- time between audio generation within the emulated frame and callback arrival;
- lower SND queue residence;
- DAC/analog delay;
- controller/input scheduling.

## Important correction to intuitive 576-frame arithmetic

A 576-frame source block at 22050 represents:

```text
26.122 ms
```

but that does **not** mean every FBA sample waits 26.122 ms in the frontend FIFO.

Because 367 frames arrive every video callback, transfers cut across producer batches. The exact mean batching residence is only about 13.07 ms, with a phase maximum about 33.37 ms.

This is why the consumer-block duration must not be directly added as a fixed latency term.

## Comparison with stock SNES

Stock NTSC SNES:

```text
producer increment 183
consumer            576
mean frontend residence ~26.05 ms
phase max               ~66.56 ms
```

Stock FBA:

```text
producer increment 367
consumer            576
mean frontend residence ~13.07 ms
phase max               ~33.37 ms
```

Thus the same 576-frame frontend quantum imposes substantially more batching residence on the low-rate SNES path because its producer contributes fewer source frames per video callback.

## Latency-improvement implication

Reducing the frontend quantum remains a real latency lever, especially for SNES.

However, the correct baseline is now the phase distribution above, not one full 576-frame block duration per sample.

Any future candidate must keep this lane separate from:

- resampler changes;
- lower-SND backlog changes;
- stereo-to-mono fold;
- L23/noise sequencing.

## Hardware gate

Not reached.
