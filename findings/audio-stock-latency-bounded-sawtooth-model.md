# XGO stock audio latency model — bounded queue sawtooth by source rate

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN-DERIVED BOUNDED MODEL — NO HARDWARE CANDIDATE**

## Inputs now closed at BIN level

Frontend source ring:

```text
capacity: 4608 stereo S16 source frames
consumer admission: at least 576 source frames
consumer transfer quantum: 576 source frames
```

Low-rate conversion:

```text
11025 -> 44100: x4 whole-stereo-frame repetition
22050 -> 44100: x2 whole-stereo-frame repetition
44100/48000: no low-rate repetition helper
```

Lower SND:

```text
1 cursor unit = 16 bytes = 4 stereo S16 output frames
software commit cursor = SND +0x38
playback/consumption cursor used by queue arithmetic = SND +0x3A
queued = (+0x38 - +0x3A) mod 8208
admit next lower transfer iff queued < 482 units
```

## Resulting lower-queue sawtooth

The consumer submits one complete converted 576-source-frame block whenever lower backlog has fallen below 482 units.

Thus lower occupancy follows a source-dependent sawtooth rather than filling the 131,328-byte backing ring.

### 22.05-kHz FBA

One upper quantum represents:

```text
576 / 22050 = 26.122 ms
```

After x2 repetition:

```text
1152 output frames
288 lower units
26.122 ms at 44100
```

Admission occurs below:

```text
482 units = 43.719 ms
```

So an instantaneous admission near the threshold produces a lower queue near:

```text
481 + 288 = 769 units
3076 frames
69.751 ms
```

The hardware then drains it until it falls below 482 units, at which point another block may be accepted.

Ignoring the short software copy/commit interval, the stock FBA lower queue therefore cycles approximately over a 26.1-ms vertical range, with the admission boundary near 43.7 ms.

### 11.025-kHz SNES special path

One source quantum:

```text
576 / 11025 = 52.245 ms
```

After x4 repetition:

```text
2304 output frames
576 lower units
52.245 ms at 44100
```

Near-threshold post-submit upper bound:

```text
481 + 576 = 1057 units
4228 frames
95.873 ms
```

Thus SNES has a much larger lower-queue excursion because one converted block itself exceeds the 482-unit threshold.

### Native 44.1-kHz source

```text
576 frames = 144 units = 13.061 ms
post-submit bound = 625 units = 2500 frames = 56.689 ms
```

### Native 48-kHz source

```text
576 frames = 144 units = 12.000 ms
threshold = 1928 frames = 40.167 ms
post-submit bound = 2500 frames = 52.083 ms
```

## Why the 744-ms lower allocation is not normal latency

The lower backing store can represent 32,832 stereo frames, but the producer is throttled at a queued-distance threshold of only 1,928 frames.

Therefore normal stock operation is structurally prevented from simply filling the entire lower allocation under this path.

The large allocation is capacity/wrap storage, while the active backlog controller operates around the 482-unit threshold plus one accepted block.

## Frontend-ring contribution

The upper consumer waits until 576 source frames exist before forwarding a block.

This establishes a source-time batching quantum:

```text
11025: 52.245 ms
22050: 26.122 ms
44100: 13.061 ms
48000: 12.000 ms
```

However, this quantum must **not** simply be added wholesale to lower-queue depth as "latency."

A particular sample's wait in the 576-frame batch depends on where it lands in that batch:

- earliest sample can wait nearly one full source quantum before the block is released;
- latest sample waits almost none for batch completion.

Therefore the batching contribution ranges approximately from zero to one source quantum, before scheduler/task timing.

## Static lower+batch bounds

A conservative sample-path envelope can now be expressed without pretending it is a measured fixed delay.

For a sample at the earliest position of a just-started upper batch, using the largest arithmetic lower post-submit queue:

```text
FBA 22050:
  upper batch wait <= 26.122 ms
  lower queue bound <= 69.751 ms
  combined software-queue envelope <= 95.873 ms

SNES 11025:
  upper batch wait <= 52.245 ms
  lower queue bound <= 95.873 ms
  combined software-queue envelope <= 148.118 ms

native 44100:
  <= 13.061 + 56.689 = 69.750 ms

native 48000:
  <= 12.000 + 52.083 = 64.083 ms
```

These are conservative queueing envelopes, not measured end-to-end latency.

They exclude:

- core callback timing relative to emulation/input;
- task scheduling and `dly_tsk(1)` granularity;
- time consumed while memcpy/commit executes;
- SND/DAC internal pipeline;
- analog amplifier/speaker propagation.

They also combine maxima that need not occur simultaneously.

## Steady-state interpretation [BIN/INF]

Because the lower consumer is admitted only after backlog falls below the threshold and then adds a fixed block, steady occupancy is expected to oscillate around:

```text
threshold .. threshold + block
```

subject to cursor granularity and task scheduling.

The exact average occupancy cannot be promoted from static code alone. If the crossing phase were uniformly distributed, a midpoint estimate could be computed, but that would be a model assumption rather than recovered firmware behavior and is intentionally omitted.

## Family-source corroboration [UP]

The newer HC15xx `i2so_platform_device` structure explicitly contains:

```text
dma_buf
dma_size
wr
rd
avail
params
completion
```

This independently confirms that the family I2SO driver models playback as a DMA ring with distinct write/read positions and availability.

That source is later-family ancestry, not proof of field-for-field identity with XGO, but it strongly corroborates the semantic interpretation recovered directly from XGO instructions.

## Practical consequence for later experiments

The dominant stock queueing mechanism differs by source rate:

```text
SNES 11025:
large 52.245-ms batching/conversion block

FBA 22050:
26.122-ms batching/conversion block

native 44.1/48:
~12-13-ms block
```

Therefore changing only the lower SND threshold/period geometry cannot remove all SNES latency. The 576-source-frame upper quantum itself is a major independent contributor.

This is why any future latency experiments must keep:

1. upper consumer quantum;
2. lower backlog threshold;
3. source-rate/resampler policy

as separately controlled variables.

## Next static target

Close the update granularity of SND `+0x3A` and the old driver's interrupt cadence. That will tell us how far below 482 the queue can fall before software observes the crossing and therefore tighten the sawtooth bounds.

## Hardware gate

Not reached.
