# Reinit L23 unmute cannot synchronously wait for PCM priming in run_emulator

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN/ARCHITECTURE CONSTRAINT — DESIGN LEAD ONLY**

## Problem

The runtime-reinit noise lane now has a strong candidate shape:

```text
mute L23
 -> stock lower reconfiguration/reset
 -> frontend reset
 -> fresh PCM reaches lower SND
 -> unmute L23
```

The remaining question is where “fresh PCM reaches lower SND” can safely be detected.

## Critical lifecycle constraint

The runtime reinit occurs inside the emulator/frontend execution path.

After reinit, fresh PCM is produced only when normal emulation continues and cores invoke their audio callbacks.

Therefore the run-emulator thread cannot safely do:

```text
sound_init()
while lower_queue_empty:
    dly_tsk(1)
L23_unmute()
```

because fresh core PCM may depend on that same execution path returning to `retro_run()`.

For SNES in particular, the frontend needs four post-reset 183-frame callbacks before the first 576-frame consumer transfer is possible.

A synchronous wait immediately after `sound_init` risks waiting for data whose producer cannot run yet.

## Correct priming boundary

The first unquestionably useful event is not “sound_init returned” and not “10 ms elapsed.”

It is:

> the first successful post-reset frontend-consumer submission into the lower SND path.

The recovered path is:

```text
core callback
 -> frontend producer ring
 -> >=576 source frames
 -> consumer task
 -> 0x8035C4A8
 -> object +0x70 / 0x802FDF54
 -> lower PCM conversion/submission
 -> lower commit advances
```

That path executes asynchronously in the sound consumer task once enough fresh source PCM exists.

## Design implication

If a future noise-only experiment mutes L23 around runtime reinit, the clean evidence-based reopen mechanism is likely a one-shot **post-reinit pending-unmute flag** consumed at or immediately after the first successful lower submission.

Conceptually:

```text
runtime reinit:
    L23 mute
    pending_audio_unmute = 1
    perform stock sound_init
    return to emulation

sound consumer:
    submit first fresh lower block
    if pending_audio_unmute:
        L23 unmute
        pending_audio_unmute = 0
```

This is a design lead, not a patch candidate.

## Why lower readiness alone is insufficient

The lower readiness callback returns true when:

```text
queued < 482
```

An empty queue has:

```text
queued = 0
```

and is therefore “ready.”

So readiness means **space/admission available**, not **audio primed**.

It cannot be used as the unmute condition by itself.

## Why fixed delay is inferior

The stock path already contains an explicit 10-ms reconfiguration delay, but post-reset source refill is core-dependent:

```text
FBA: 367 + 367 -> first 576 transfer on second callback
SNES: 183 + 183 + 183 + 183 -> first transfer on fourth callback
```

No single additional fixed delay cleanly represents both.

A first-successful-submission event naturally adapts to the producer.

## External-route caution

L23 is currently proven only as the known audio gate used by the physical-volume path.

Exact external/AV analog topology remains OPEN.

Any eventual gating experiment must verify that L23 manipulation does not undesirably mute or disturb an external audio route.

## Hardware gate

Still not reached. This note identifies the safe lifecycle shape needed before a transition-noise candidate can be responsibly built.
