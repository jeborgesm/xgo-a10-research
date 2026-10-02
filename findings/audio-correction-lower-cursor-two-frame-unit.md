# CORRECTION: lower SND cursor unit is two stereo frames, not four

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN + ALi SRC CROSS-CLOSURE — SUPERSEDES EARLIER 4-FRAME UNIT MODEL**

## Correction

Earlier lower-SND archaeology correctly established:

```text
cursor byte stride = 16 bytes
```

but incorrectly interpreted those 16 internal bytes as four ordinary packed stereo-S16 frames.

The legacy ALi PCM descriptor source plus direct XGO packing code now closes the internal representation.

> **One lower cursor unit represents TWO stereo S16 time frames, stored in a 16-byte internal hardware/DMA layout.**

The internal representation is therefore twice the byte size of ordinary packed stereo S16.

## Exact descriptor identity

Public ALi HLD:

```c
struct pcm_output {
    UINT32 ch_num;          // +0x00
    UINT32 ch_mod;          // +0x04
    UINT32 samp_num;        // +0x08
    UINT32 sample_rata_id;  // +0x0C
    UINT32 inmode;          // +0x10
    UINT32 *ch_left;        // +0x14
    UINT32 *ch_right;       // +0x18
    ...
};
```

XGO `0x802FDF54` uses those exact offsets.

For the frontend interleaved stereo buffer, +0x14 and +0x18 can point to the same packed source while the lower writer extracts the 16-bit halves.

## Direct XGO packing proof

In the generic two-channel write path, one lower cursor position at:

```text
lower_base + (cursor << 4)
```

receives four 32-bit stores at offsets:

```text
+0x00
+0x04
+0x08
+0x0C
```

The source advances by:

```text
s6 << 3
```

i.e. **8 source bytes per cursor position**.

Packed stereo S16 is four bytes per time frame.

Therefore:

```text
8 source bytes / 4 bytes per stereo frame = 2 stereo frames per cursor unit
```

The lower representation expands those two packed stereo frames into 16 internal bytes.

## Independent command-API confirmation

Public ALi command:

```text
SND_GET_SAMPLES_REMAIN = 0x31
```

matches the XGO 0x31 handler.

Its XGO helper doubles the lower queued-distance value before contributing it to the returned samples-remaining count:

```text
samples_from_lower_queue = queued_cursor_units * 2
```

That independently matches:

> **2 PCM sample frames per lower cursor unit.**

## Corrected core geometry

### Lower ring

```text
wrap modulus     = 8208 cursor units
frames/unit      = 2 stereo frames
PCM capacity     = 16416 stereo frames
```

Time capacity:

```text
44100 Hz -> 372.245 ms
48000 Hz -> 342.000 ms
```

These are capacities, not normal latency.

### Admission threshold

```text
threshold = 482 cursor units
          = 964 stereo frames
```

Time depth:

```text
44100 Hz -> 21.8594 ms
48000 Hz -> 20.0833 ms
22050 Hz -> 43.7188 ms
11025 Hz -> 87.4376 ms
```

## Corrected block sizes

### FBA stock 22050 -> x2 -> 44100

```text
576 source frames
1152 output frames
576 lower cursor units
26.122 ms represented audio
```

### SNES stock 11025 -> x4 -> 44100

```text
576 source frames
2304 output frames
1152 lower cursor units
52.245 ms represented audio
```

### Native 44100/48000 576-frame block

```text
576 output frames
288 lower cursor units
```

### Native FBA 22050 576-frame block

```text
576 output frames
288 lower cursor units
26.122 ms represented audio
```

## Corrected conservative post-submit bounds

With pre-submit maximum 481 units:

### FBA stock

```text
481 + 576 = 1057 units
2114 output frames
47.9365 ms @44100
```

### SNES stock

```text
481 + 1152 = 1633 units
3266 output frames
74.0590 ms @44100
```

### Native 44100

```text
481 + 288 = 769 units
1538 output frames
34.8753 ms
```

### Native 48000

```text
1538 / 48000 = 32.0417 ms
```

Again these are conservative arithmetic queue envelopes, not measured normal latency.

## 960 semantics narrowed substantially

Stock:

```text
sample_num = 960
threshold units = (960 >> 1) + 2 = 482
```

With two PCM frames per cursor unit:

```text
482 units = 964 PCM frames
```

So the admission threshold corresponds almost exactly to one `sample_num` of PCM plus four frames.

This is strong evidence that the legacy `sample_num` argument is genuinely a PCM sample-frame/count quantity rather than an unrelated opaque period number.

Its exact hardware-register wording remains vendor-specific, but the software unit relationship is now much clearer.

## What this changes and what it does not

Changes:

- every prior lower cursor-unit -> PCM-frame conversion using factor 4 must use factor 2;
- unit-per-second deficits double numerically;
- lower ring capacity in milliseconds halves;
- 482 threshold time-depth halves;
- conservative lower queue bounds shrink.

Does **not** change:

- source/output sample rates;
- 576 frontend quantum;
- represented duration of a FBA/SNES PCM block;
- exact fixed-367 and fixed-183 producer deficits in frames/second;
- native-rate support;
- the qualitative conclusion that smaller frontend batching can reduce latency.

## Repository cleanup requirement

All findings that used the old four-frame cursor interpretation must be treated as superseded until their arithmetic is updated.

This correction is authoritative for subsequent audio work.
