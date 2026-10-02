# Stock SNES steady-state empty-gap model under ALSA cursor clamping

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN INPUTS + NECESSARY QUEUE INFERENCE + CONDITIONAL EXACT MODEL**

## Purpose

The stock SNES rate mismatch is proven:

```text
43,920 output frames/s supplied
44,100 output frames/s nominal SND drain
deficit = 180 output frames/s = 90 lower cursor units/s
```

This note asks what the lower queue must do when playback reaches the software commit cursor.

## Queue arithmetic constrains the empty behavior

The lower readiness calculation is binary-proven:

```text
queued = (commit38 - playback3A) mod 8208
ready when queued < 482
```

Suppose the hardware playback cursor were allowed to advance even one cursor unit *past* the software commit cursor at empty.

Then:

```text
commit - playback = -1 mod 8208 = 8207
```

The frontend would interpret the queue as nearly full:

```text
8207 >= 482 -> not ready
```

and would refuse the next submission.

If playback continued advancing beyond commit, the modular distance would remain enormous rather than self-correcting.

No software write to SND playback cursor `+0x3A` has been found in the normal readiness/submission path, and the readiness helper itself performs no recovery.

Therefore normal functioning requires one of these equivalent architectural outcomes at empty:

1. hardware playback progress stops/clamps when `+0x3A == +0x38`; or
2. a hardware/event transition immediately rebases the cursor relationship before software next observes it.

A freely running playback cursor that overtakes commit is incompatible with the recovered queue contract.

This is a **necessary architectural inference**, not a direct register observation.

## Strongest working model

The simplest model consistent with the binary contract and the newly identified legacy **ALSA mode** is:

```text
playback drains queued PCM
 -> playback3A catches commit38
 -> lower transport becomes empty/idle
 -> playback3A does not overtake commit38
 -> later commit advances
 -> playback resumes
```

The exact DAC value while idle remains OPEN.

## Exact cyclic SNES burst structure

Inputs:

```text
producer = 183 source frames per 60-Hz emulated frame
frontend quantum = 576 source frames
x4 conversion
one lower cursor unit = two output frames
one transfer = 1152 lower cursor units
drain = 22050 cursor units/s
scheduler = 17,17,16 ms
```

The 183/576 source phase repeats every 192 emulated frames = 3.2 s.

There are 61 lower submissions per source-phase cycle.

Considering the recurrence cyclically, including the gap from the last submission of one phase cycle to the first submission of the next:

```text
52 inter-submission gaps = 3 emulated frames
 9 inter-submission gaps = 4 emulated frames
total gaps             = 61
```

This corrects the earlier internal-cycle-only count of eight four-frame gaps. There are eight inside the displayed 192-frame window plus a ninth across the cycle boundary.

## Conditional steady-state empty gaps

Under the clamp/idle model above, with immediate resume when fresh PCM is committed and ignoring only the still-OPEN one-tick polling granularity, exact simulation of the deterministic stock schedule reaches empty during each of the nine four-frame gaps.

Steady-state empty durations within a representative 3.2-s cycle are approximately:

```text
1.2857 ms
3.5306 ms
0.2857 ms
1.2857 ms
1.2857 ms
2.5306 ms
1.2857 ms
1.2857 ms
0.2857 ms
```

Total:

```text
13.06122449 ms empty per 3.2 s
```

That total is not coincidental.

The proven rate deficit per 3.2-s cycle is:

```text
288 lower cursor units
```

and:

```text
288 / 22050 s = 13.06122449 ms
```

So the conditional empty-time model exactly accounts for the long-term missing PCM.

## Admission threshold does not repair this pattern

The 482-unit admission predicate does not synthesize audio.

In the idealized deterministic simulation, the queue before the next source block is normally already below the admission threshold, so the 1152-unit block can be submitted as soon as it becomes available.

Thus the long-term 90-unit/s deficit survives the admission policy unchanged.

The one-tick readiness polling granularity can add timing jitter/delay and remains OPEN, but cannot eliminate the deficit.

## Reinit versus steady state

Two distinct empty-gap mechanisms now exist:

### Runtime reinit

Both lower queue state and frontend FIFO are explicitly reset. SNES then needs four fresh 183-frame callbacks before its first 576-frame frontend transfer.

This can create a much larger transition gap.

### Normal steady state

No reset is required. Fixed-183 production is simply slower than nominal SND consumption, creating recurring depletion pressure. Under the clamp model this becomes nine short empty intervals per 3.2-s source-phase cycle.

Do not conflate these mechanisms.

## Underrun-fade significance

The SND underrun-fade feature is independently proven enabled.

The conditional steady-state model now gives it a concrete job to perform: shape the DAC transition during these short empty intervals.

Possible behaviors still OPEN include:

- fade toward zero then resume;
- hold/fade last sample;
- output zero after fade;
- another hardware-specific transition.

The exact waveform/duration is the next fidelity/noise boundary.

## What is proven versus conditional

### Proven [BIN]

- fixed 183 SNES source frames/frame;
- 60-Hz stock scheduler;
- 576-source-frame frontend transfer;
- exact x4 repetition;
- 44.1-kHz hardware-facing rate;
- modular lower queue distance;
- 482-unit admission threshold;
- SND ALSA mode enabled;
- underrun fade enabled.

### Necessary inference [INF]

The playback cursor cannot freely overtake the commit cursor under the observed modular queue contract without making normal recovery impossible.

### Conditional model [INF]

If ALSA mode clamps/idles at empty and resumes on new commit, the deterministic SNES schedule yields nine short empty intervals totaling exactly 13.0612 ms per 3.2 s.

### Still OPEN

- direct hardware observation of `+0x3A` at empty;
- exact ALSA-mode resume semantics;
- DAC sample during empty;
- underrun-fade curve and duration;
- RTOS tick contribution.

## Hardware gate

Not reached.
