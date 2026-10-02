# Audio fidelity / noise / latency deep-dive checkpoint — 2026-10-01

Branch: `research-audio-fidelity-latency`  
Status: **OFFLINE ARCHAEOLOGY CONTINUES — NO HARDWARE CANDIDATE**

## New closures from this deep dive

### 1. HC15xx family API vocabulary recovered [UP]

Recovered HCRTOS source exposes the concepts missing from the old XGO binary labels:

- periods / period_size
- start_threshold
- get_avail / AVAIL_MIN
- delay
- drain
- pause / resume
- underrun event
- DMA-style I2SO PCM

This provides a disciplined vocabulary for identifying old XGO functions without guessing from arithmetic alone.

### 2. XGO underrun-fade control identified [BIN + family HW/SRC]

XGO low-level helper `0x8030A61C` controls SND offset `+0x3C`, bit `0x40`.

Both recovered XGO setup callers enable the bit.

Independent UniFrog HC15xx hardware work names exactly:

```text
SND0 +0x3C bit 0x40 = underrun fade
```

Therefore XGO stock enables the HC15xx underrun-fade feature.

Exact fade curve/end state remains OPEN.

### 3. Digital fade and physical L23 gate are separate [BIN/INF]

XGO has:

```text
SND underrun fade: +0x3C bit 0x40
physical amp gate: GPIO L23
```

Family hardware work confirms that digital zero alone does not necessarily remove analog board noise with the amp route open.

This strongly supports treating XGO noise as a sequencing/gating problem distinct from PCM fidelity.

### 4. Stock lower audio uses 90 during setup [BIN]

XGO lower setup calls a sound-control helper with `0x5A = 90`.

Family stock archaeology independently reports the same `0x5A` value, and the open SF2000 DTS uses volume 90 with a clipping-avoidance note.

XGO user volume can later reach 99. Whether 99 actually clips on XGO remains OPEN and belongs to a separate fidelity experiment.

### 5. Direct 22.05-kHz I2SO is family-hardware proven [family HW]

Current UniFrog hardware work reports successful 22050-Hz native I2SO operation.

This proves the HC15xx family silicon/runtime does not inherently require:

```text
22050 -> duplicate 2x -> 44100
```

XGO's FBA conversion is therefore a stock driver/software policy.

For a future non-stock path, direct 22050 is now a concrete family-proven way to remove XGO's zero-order-hold conversion.

### 6. Small periods are a family-proven latency direction [family HW]

UniFrog reports 512-byte I2SO periods gave the lowest measured write cost among its tested sizes across 22050/44100/48000.

Exact current period counts in UniFrog have evolved, so old documentation defaults must not be copied literally.

The durable conclusion is only:

> smaller tested lower-I2SO periods reduced blocking and are a credible latency experiment after XGO baseline occupancy is measured.

### 7. Later HC15xx source has a stateful resampler API [UP]

Recovered HCRTOS headers expose `delta`, `phase`, and three-sample per-channel history plus `resample_process()`.

The implementation is absent, so exact filter quality is OPEN.

A later HCD3100-family tree goes further with WebRTC-style resampling state. This is lineage evidence, not XGO architecture.

### 8. Important cursor-ownership correction [BIN]

The earlier phrase "two hardware cursors +0x38/+0x3A" was too broad.

Post-transfer callback:

```text
object +0x74 = 0x80304C50
```

loads private software cursor `+0x46` and calls:

```text
0x8030A130
```

which writes:

```text
SND +0x38 = cursor
```

Therefore:

```text
+0x38 = software-committed SND cursor/boundary
+0x3A = paired SND-maintained cursor
```

The modular-distance arithmetic is still proven, but its semantic label must remain OPEN until the active playback mode is closed.

This supersedes earlier wording that treated both as independently advancing hardware cursors.

## Current pipeline with evidence-safe labels

```text
libretro core stereo S16 PCM
        |
        v
frontend 0x4800-byte ring
  4608 stereo source frames
  576-frame consumer quantum
        |
        v
XGO low-rate conversion
  22050 -> 44100 by 2x whole-frame repetition
  11025 -> 44100 by 4x whole-frame repetition
        |
        v
lower circular storage
  131328 bytes
  private software cursor +0x46
  modulus +0x48 = 8208
        |
        v
post-transfer commit
  SND +0x38 <- private +0x46
  paired SND +0x3A observed by distance helper
        |
        v
SND/I2SO
  sample_num 960 hardware count
  +0x3C bit 0x40 underrun fade ENABLED
        |
        v
DAC / analog output
        |
        v
GPIO L23 amplifier gate
        |
        v
single physical speaker
```

## What is still not closed

- exact vendor name/unit for `sample_num=960`;
- exact semantic role/name of SND `+0x38/+0x3A`;
- whether the 482-distance threshold is availability, start threshold, delay threshold, or mode-specific;
- normal steady-state lower queue occupancy;
- exact emulator-to-DAC latency;
- exact fade curve and post-underrun terminal behavior;
- exact XGO gain curve and whether user level 99 clips;
- direct 11025 hardware viability on XGO's old stock driver.

## Most promising improvement hypotheses, kept separate

### Fidelity

A. FBA: bypass XGO's 2x ZOH by using native 22050 I2SO, based on family hardware proof.

B. SNES: investigate direct 11025 or a real resampler; do not assume either yet.

C. Test 90-vs-99 gain separately for clipping.

### Noise

A. Preserve SND underrun fade.

B. Keep DAC/SND mute separate from L23 amp gating.

C. Eventually test delayed L23 close only after sustained silence, mirroring the successful family strategy.

### Latency

A. First recover XGO delay/occupancy semantics.

B. Only then test lower period/count reduction.

C. Do not change scheduler or frameskip as part of the latency experiment.

## Next offline work

1. Resolve active mode reaching `0x802FD5A4` and identify what its 482-distance predicate actually means.
2. Trace SND `+0x3A` update/status/interrupt path.
3. Find XGO equivalent of HCRTOS `SND_IOCTL_DELAY`.
4. Trace lower volume helper and SND/DAC mute sequencing.
5. Search family binaries/source for direct 11025 evidence.

## Hardware gate

Not reached. Static/source archaeology still has productive targets.
