# FBA exact submission recurrence and lower-queue headroom

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **EXACT PHASE MODEL — CORRECTED TWO-FRAME CURSOR UNIT**

## Why this model is needed

A 576-source-frame frontend block represents 26.122 ms of 22050-Hz PCM, but that does **not** mean lower submissions occur only once every 26.122 ms.

FBA supplies 367 source frames every emulated video frame.

The frontend residual recurrence is:

```text
r[n+1] = (r[n] + 367) mod 576
```

Since gcd(367,576)=1, the exact phase closes after 576 producer callbacks.

Across that phase:

```text
367 * 576 = 211392 source frames
211392 / 576 = 367 exact lower submissions
```

Thus the frontend submits 367 blocks across 576 video frames.

At the exact XGO 60-FPS scheduler:

```text
phase duration = 9.6 seconds
submission gaps = 1 or 2 video frames
```

This exact burst schedule supersedes coarse models that treated the represented 26.122-ms block duration as the submission interval.

## Correct lower unit

Authoritative geometry:

```text
1 lower cursor unit = 2 stereo PCM time frames
admission ceiling   = 482 units
```

## Stock 44100 path, uncorrected fixed-367 producer

Each frontend block becomes:

```text
576 source
x2 repetition
1152 output frames
576 lower units
```

Hardware drain at 44100:

```text
44100 / 2 = 22050 lower units/s
```

Across the exact 9.6-s phase:

```text
input = 367 * 576 = 211392 units
drain = 22050 * 9.6 = 211680 units
deficit = 288 units / phase
        = 30 units/s
        = 60 output frames/s
```

This is the same already-proven 22020-vs-22050 producer mismatch expressed in corrected lower units.

### Exact continuous-drain phase requirement

If lower playback is already running continuously, the uncorrected stock burst schedule needs up to:

```text
486 units
```

of pre-existing queue before the first modeled burst to avoid crossing zero anywhere in the complete phase.

That is notable because:

```text
admission ceiling = 482 units
```

A submission is accepted only when pre-submit backlog is below 482.

This does **not** prove a physical underrun, because hardware start policy, playback-cursor granularity, fade behavior and real clock error remain outside this ideal model.

But it shows that the fixed-367 deficit is not merely abstract: under an exact continuous 44.1-kHz drain, no indefinitely stable queue solution exists without rate correction.

## Native 22050 path, uncorrected fixed-367 producer

Each frontend block becomes:

```text
576 output frames
288 lower units
```

Hardware drain:

```text
22050 / 2 = 11025 lower units/s
```

Across 9.6 s:

```text
input = 367 * 288 = 105696 units
drain = 11025 * 9.6 = 105840 units
deficit = 144 units / phase
        = 15 units/s
        = 30 output frames/s
```

The same 0.136% time deficit remains; cursor-unit deficit halves because the hardware rate halves.

The exact phase needs up to:

```text
243 units
```

of pre-existing backlog before the first modeled 288-unit burst to avoid crossing zero within one 9.6-s phase.

After that first burst the queue would be:

```text
243 + 288 = 531 units
```

The pre-submit value 243 is comfortably below the 482 admission ceiling, so the first burst can be accepted.

But the persistent 144-unit deficit per phase means no finite initial backlog can prevent eventual depletion forever.

## Exact rate-corrected native 22050

Correct 22020->22050 conversion requires total phase input:

```text
105840 lower units
```

An exact integer distribution is:

```text
223 blocks * 288 units
144 blocks * 289 units
= 105840 units
```

Using a Bresenham-style even distribution of the 144 extra units across the 367 submissions, the complete deterministic phase requires only:

```text
105 units
```

of pre-existing queue before the first burst to remain non-empty.

After the first 288-unit burst:

```text
105 + 288 = 393 units
```

which remains below the 482-unit admission ceiling.

This is a much stronger result than the previous coarse queue estimate:

> **A rate-corrected native-22050 FBA stream has a deterministic non-empty solution entirely below the normal 482-unit admission ceiling.**

No lower-threshold change is required by the exact FBA recurrence.

## Exact rate-corrected 44100 for comparison

At 44100, exact correction requires:

```text
211680 units / phase
```

which can be distributed as:

```text
79 blocks  * 576 units
288 blocks * 577 units
= 211680 units
```

An evenly distributed correction needs approximately:

```text
209 units
```

of pre-existing queue before the first burst.

That is also below the 482-unit admission ceiling.

Therefore exact rate correction can stabilize either 44100 or native 22050 without changing the lower admission policy.

## Practical consequence for the experiment ladder

### Test A — native 22050 only

Still valid and highly isolated.

It retains the 0.136% fixed-367 deficit, so a rare recurring empty/fade artifact may remain.

If Test A sounds cleaner but still has periodic choppiness, that is useful evidence rather than a failed native-rate proof.

### Test B — exact rate correction

Now has an especially strong rationale.

At native 22050, exact correction changes the system from a queue with unavoidable long-term depletion to one with a deterministic stable recurrence below the existing admission ceiling.

That is precisely the sort of small change that could remove recurring gameplay-audio roughness without adding latency or touching the scheduler.

## Evidence boundary

- producer 367, consumer 576, scheduler 60: **BIN/SRC**
- cursor unit two frames, threshold 482: **BIN**
- recurrence and queue values: **exact arithmetic model**
- physical SND clock error/start policy/cursor increment timing: **OPEN/HW**

## Hardware gate

Test A remains hardware-ready in software-contract terms. Test B should remain separate until Test A establishes native-rate behavior.
