# CPS1/FBA latency floor is constrained by once-per-video-frame audio delivery

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN/SRC + EXACT PHASE MODEL; DESIGN LEAD**

## Key limitation

The stock FBA libretro wrapper delivers audio only once per `retro_run()`:

```text
BurnDrvFrame()
...
video_cb(...)
audio_batch_cb(g_audio_buf, nBurnSoundLen)
```

XGO's embedded vendor build supplies 367 source frames per callback.

Therefore no frontend queue optimization can make newly generated FBA PCM arrive continuously throughout the video frame. The frontend sees one audio burst per emulated frame.

At XGO's 60-Hz scheduler, source delivery granularity is approximately:

```text
16.67 ms
```

This creates a practical latency/underrun floor independent of the 576-frame frontend consumer quantum.

## Stock 576-source-frame consumer

Exact callback-to-consumer residence already recovered:

```text
mean  = 0.7833787 video intervals ~= 13.06 ms at 60 Hz
max   = 2 intervals             ~= 33.33 ms
```

The lower queue then has to absorb the bursty submission cadence.

## Smaller-quantum exact models

The same phase calculation can be repeated without changing the core producer.

### 384-source-frame quantum

```text
mean frontend residence = 0.521798 intervals ~= 8.70 ms
max                     = 2 intervals
consumer submissions    ~= 57.34 / second
```

### 288-source-frame quantum

```text
mean frontend residence = 0.391008 intervals ~= 6.52 ms
max                     = 1 interval
consumer submissions    ~= 76.46 / second
```

### 192-source-frame quantum

```text
mean frontend residence = 0.260218 intervals ~= 4.34 ms
max                     = 1 interval
consumer submissions    ~= 114.69 / second
```

The latency benefit continues, but task/copy/submission frequency rises correspondingly.

## Lower-queue burst requirement with exact rate correction

Using the proven 60-Hz scheduler, the corrected two-frame cursor unit, and a rate-corrected 44.1-kHz stream, the minimum ideal initial lower backlog needed to bridge the deterministic burst schedule without emptying is approximately:

```text
frontend quantum   required lower backlog
576                957.2 units  ~= 43.41 ms
384                765.2 units  ~= 34.70 ms
288                669.2 units  ~= 30.35 ms
256                637.2 units  ~= 28.90 ms
192                573.2 units  ~= 26.00 ms
144                525.2 units  ~= 23.82 ms
96                 477.2 units  ~= 21.64 ms
72                 453.2 units  ~= 20.55 ms
```

This is an idealized continuous-drain model, not a measured hardware startup depth.

The important shape is robust: reducing the frontend quantum helps substantially at first, but the benefit asymptotically approaches a floor around one video-frame-scale producer cadence because FBA itself emits PCM only once per frame.

## Practical implication

Trying to drive the frontend quantum toward zero is not useful.

For CPS1, a moderate reduction such as 576 -> 384 or 288 is much more defensible than an extremely small quantum:

- meaningful reduction in batching residence;
- meaningful reduction in lower burst-backlog requirement;
- bounded increase in sound-task wakeups/copies;
- does not require modifying the FBA core's internal frame execution.

## CPU-load caution

CPS1 is exactly where CPU budget matters.

Approximate consumer-transfer frequency:

```text
576 quantum -> 38.23 transfers/s
384 quantum -> 57.34 transfers/s
288 quantum -> 76.46 transfers/s
192 quantum -> 114.69 transfers/s
```

A smaller quantum therefore trades latency for more RTOS wakeups, readiness checks, conversion calls and lower submissions.

That trade must be measured on heavy CPS1 workloads rather than optimized solely from latency arithmetic.

## Native-rate interaction

Native 22050 output halves the PCM expansion/copy bandwidth relative to the stock x2 44100 path.

That could recover enough CPU budget to make a moderately smaller frontend quantum practical.

However native rate and quantum reduction should first be tested separately so failures remain attributable.

## Bottom line

The current 576-frame batching is not the theoretical minimum, and CPS1 has credible room for a perceptible latency reduction.

But the core's once-per-frame audio delivery means software cannot make latency arbitrarily small without modifying the FBA core itself.

The sensible target is **stable, frame-scale audio latency**, not zero buffering.

## Hardware gate

Not reached.
