# Family audio improvement leads — direct 22.05-kHz I2SO, measured small periods, and resampler ancestry

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **FAMILY HW/UPSTREAM COMPARISON — NO XGO HARDWARE CANDIDATE**

## Why this matters

The XGO stock path is now BIN-proven to normalize 22.05 kHz to 44.1 kHz by duplicating every stereo frame twice, and 11.025 kHz by repeating every frame four times.

The investigation priority asks whether HC15xx relatives implement any of these stages better.

Current UniFrog work provides a concrete answer for at least the 22.05-kHz lane.

## SF2000 family hardware can use 22.05 kHz directly [family HW/UP]

UniFrog's retained hardware findings report successful native HCRTOS I2SO benchmarking at:

```text
22050
44100
48000
```

A later UniFrog commit tightens the libretro device-rate policy after a real failure at the unusual Snes9x-reported 32040-Hz rate:

```text
known-good direct rates:
22050
32000
44100
```

Unusual rates are redirected to a known-good output rate.

Therefore, on tested SF2000-family HCRTOS hardware, **22.05-kHz PCM does not need to be converted to 44.1 kHz merely to reach I2SO**. [family HW]

This is a major contrast with XGO stock:

```text
XGO stock FBA:
22050 source
 -> duplicate each stereo frame 2x
 -> 44100 hardware-facing path

modern family HCRTOS/UniFrog:
22050 source
 -> direct 22050 device rate is hardware-proven
```

This identifies XGO's 22.05->44.1 zero-order-hold conversion as a **stock software/driver policy**, not an unavoidable HC15xx silicon requirement.

## Fidelity implication

For FBA/CPS1, a future non-stock audio path could potentially remove the proven 2x zero-order hold entirely by using a direct 22.05-kHz I2SO configuration.

That would avoid the stock repetition imaging/stairstep behavior without inventing interpolated samples.

This is a future experiment direction, not authorization to patch the current protected firmware.

## 11.025-kHz status

The HC15xx public PCM API declares 11025-Hz rate capability, and the HCRTOS I2SO test program defaults to 11025 Hz.

However, the current UniFrog production policy specifically names 22050/32000/44100 as device-tested known-good rates after rejecting an unusual 32040-Hz core rate.

Therefore:

- HC15xx API support for 11025: [UP]
- example configuration at 11025: [UP]
- current retained production hardware proof equivalent to 22050: not established by the evidence reviewed here.

Do not yet claim that XGO's SNES 11.025-kHz path can simply switch to direct 11025 on stock hardware.

## Later HC15xx resampler API [UP]

The recovered HCRTOS kernel headers expose a reusable resampler state:

```c
struct rescale {
    unsigned int enabled;
    unsigned int delta;
    unsigned int phase;
    int32_t history[MAX_RESCALE_CHANNELS][3];
    unsigned int frequency;
    unsigned int frequency_out;
};
```

with:

```text
init_scale()
resample_flush()
resample_process()
```

The implementation is not present in the examined open tree, so its exact filter must remain OPEN.

Nevertheless, this is architecturally more sophisticated than XGO's BIN-proven low-rate helper: it maintains phase plus three-sample history per channel rather than merely repeating each 32-bit stereo word.

A still newer HCRTOS-family tree (`tjh-l/HCD3100-8y`) exposes WebRTC-style resampling state and explicit source/target rates. This is useful lineage evidence, but it is later-family evidence and must not be promoted into XGO architecture.

## UniFrog's libretro conversion policy [UP]

Current UniFrog avoids resampling when the core rate is already a known-good device rate.

Its generic fallback for unusual rates uses an accumulator/drop-style conversion in the frontend. That code should **not** be copied blindly as a high-fidelity resampler.

The important family lesson is instead:

> prefer a hardware-supported native PCM rate when proven; resample only when the device rejects the core's rate.

For XGO FBA, family hardware evidence now says 22050 is a credible native-rate target.

## Latency evidence from family hardware [family HW]

UniFrog's SF2000 hardware benchmark reports that **512-byte periods had the lowest measured write cost** across 22050, 44100 and 48000 Hz; larger periods blocked longer.

Its performance API explicitly tracks audio delay/backlog, write pressure, clipping, queue occupancy and underrun likelihood.

Current source has evolved beyond the older documentation's exact period-count defaults, so the historical “four periods” statement must not be treated as the current libretro configuration. The durable hardware result is the direction:

```text
smaller tested I2SO periods -> lower write blocking / lower-latency behavior
```

This gives us a family-proven experimental direction for XGO after its stock latency baseline is measured.

## Noise/fidelity family evidence

UniFrog hardware findings also establish:

- hardware DAC volume/mute should be configured before opening the physical amp gate;
- digital zero alone does not eliminate board noise with the analog route open;
- higher software gain can mask noise but produce crunchy/clipped audio;
- stable SF2000 libretro uses 1x software gain;
- the open SF2000 DTS uses I2SO volume 90 with an explicit clipping-avoidance comment.

XGO independently initializes a lower sound control with `0x5A = 90`, while its user-facing volume policy can later reach 99.

This makes maximum-gain clipping a valid **separate fidelity lane**, but not yet a proven XGO defect.

## Experimental lanes implied by the family comparison

Keep these independent:

### Fidelity

- stock XGO 22.05->44.1 ZOH vs direct 22.05-kHz I2SO;
- later, if needed, quality resampler vs stock repetition;
- volume 90 vs 99 clipping/peak behavior.

### Latency

- stock queue occupancy baseline;
- period/count geometry only after baseline;
- eventually smaller lower periods if the stock API surface can be changed safely.

### Noise

- SND mute and underrun-fade behavior;
- L23 amplifier-gate sequencing;
- sustained-silence close policy.

Do not combine these into one candidate.

## Next offline target

The highest-value remaining static target is XGO's equivalent of the family `SND_IOCTL_DELAY`/queue-delay calculation.

Once found, it should expose queued frames directly and may finally turn the stock latency question from capacity bounds into a real occupancy model.

## Hardware gate

Not reached.
