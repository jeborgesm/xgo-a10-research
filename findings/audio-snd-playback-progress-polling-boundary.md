# XGO lower-SND +0x3A progress granularity — static boundary and tightened latency interpretation

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN + UPSTREAM BOUNDARY — NO HARDWARE CANDIDATE**

## Question

After closing:

```text
queued = (SND+0x38 software commit - SND+0x3A playback progress) mod 8208
admit next transfer iff queued < 482
```

the next question was whether software/interrupt cadence updates `+0x3A` in coarse period-sized jumps or whether it is a live SND progress register.

## XGO software-side result [BIN]

The XGO admission path does not wait for, consume, or update a software shadow of the playback cursor.

Each readiness test calls the low-level `+0x3A` reader again and recomputes queue depth from the current SND register value.

The upper consumer's wait behavior is:

```text
readiness false
 -> dly_tsk(1)
 -> retry
 -> reread SND cursor
```

Therefore the **software observation cadence** of the threshold crossing is bounded by the one-tick retry loop plus task scheduling.

No XGO software period counter is interposed in this admission path.

## Family-source corroboration [UP]

The recovered later HC15xx I2SO device model contains explicit:

```text
dma_buf
dma_size
wr
rd
avail
completion
```

and the generic sound core calls platform `get_avail()` at transfer/poll time.

This is consistent with a driver reading/maintaining live DMA-ring progress rather than exposing only an eight-period interrupt count.

However, the concrete proprietary I2SO platform implementation that maps old XGO SND `+0x3A` to a named hardware field is not present in the recovered source.

## What can and cannot be claimed

### Closed

- XGO software commits the producer boundary to SND `+0x38`.
- XGO rereads SND `+0x3A` on every readiness retry.
- queue depth is recomputed from those values.
- admission threshold is 482 units.
- when blocked, software polls again after `dly_tsk(1)`.

### Still OPEN

- physical increment quantum of the SND `+0x3A` register;
- whether it increments per DMA beat, burst, sample group, or internal period;
- whether an interrupt also fires at coarser period boundaries;
- exact duration of one RTOS tick in the active stock configuration if not independently closed elsewhere.

Therefore we must not invent a "960-frame interrupt granularity" for `+0x3A`.

## Tightened latency interpretation

The lower queue does **not** need to wait for a whole software-visible period interrupt before becoming admissible, based on the traced readiness path.

Instead, once the live/maintained `+0x3A` value makes:

```text
queued < 482
```

true, the consumer can discover that on its next one-tick polling retry.

Thus the previous sawtooth bounds do not require adding another assumed 960-frame interrupt delay.

Any overshoot below the 482 boundary comes from:

1. the physical update granularity of `+0x3A`;
2. the RTOS polling/scheduling interval;
3. hardware playback occurring while software executes the test/copy/commit.

Only item 1 remains opaque at the register level.

## Why the SND interrupt is not required to close admission behavior

The HC15xx family has a dedicated SND interrupt, and later APIs expose underrun/completion events.

But XGO's normal producer-unblock path is polling-based. Therefore identifying the interrupt handler remains useful for underrun and period-event archaeology, but it is **not required** to explain how normal queue admission resumes.

This narrows the critical path for latency work.

## Consequence

The first evidence-backed stock latency model can stand without assigning an interrupt-period penalty.

The remaining uncertainty in normal lower-queue latency is now sub-threshold crossing granularity/scheduling, not hundreds of milliseconds of hidden buffering.

## Next target

Shift the latency archaeology upward to the frontend ring:

- determine typical producer write sizes emitted by each core;
- determine whether the 576-frame consumer quantum is normally accumulated in one callback or across callbacks;
- identify callback phase relative to frame execution.

This can tighten the actual sample-age distribution much more than further speculation about the large lower backing ring.

In parallel, inspect the SND interrupt path specifically for underrun/fade behavior, not as a prerequisite for normal admission.

## Hardware gate

Not reached.
