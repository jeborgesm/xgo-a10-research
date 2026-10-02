# XGO stock SNES NTSC frontend residence distribution — BIN-derived 183/576 model

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DETERMINISTIC MODEL FROM STOCK BIN GEOMETRY**

## Inputs

Stock SNES producer increment:

```text
P = 183 stereo source frames per normal NTSC emulated frame
```

Stock XGO frontend consumer:

```text
C = 576 stereo source frames per transfer
```

The consumer removes a complete 576-frame FIFO block whenever at least that many frames are available.

## Exact phase period

```text
gcd(183,576) = 3
phase cycle = 576 / 3 = 192 producer callbacks
```

Across one complete 192-callback phase cycle:

```text
183 * 192 = 35136 source frames
35136 / 576 = 61 complete consumer transfers
```

The ring residual returns exactly to zero at the cycle boundary.

## Sample residence after callback

Timestamping each source frame at the instant its stock core callback writes it into the XGO frontend ring, the complete deterministic phase cycle yields:

```text
consumed in same callback phase : 16.1458%
wait 1 later callback           : 31.7708%
wait 2 later callbacks          : 31.7708%
wait 3 later callbacks          : 20.0051%
wait 4 later callbacks          :  0.3074%
```

No sample requires five or more later producer callbacks in the idealized immediate-consumer model.

Mean:

```text
1.56557 video-frame intervals
```

Using the ~60.1-Hz SNES NTSC lineage refresh rate:

```text
mean frontend residence ~= 26.05 ms
phase maximum            ~= 66.56 ms
```

These are residence times **after the libretro callback reaches the frontend**. They do not include the time during which the emulated frame/APU generated the sample before callback.

## Comparison with maintained family model

The maintained family source's 183/184 fractional producer model gave approximately:

```text
mean ~= 26.08 ms
```

The exact stock integer model gives approximately:

```text
mean ~= 26.05 ms
```

So the earlier family model was numerically very close, but the stock mechanism is now correctly identified as fixed 183-frame packetization rather than fractional 183/184 callbacks.

## Important interpretation

The 576-frame consumer block represents:

```text
576 / 11025 = 52.245 ms
```

of nominal source PCM.

Yet the mean stock frontend residence is approximately half that value:

```text
~26.05 ms
```

This confirms from the actual stock producer geometry why adding the entire 52.245-ms quantum as a fixed latency term was too pessimistic.

## Lower-SND handoff

Each 576-frame stock SNES frontend transfer is subsequently expanded x4:

```text
576 @ 11025
 -> 2304 output frames @ 44100
 -> 576 lower cursor units
```

and admitted when lower queued distance is below 482 units.

Thus a realistic stock latency model must combine:

- frontend residence distribution: mean ~26.05 ms, phase-dependent 0..~66.56 ms after callback;
- lower-SND queue sawtooth: threshold 482 units plus one 576-unit accepted block;
- task scheduling/polling;
- DAC/internal hardware pipeline.

It must not simply add both independent maxima and label the result normal latency.

## OPEN

- exact PAL producer count and residence distribution;
- whether stock performs any long-term correction for truncating 11025/refresh to 183;
- correlation/phase locking between the 183/576 frontend cycle and the 576-unit lower queue cycle;
- measured input-to-speaker latency.

## Hardware gate

Not reached.
