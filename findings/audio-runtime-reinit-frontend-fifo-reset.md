# Runtime sound reinit resets the frontend PCM FIFO to empty

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **DIRECT STOCK BIN — REENTRY QUEUE BEHAVIOR CLOSED AT FRONTEND LAYER**

## Scope

This follows the runtime sound-reinitialization call at `0x8035F0C4` into the already recovered stock sound initializer `0x8035C998`.

The previous finding established that this reinit is not locally bracketed by the XGO L23 hardware mute/gate.

## Reinit enters the full stock sound initializer [BIN]

Runtime path:

```text
0x8035F0C0  move a0,zero
0x8035F0C4  jal  0x8035C998
0x8035F0C8  li   a2,2
```

Thus this is not merely a scheduler reset. It executes the same stock sound initialization function used by normal emulator startup.

## Frontend ring state [BIN]

Using stock GP `0x80C34774`, the relevant GP-relative stores in `0x8035C998` decode as:

```text
GP + 0xA0C8 = 0x80C2E83C  ring base
GP + 0xA0E0 = 0x80C2E854  producer byte offset
GP + 0xA0E4 = 0x80C2E858  consumer byte offset
GP + 0xA0E8 = 0x80C2E85C  ring capacity
GP + 0xA0EC = 0x80C2E860  consumer quantum
```

The initializer performs:

```text
0x8035CAC0  sw zero,0xA0E0(gp)   producer = 0
...
0x8035CACC  sw zero,0xA0E4(gp)   consumer = 0
...
0x8035CAD4  li t4,0x4800
0x8035CADC  sw t4,0xA0E8(gp)    capacity = 0x4800
...
0x8035CAE4  li a1,0x240          quantum = 576
...
0x8035CB0C  sw a1,0xA0EC(gp)
```

Therefore every execution of this initializer resets the logical frontend PCM FIFO to:

```text
producer = consumer = 0
```

[BIN]

## Existing allocation is reused [BIN]

The initializer checks the existing ring-base global.

If no ring exists it allocates `0x4800` bytes and stores the new base.

If a ring already exists, the allocation path is skipped.

Therefore runtime reinit normally reuses the existing PCM memory while resetting its logical producer/consumer positions.

The old PCM bytes do not need to be erased: with producer and consumer equal, they are outside the logical queue and cannot be consumed until overwritten by newly produced PCM.

## Consequence: queued frontend audio is discarded

If the frontend FIFO contained unconsumed PCM immediately before runtime reinit, resetting both offsets to zero discards that queued logical audio.

This gives a concrete reentry behavior:

```text
old queued frontend PCM
       ↓
sound reinit
       ↓
producer = 0
consumer = 0
       ↓
frontend queue is logically empty
       ↓
new core PCM must accumulate to >=576 frames again
```

For stock SNES at 183 frames per normal NTSC callback, that means playback cannot submit a fresh frontend block until enough post-reinit callbacks rebuild the 576-frame threshold.

This is a potential gap/discontinuity source independent of the lower SND queue.

## Noise interaction

The same runtime reinit is not locally protected by L23.

Thus stock can perform:

```text
speaker gate remains open
        ↓
discard frontend queued PCM
        ↓
wait for new PCM to rebuild 576-frame threshold
        ↓
resume lower submission
```

Whether that gap becomes silence, underrun fade, held DAC data, or an audible transient depends on the lower SND queue and DAC behavior.

That lower-layer behavior remains the next target.

## Important distinction

This result does **not** mean stale bytes from the reused frontend allocation are replayed.

The logical FIFO is emptied by pointer reset.

Any audible stale/held value would have to arise downstream — in the lower SND/DMA/DAC state — not from the old frontend ring bytes.

## Latency/reentry implication

After reinit, the frontend batching delay effectively restarts from an empty phase.

For SNES this is especially significant because the consumer quantum represents 52.245 ms of source PCM and normal stock callbacks contribute only 183 frames at a time.

This does not change steady-state mean latency, but it can lengthen the first post-reinit audio restart compared with a steady-state phase that already had residual occupancy.

## Next target

Trace what the same initializer's device-control calls do to:

- lower SND commit cursor;
- hardware playback cursor;
- lower queue contents;
- underrun-fade state;
- start/stop state.

The key question is now precise:

> when the upper FIFO is forcibly emptied while L23 stays open, does the lower SND path continue draining old audio, fade an underrun, hold a last sample, or reset immediately?

## Hardware gate

Not reached.
