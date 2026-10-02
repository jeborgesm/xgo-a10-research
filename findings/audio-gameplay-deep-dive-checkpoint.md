# Gameplay-audio deep-dive checkpoint and controlled experiment ladder

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **OFFLINE ARCHAEOLOGY COMPLETE ENOUGH FOR FIRST CPS1 A/B; NO ARTIFACT BUILT**

## User target

Make the XGO sound as good as the hardware reasonably allows **while playing games**.

Primary concerns are CPS1/FBA audio synchronization, sustained playback stability under load, avoiding software-created distortion, preserving meaningful stereo content through the single internal speaker, and protecting the established CPS1 performance baseline.

Transition pops/menu cleanup are no longer gating.

## Major deep-dive closures

### FBA conversion quality

Stock XGO performs:

```text
22050 source -> 44100 by exact x2 frame repetition
```

There is no interpolation/filtering.

### Exact XGO native rate capability

The active XGO SND clock programmer contains dedicated 22050- and 11025-Hz divider configurations. Related HC15xx source actively configures native 11025 I2SO playback.

### Minimal native-22050 proof surface

A native FBA proof requires only three instruction-word changes:

```text
0x80306E00  keep selected rate at requested 22050
0x802FDFC8  bypass first x2 22050 conversion branch
0x802FE068  bypass second x2 22050 conversion branch
```

No code cave is needed. Generic lower submission is rate-agnostic after that conversion decision.

### FBA actual producer clock

```text
367 source frames * 60 scheduler frames/s = 22020 source frames/s
```

The declared rate is 22050. Exact correction ratio:

```text
22050 / 22020 = 735 / 734
```

This 0.136% deficit should be corrected separately from the first native-clock proof.

### CPS timing

The embedded CPS engine retains nominal `59.633333 Hz`, while XGO's frontend executes its protected NTSC loop at exact 60 FPS.

The vendor's fixed 367 audio segment aligns much more closely with the frontend 60-Hz cadence than with nominal CPS board timing.

For this project, audio should synchronize with XGO's actual protected gameplay cadence; board-authentic CPS speed is a separate project.

### Correct lower cursor geometry

Deep ALi HLD source correlation corrected an earlier interpretation:

```text
1 lower cursor unit
= 16 internal DMA bytes
= 2 stereo S16 time frames
```

not four frames.

Correct threshold:

```text
482 units = 964 frames
             21.859 ms @44100
             43.719 ms @22050
```

The threshold is an admission ceiling, not a forced preload.

### Legacy ALi sound API identified

XGO command semantics line up with public ALi HLD:

```text
0x10 IS_SND_RUNNING
0x15 IS_PCM_EMPTY
0x21 SND_CHK_PCM_BUF_DEPTH
0x31 SND_GET_SAMPLES_REMAIN
0x36 SND_AUTO_RESUME
```

XGO sound initialization explicitly disables `SND_AUTO_RESUME`, even though the object default enables it. Do not change that in the first candidate.

### DMA depth

`SND_CHK_PCM_BUF_DEPTH` returns 8, matching the recovered lower allocation depth factor.

### FBA latency floor

FBA produces one audio burst per video frame, so latency cannot be reduced arbitrarily by shrinking downstream queues.

Stock frontend 576-frame batching adds about 13.06 ms mean callback-to-consumer residence.

A moderate later reduction to 384 or 288 can save several milliseconds, but increases sound-task/submission frequency and must be stress-tested on heavy CPS1.

### Single-speaker precedent

Maintained family source uses:

```text
audible first channel = (L >> 1) + (R >> 1)
second digital channel = original R
```

which preserves right-only content on a single-speaker unit without raw-sum clipping.

Exact XGO external/AV stereo topology remains open, so mono folding remains a separate later experiment.

## Controlled experiment ladder

### Test A — native 22050 proof

Change only hardware-facing FBA rate 44100 -> 22050 and bypass x2 repetition.

Keep stock scheduler, 367 producer, 576 frontend quantum, 960 sample_num, 482 admission threshold, stereo policy, auto-resume, SNES and Audio OSD.

Questions:

1. boots reliably after normal LCFG reseal;
2. SF2 audio pitch/clarity improves or remains correct;
3. audio remains synchronized during long play;
4. Cadillacs and Dinosaurs is no worse under heavy load;
5. no new stalls or silence.

### Test B — exact FBA rate correction

Only after A passes. Correct actual 22020-frame/s production to exact 22050 hardware time using a fractional scheme.

Question: does eliminating the 0.136% persistent deficit remove recurring micro-choppiness/empty events?

Do not change frontend quantum yet.

### Test C — latency quantum

Only after stable rate/fidelity path.

Compare:

```text
576 baseline
384 moderate
288 aggressive
```

Stress with heavy CPS1. Choose the smallest quantum that remains audibly clean and does not regress gameplay performance.

### Test D — single-speaker fold

Use material with meaningful stereo separation, especially QSound-era CPS titles.

Acceptance: left-only content audible; right-only content audible; centered material not clipped; external stereo preserved if that route proves stereo.

### Test E — auto-resume diagnostic only if needed

If heavy CPS1 still exhibits stalls after A/B/C, use the now-identified `IS_PCM_EMPTY` / `SND_GET_SAMPLES_REMAIN` diagnostics to establish whether real lower-buffer empty events correlate with the symptom.

Only then evaluate `SND_AUTO_RESUME`.

## Fallback if native 22050 sounds worse

Do not force native output.

Fallback fidelity path:

```text
retain 44100 hardware
replace x2 zero-order hold with a low-cost interpolating/fractional converter
```

That path costs more CPU/memory than native output but remains technically available.

## Current assessment

There is now a strong, evidence-backed path to improving CPS1 audio without touching the protected gameplay scheduler.

The first native-rate test is especially attractive because it removes crude x2 repetition, halves lower PCM payload rate, eliminates the expansion scratch pass, requires only three instruction-word changes, and leaves the rest of the audio architecture intact.

The remaining uncertainty for Test A is genuinely hardware/audibility, not missing software archaeology.

## Workflow note

The offline archaeology GitHub Action is now manual-only because stock `bisrv.asd` is intentionally not committed to GitHub.

Findings-only commits should therefore stop generating meaningless missing-firmware workflow failures.

## Artifact gate

No hardware ZIP has been produced in this checkpoint.
