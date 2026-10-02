# Lower SND service task is event-flag driven

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN STRUCTURAL IDENTIFICATION; LEGACY SYMBOL NAMES OPEN**

## Caller context

The lower transfer-service state machine `0x80301618` is reached from the task/service loop around `0x80302Dxx..0x80302Fxx`.

That caller exposes a clear event-flag synchronization contract.

## Three synchronization primitives [BIN]

The loop repeatedly uses three helpers:

```text
0x802E0274
0x802E03AC
0x802E0448
```

Their argument patterns distinguish their roles structurally.

### 0x802E0448 — wait/receive event flags

Calls supply:

```text
a0 = pointer to output/received flag word
a1 = 16-bit object event handle from +0x130
a2 = requested mask
a3 = mode value 2
stack arg = timeout
```

Observed masks/timeouts include:

```text
mask 0x0004
mask 0x8000 with timeout 0x1388
mask 0x0001 with timeout -1
mask 0x10006 with timeout 0x64
```

This is structurally an event-flag wait/receive primitive.

### 0x802E03AC — signal/set event flags

Calls use:

```text
a0 = event handle from +0x130
a1 = event bit/mask
```

Observed masks include:

```text
0x0001
0x0004
0x8000
0x10000
```

This is structurally the matching signal/set operation.

### 0x802E0274 — complementary event-control operation

Calls also use the same event handle plus a bit mask such as:

```text
0x0100
0x0400
```

It is a complementary event-flag control operation, likely clear/configure semantics, but its exact legacy SDK name remains OPEN.

## Transfer-service event path [BIN]

The normal lower-service route eventually performs:

```text
wait/receive event flags
       ↓
inspect returned bits
       ↓
signal/acknowledge selected bits
       ↓
call 0x80301618(active_sound_object)
       ↓
loop while service reports active work
```

Therefore `0x80301618` is not a polling-only queue calculator. It is driven by lower transport events.

This materially narrows the search for hardware cursor advancement and empty/underrun handling.

## Important event mask near transfer service

Immediately before the `0x80301618` service call, the loop waits using:

```text
a2 = 0x00010006
timeout = 0x64
```

After wakeup it examines at least bits:

```text
0x0002
0x0004
0x10000
```

and signals/acknowledges corresponding event state before entering the transfer service.

Exact symbolic meanings of these bits are not yet proven.

Do not label `0x10000` as UNDERRUN solely from modern-family terminology.

## Relevance to +0x3A / empty-state recovery

The lower queue's hardware playback cursor is read directly from SND +0x3A by the queued-distance path.

The service task is event-driven and its state machine owns the lower fragment/cursor fields.

The most plausible architecture now is:

```text
SND/DMA event
   ↓
legacy event flag
   ↓
lower service task
   ↓
0x80301618 state-machine update
   ↓
fragment/cursor bookkeeping
```

The final mapping from each event bit to DMA completion, empty, underrun or other hardware condition remains OPEN.

## Next target

Trace producers of event bits `0x2`, `0x4` and `0x10000` back toward interrupt/callback registration and SND register handling.

That route is more direct than trying to infer empty behavior from queue-query functions.

## Hardware gate

Not reached.
