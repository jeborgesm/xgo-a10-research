# Audio family-source comparison — stock driver remains opaque below frontend

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **UPSTREAM/FAMILY SOURCE AUDIT — NO HARDWARE CANDIDATE**

## Scope

Per the investigation plan, this pass compares the XGO lower-audio findings against maintained SF2000/GB300 family material before requesting any hardware observation.

Primary maintained family reference searched: `Trademarked69/sf2000_multicore`, including its SF2000 08/03 and GB300 V2 linker maps and frontend source.

## What family source confirms [UP]

The maintained family project exposes the same stock-frontend boundary rather than replacing the vendor SND implementation.

Its linker maps identify:

```text
SF2000 08/03
run_sound_advance = 0x80356168
retro_audio_sample_batch_cb = 0x80358430

GB300 V2
run_sound_advance = 0x8035ADB4
retro_audio_sample_batch_cb = 0x8035C25C
```

The GB300 map explicitly annotates `run_sound_advance` as `sound_driver_play`.

This agrees with the XGO binary recovery: libretro PCM is handed to a stock vendor sound-driver path rather than to an open multicore SND backend.

## What maintained multicore does not expose [UP/OPEN]

Repository search did not locate source definitions for the HC15xx vendor SND register layer corresponding to XGO's:

```text
MMIO cursor pair +0x38/+0x3A
hardware count fields +0x11C/+0x19C
```

Nor did it expose a documented vendor underrun handler or named register definitions sufficient to assign exact semantics to those offsets.

This is consistent with the project's architecture: multicore links against/reuses stock firmware functions for the frontend/audio path.

Therefore the maintained multicore tree cannot by itself close XGO's lower cursor register names or underrun waveform.

## Family comparison implication [UP/BIN]

The strongest family evidence is structural:

```text
libretro callback
 -> family stock run_sound_advance / sound_driver_play
 -> opaque vendor audio driver
```

That is the same boundary now recovered much farther down in the XGO binary.

No evidence was found in maintained multicore source for an alternate family software resampler that would supersede the XGO binary-proven 2x/4x whole-stereo-frame repetition algorithm.

Absence from the source tree is not proof that SF2000/GB300 binaries use the identical converter; binary comparison remains the correct route for that question.

## Hardware gate assessment

Offline work is **not exhausted**.

The maintained source does not name the lower registers, but two offline avenues remain:

1. binary-compare the corresponding SF2000 08/03 and GB300 V2 stock audio-device callbacks against XGO;
2. inspect HC-RTOS/vendor-derived source repositories beyond multicore for the SND register layout.

No hardware test is requested yet.

## Next offline target

Use the pinned family stock images already used by the archaeology workflow to locate the family equivalents of:

```text
XGO +0x70 audio-device submission callback
XGO low-rate repetition helper
XGO readiness/cursor-distance helper
```

Compare instruction-level behavior and constants:

- 11025/22050 conversion ratios;
- 960 sample_num;
- derived 482 threshold;
- lower ring geometry;
- cursor/register offsets.

If those are conserved, the family binaries can provide an independent check of the XGO reconstruction even though the maintained source leaves the vendor SND backend opaque.
