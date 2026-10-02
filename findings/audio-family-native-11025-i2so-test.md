# HC15xx family I2SO test defaults to native 11025 Hz

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **UP — FAMILY SOURCE**

## Closure of prior family-evidence gap

The maintained HC15xx HCRTOS source contains a direct I2SO playback test:

```text
bnister/sf2000_hcrtos
components/cmds/source/sound_test/i2so_test.c
```

Its default playback configuration is explicitly:

```c
params.rate = 11025;
params.channels = 2;
params.period_size = read_size;
params.periods = 8;
params.bitdepth = 16;
params.start_threshold = 2;
ioctl(snd_fd, SND_IOCTL_HW_PARAMS, &params);
ioctl(snd_fd, SND_IOCTL_START, 0);
```

The test then submits ordinary interleaved S16 stereo transfers directly to `/dev/sndC0i2so`.

Thus 11025 is not merely an enum/API-declared family rate. It is the **default executable playback rate in the family I2SO sound test**. [UP]

## Relationship to exact XGO evidence

This independently aligns with the exact XGO binary recovery:

- XGO low-level rate programmer has a dedicated 11025 branch;
- that branch programs a coherent divider pattern;
- related HC15xx HCRTOS code actively configures I2SO playback at 11025.

Together these make “the silicon family fundamentally cannot output 11025” an increasingly implausible explanation for XGO's forced 44.1-kHz path.

The remaining question is exact XGO board/output qualification, not family API capability.

## Useful family semantics

The same test makes several modern-driver units explicit:

```text
period_size is bytes
xfer.frames = bytes / 4 for stereo S16
delay is returned in frames
start_threshold is a number of periods
```

This continues to support the rule that modern HCRTOS `start_threshold=2` must not be numerically equated with XGO's legacy 482 cursor-unit admission threshold.

## Evidence discipline

- family native 11025 playback configuration: **UP**
- exact XGO native 11025 register branch: **BIN**
- exact XGO board audible success at native 11025: **OPEN/HW-only eventually**
- modern HCRTOS period/start-threshold numeric mapping to XGO legacy driver: **not established**

## Hardware gate

Not reached.
