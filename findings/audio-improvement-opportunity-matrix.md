# Audio improvement opportunity matrix — evidence-gated baseline

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **INVESTIGATION CHECKPOINT — NO HARDWARE CANDIDATE**

## Purpose

Freeze the currently proven improvement surfaces before deeper work continues, so later experiments change one mechanism at a time and do not accidentally mix hypotheses.

## Lane A — fidelity / sample-rate conversion

### Stock behavior [BIN]

```text
22050 source -> 44100 by repeating every stereo frame twice
11025 source -> 44100 by repeating every stereo frame four times
44100 source -> 44100
48000 source -> 48000
```

The low-rate path is exact zero-order hold. There is no interpolation or filtering.

### Improvement opportunity

Replace the x2/x4 frame repetition with a better controlled conversion, or bypass conversion where native hardware rate support is proven.

Family evidence demonstrates successful native 22050 I2SO operation on related HC15xx software/hardware. Subsequent exact-XGO binary recovery strengthened this substantially: the active XGO low-level SND clock programmer contains explicit 11025- and 22050-Hz cases. The remaining uncertainty is complete-board behavior when the higher-level forced 44.1-kHz normalization is bypassed, not absence of low-rate clock programming.\n\nA native-rate experiment must also account for the lower 482-unit admission threshold: unchanged cursor-unit depth represents about 87.44 ms at 22.05 kHz and 174.88 ms at 11.025 kHz, so native rate can improve fidelity while worsening wall-clock queue depth unless latency policy is handled separately.

### Isolation rule

Do not alter queue sizes, scheduler, mono policy or mute sequencing in the fidelity candidate.

---

## Lane B — frontend batching latency

### Stock behavior [BIN + arithmetic]

Frontend FIFO:

```text
capacity = 4608 stereo S16 source frames
consumer quantum = 576 source frames
```

FBA 22050:

```text
producer = 367 frames/video callback
mean frontend batching residence ~= 13.07 ms
phase max ~= 33.37 ms
```

Stock NTSC SNES 11025:

```text
producer = 183 frames/video callback
mean frontend batching residence ~= 26.05 ms
phase max ~= 66.56 ms
```

### Improvement opportunity

The fixed 576-source-frame quantum is disproportionately expensive for SNES.

A smaller consumer quantum is therefore a concrete latency lever.

### Important constraint

The lower SND admission/backlog policy is a separate queue and must not be changed in the same first experiment.

---

## Lane C — lower SND backlog

### Stock behavior [BIN]

Lower SND queued distance is:

```text
(commit38 - playback3A) mod 8208
```

Admission requires queued distance below 482 cursor units.

One cursor unit = 16 bytes = four stereo S16 output frames.

Threshold depth:

```text
44100: 43.719 ms
48000: 40.167 ms
```

Whole converted blocks can take the queue above that threshold after admission.

### Improvement opportunity

There may be additional latency available by changing lower backlog/admission policy, but the exact safe floor is not yet known.

### Isolation rule

Do not combine lower threshold changes with the first frontend-quantum experiment.

---

## Lane D — internal-speaker stereo-to-mono preservation

### Stock behavior [BIN/HW]

- libretro/frontend PCM is interleaved stereo S16;
- lower SND transport is configured for two channels;
- the physical XGO specimen has one internal speaker;
- stock frontend does not downmix before its PCM ring.

### Requirement

Internal-speaker playback must preserve ordinary content from either source channel.

A safe diagnostic fold already exists from historical Arcade Test13:

```text
mono = (L + R) / 2
L = mono
R = mono
```

This preserves left-only and right-only content, avoids raw-sum overflow, and leaves the downstream transport stereo-shaped.

### Remaining boundary

Do not globally fold until external/AV audio topology is known. The LCD/TV mode branch does not software-switch L23 or the PCM transport, so external audio may share the same stereo DAC stream.

---

## Lane E — reinit / transition noise

### Stock behavior [BIN]

Initial game startup initializes sound before opening L23.

A runtime sound-reinitialization path instead executes while L23 remains in its prior state, normally open.

That reinit:

- performs a real sound-device control/setup sequence;
- reapplies volume;
- issues further device controls;
- resets frontend producer and consumer offsets to zero;
- leaves old frontend ring bytes allocated but logically discarded.

### Improvement opportunity

If this path correlates with audible pop/click/noise, the board already provides an appropriate suppression mechanism: L23.

Preferred eventual shape:

```text
mute L23
 -> reconfigure
 -> wait for a proven valid/primed audio condition
 -> unmute L23
```

Do not invent a fixed delay while a queue/ready condition can potentially be recovered.

---

## Lane F — SNES fixed-integer producer fidelity

### Stock behavior [BIN]

The built-in SNES path computes:

```text
callback_increment = trunc(sample_rate / video_refresh_rate)
```

For normal NTSC:

```text
sample_rate = 11025
increment = 183 frames per video callback
```

Maintained family source instead uses fractional accumulation and therefore alternates frame counts as necessary.

### Improvement opportunity / OPEN question

If stock XGO has no compensation elsewhere, fixed 183-frame production may create a small long-term mismatch against nominal 11025-Hz timing.

This must **not** yet be called a pitch error or audible defect. Upstream mixer clocking or another compensation mechanism may account for it.

The next fidelity archaeology target is to close that compensation question.

---

# Priority order before hardware candidates

1. close SNES fixed-183 compensation/mixer behavior;
2. continue legacy XGO device-control dispatcher recovery for runtime reinit;
3. recover lower-SND behavior across reinit;
4. close external/AV channel topology as far as software/family evidence permits;
5. only then define isolated candidate experiments.

# Current practical conclusion

There are now multiple independent, code-backed improvement surfaces. The investigation is no longer asking whether XGO audio can plausibly be improved; it is determining which change gives which benefit and how to test each without confounding the others.

No hardware candidate is authorized yet.
