# Future improvements after interactive mapper

This file deliberately keeps post-mapper work out of the mapper branch implementation scope while preserving hardware observations and desired follow-up work.

## Emulator performance / replacement

Hardware observations during mapper validation:

- SNES emulation is slow/choppy on tested titles.
- CPS1 Street Fighter II can drop enough frames that moves/animations become effectively invisible and gameplay suffers.
- NES mapper validation worked, but the broader emulator modernization work remains relevant.

Planned direction:

- continue the external/native core integration track;
- evaluate replacement SNES and CPS1-capable cores/emulators against stock performance;
- preserve the existing launcher/save/input integration where practical;
- measure frame pacing and audio behavior on hardware rather than relying on subjective desktop/core expectations.

## Audio control granularity

Current device UI effectively exposes four useful states:

```text
mute / none
low
mid
high
```

Desired future behavior is finer intermediate volume control, for example:

```text
0% / mute
low
mid-low
mid
mid-high
high
```

or a larger stepped scale if the underlying mixer supports it cleanly.

Desired UI behavior:

- temporary on-screen volume percentage or level indicator when volume changes;
- indicator disappears automatically after a short interval;
- no permanent overlay during gameplay.

Research questions:

1. Determine whether the current four-level behavior is only a UI quantization or reflects actual hardware/mixer limitations.
2. Trace the stock volume variable, attenuation/gain conversion, and audio output path.
3. Identify the safe numeric range and useful perceptual step spacing.
4. Locate a lightweight existing OSD/text path suitable for a temporary volume indicator.

These are follow-up improvements and should not block closure of the interactive mapper feature.