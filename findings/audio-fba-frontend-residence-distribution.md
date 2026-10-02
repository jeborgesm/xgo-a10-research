# Idealized FBA frontend residence distribution from the 367/576 cadence

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DERIVED FROM CLOSED CONSTANTS — SCHEDULER JITTER EXCLUDED**

## Model

Use the recovered stock-family FBA producer cadence:

```text
P = 367 source frames per emulated-frame audio callback
rate = 22050 Hz
```

and XGO BIN-proven frontend consumer quantum:

```text
C = 576 source frames
```

Assume:

- each FBA callback appends its 367-frame block atomically for timing classification;
- consumer removes a 576-frame block as soon as occupancy permits;
- no task scheduling delay beyond the callback phase;
- start from an empty ring.

Because `gcd(367,576)=1`, 576 producer callbacks cover the complete residual phase cycle.

## Exact phase-cycle result

Across the complete idealized 576-callback cycle, every produced source frame is eventually consumed.

Classifying each sample by the number of **later FBA callbacks** it must survive before its 576-frame consumer block is released gives:

```text
0 callback intervals: 31.9444%
1 callback interval : 57.7732%
2 callback intervals: 10.2823%
```

No sample requires three later producer callbacks in this idealized phase model.

One FBA callback's represented audio duration is:

```text
367 / 22050 = 16.644 ms
```

Thus the callback-phase residence classes are approximately:

```text
0 intervals: ~0 ms phase wait
1 interval : ~16.64 ms
2 intervals: ~33.29 ms
```

The mean callback-phase wait is:

```text
0.78338 callback intervals
= ~13.04 ms
```

## Interpretation limits

This is **not** a measured wall-clock latency distribution.

It intentionally quantizes production at callback boundaries. Samples are generated throughout emulation of the frame, while the libretro core exposes the completed audio buffer at its callback.

Therefore the calculation answers:

> after a completed FBA audio callback has handed its block to the XGO frontend, how many later FBA callback phases are needed before each sample's 576-frame consumer block can be formed?

It does not include:

- sample generation time within the emulated frame;
- XGO audio-consumer task scheduling;
- lower-SND backlog;
- DAC/analog delay.

## Important correction to intuition

The frontend's 576-frame quantum represents 26.122 ms of PCM, but **typical FBA samples do not wait 26.122 ms after arrival at the frontend**.

Under the deterministic 367/576 phase model, the mean post-callback frontend residence is only about 13.04 ms, and ~89.7% of samples are consumed by the same or next FBA callback phase.

This is a much tighter and more realistic static description than treating 26.122 ms as a fixed frontend delay.

## Lower queue remains separate

The lower SND block generated from each 576-source-frame consumer transfer remains:

```text
288 cursor units
26.122 ms represented output audio
```

and admission occurs when lower queued audio is below 482 units.

The frontend mean residence cannot simply be added to a guessed lower mean because the two phase systems can couple through blocking. A joint deterministic model requires the hardware playback rate and scheduler timing.

## Next target

Recover the stock SNES producer callback size/cadence. If it is one frame-sized 11.025-kHz block, the same phase-cycle method can quantify how much of SNES's apparent 52.245-ms consumer quantum is real frontend residence versus merely transfer size.

## Hardware gate

Not reached.
