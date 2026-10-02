# Native-rate latency policy is coupled to the stock 960 hardware count

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN + DERIVED DESIGN CONSTRAINT**

## Important coupling

A native 11025/22050 experiment cannot safely “rescale the 482 threshold” by simply changing the stock `sample_num` argument.

The stock configuration derives both pieces of state from the same value.

Normal setup receives:

```text
sample_num = 960
```

and stores:

```text
private +0x108 = sample_num
private +0x0FA = (sample_num >> 1) + 2
```

Therefore:

```text
960 -> admission threshold 482
```

But `+0x108` is also used by the lower SND hardware-count programming path.

So `sample_num` simultaneously participates in:

1. the software lower-queue admission threshold;
2. the hardware-facing SND count-register configuration.

## Native-rate time-depth arithmetic

With the existing 482-unit threshold:

```text
44100 Hz -> 43.7188 ms
22050 Hz -> 87.4376 ms
11025 Hz -> 174.8753 ms
```

To preserve approximately the current 43.72-ms queue time-depth, the ideal threshold would be roughly:

```text
22050 -> 241 cursor units
11025 -> 121 cursor units
```

The corresponding naive `sample_num` values from the stock formula would be approximately:

```text
threshold = (sample_num >> 1) + 2

241 -> sample_num ~= 478
121 -> sample_num ~= 238
```

But changing 960 to those values would also alter the hardware-facing count field.

That would make the experiment a combined queue-policy **and hardware-count** change.

## Consequence

A disciplined native-rate investigation has three distinct possibilities:

### A. Native rate, stock 960/count/threshold

Changes only rate selection and low-rate frame repetition.

Pros:

- cleanest first fidelity experiment;
- preserves stock hardware-count configuration.

Cons:

- lower admission threshold represents much more wall-clock audio at low rates.

### B. Native rate plus changed sample_num

Changes:

- hardware rate;
- conversion;
- lower admission threshold;
- hardware count.

This is too coupled for an initial diagnostic because any success/failure cannot be attributed cleanly.

### C. Decouple software admission threshold from sample_num

Keep the proven hardware-count value while deriving a separate time-normalized software threshold.

Architecturally cleaner for a later latency experiment, but requires an additional firmware change and therefore should be tested only after native-rate fidelity itself is proven.

## Why this matters

The stock 482 threshold is not an independent tuning constant in the current implementation.

Treating it as one would accidentally alter the still-not-fully-named hardware count semantics.

This prevents a tempting but poorly controlled “native rate + scaled 482” first candidate.

## Evidence levels

- 960 stored as sample_num: **BIN**
- threshold formula `(sample_num >> 1)+2`: **BIN**
- sample_num used by hardware count programming: **BIN**
- time-depth values and ideal threshold arithmetic: **derived**
- best future decoupling implementation: **OPEN/design**

## Hardware gate

Not reached.
