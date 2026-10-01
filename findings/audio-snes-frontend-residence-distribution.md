# Family Snes9x2005 frontend residence distribution against XGO 576-frame consumer

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DETERMINISTIC MODEL FROM PINNED SRC + XGO BIN**

## Model

Pinned family Snes9x2005 produces one callback per video frame at 11025 Hz using a fractional sample accumulator.

XGO consumes exactly 576 source frames whenever the frontend ring has at least that amount.

A long-run deterministic simulation of the source accumulator plus FIFO consumer threshold was used. Samples are timestamped at the instant their per-frame libretro audio callback reaches the frontend; therefore these numbers describe **frontend residence after callback**, not APU-generation age inside the emulated frame.

## NTSC (~60.0988 Hz)

Producer mean:

```text
11025 / 60.0988 = 183.4479 frames/callback
```

The callback sequence is principally 183/184 frames.

Long-run sample residence in callback intervals:

```text
0 later callbacks : ~16.01%
1 later callback  : ~31.85%
2 later callbacks : ~31.85%
3 later callbacks : ~19.99%
4 later callbacks : ~0.30%
```

Mean:

```text
1.5672 video-frame intervals
~26.08 ms
```

Observed deterministic phase maximum in the modeled sequence:

```text
4 intervals
~66.56 ms
```

The rare four-interval case comes from fractional callback sizing/residual phase; it is not evidence of scheduler stall.

## PAL (~50.007 Hz)

Producer mean:

```text
~220.469 frames/callback
```

Residence distribution:

```text
0 later callbacks : ~19.23%
1 later callback  : ~38.28%
2 later callbacks : ~35.37%
3 later callbacks : ~7.13%
```

Mean:

```text
1.3040 PAL-frame intervals
~26.08 ms
```

Maximum in the deterministic phase model:

```text
3 intervals
~59.99 ms
```

## Important invariant

NTSC and PAL produce nearly the same mean post-callback residence in milliseconds despite different callback frame rates.

That is expected from the common audio-rate/576-frame batching geometry: the producer changes callback packetization, while the consumer's source-time quantum remains:

```text
576 / 11025 = 52.245 ms
```

For an asynchronous FIFO blockizer with phase distributed across the block, a mean residence near half a block duration is structurally plausible:

```text
~26.12 ms
```

The modeled ~26.08 ms result closely approaches that value.

## Contrast with FBA

FBA 22050 / 367-per-frame against the same 576-frame consumer produced an idealized mean frontend residence around 13 ms.

SNES 11025 produces approximately half as many source samples per unit wall time, so the same 576-source-frame frontend quantum approximately doubles the mean residence:

```text
FBA frontend mean  ~13 ms
SNES frontend mean ~26 ms
```

This is now a much better explanation of SNES's latency disadvantage than treating every sample as waiting a full 52.245-ms block.

## Evidence boundary

These residence numbers are exact for the stated deterministic model using the pinned family Snes9x2005 source cadence plus XGO's BIN-proven 576-frame FIFO consumer.

They become a model of XGO built-in SNES only if its producer callback cadence is independently shown to match.

## Next target

Search the XGO built-in SNES/core binary for the audio callback callsite and recover its actual `frames` argument. If it matches the family ~183/184-per-frame cadence, this residence model can be promoted from family-model evidence to the stock XGO path.

## Hardware gate

Not reached.
