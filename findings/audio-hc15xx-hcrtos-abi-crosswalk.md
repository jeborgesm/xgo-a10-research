# HC15xx HCRTOS audio ABI crosswalk against XGO lower-SND binary

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN + UPSTREAM SDK-DERIVED SOURCE CROSSWALK — NO HARDWARE CANDIDATE**

## Sources and evidence discipline

XGO facts below remain based on the preserved stock `bisrv.asd` [BIN].

Family/SDK vocabulary comes from the recovered/open HC15xx HCRTOS tree `bnister/sf2000_hcrtos` [UP]. That tree is highly relevant HC15xx ancestry, but it is not assumed to be source-identical to the older proprietary XGO sound driver.

Therefore matching concepts/numbers are marked [INF] until an instruction-level or symbol-level identity is demonstrated.

## HC15xx sound ABI vocabulary [UP]

`components/kernel/source/include/uapi/hcuapi/snd.h` defines a PCM playback contract containing:

- `rate`
- `channels`
- `bitdepth`
- `period_size`
- `periods`
- `start_threshold`

The source comments state:

```text
dmabuf size(bytes) = channels * period_size * periods
start_threshold = number of periods to auto-trigger start
period_size = byte size of one period, must be 32-byte aligned
```

The API also exposes:

```text
SND_IOCTL_START
SND_IOCTL_DROP
SND_IOCTL_DELAY
SND_IOCTL_DRAIN
SND_IOCTL_PAUSE
SND_IOCTL_RESUME
SND_IOCTL_XFER
SND_IOCTL_AVAIL_MIN
SND_EVENT_UNDERRUN
```

This closes an important terminology gap: the HC15xx family sound architecture explicitly has DMA-buffer, period, availability, delay/drain, pause/resume, and underrun concepts. [UP]

## Open I2SO playback example [UP]

The HC15xx `i2so_test.c` configures:

```text
channels = 2
bitdepth = 16
periods = 8
start_threshold = 2
```

It then:

1. applies HW params;
2. sets an availability minimum;
3. starts the device;
4. submits interleaved S16 frames through `SND_IOCTL_XFER`;
5. polls when transfer reports insufficient availability;
6. queries `SND_IOCTL_DELAY` before drop/free.

This architecture closely mirrors the behavior recovered independently from XGO's opaque callbacks: readiness/availability test -> block/wait -> transfer -> hardware-progress-driven availability. [UP/BIN/INF]

## Strong XGO numerical correspondences

### Eight-buffer/period constant

XGO binary initialization writes a global constant:

```text
0x8030A040  li v0,8
0x8030A044  sw v0,0x9C08(gp)
```

That constant controls lower circular-storage allocation and modulus construction. [BIN]

The open HC15xx I2SO playback example independently uses:

```text
periods = 8
```

The numerical and architectural match is strong [INF], but the XGO global is not renamed `periods` at BIN level yet.

### Two-period-style threshold

XGO:

```text
sample_num = 960
threshold = (960 >> 1) + 2 = 482 lower units
1 lower unit = 16 bytes = 4 stereo S16 frames
482 units = 1,928 stereo frames
```

Therefore:

```text
1,928 frames = (2 * 960) + 8 frames
```

The open HC15xx playback example independently uses:

```text
start_threshold = 2
```

This is strong evidence [INF] that XGO's 482-unit gate belongs to a two-period-style readiness/start/availability geometry, with an eight-frame guard/alignment term, rather than being an arbitrary delay constant.

It is **not yet BIN proof** that XGO private `+0xFA` is literally the SDK field named `start_threshold`.

## Correction to previous startup wording

`audio-lower-snd-cursor-roles-startup-admission.md` stated that no separate large startup-prebuffer threshold had been found in the traced XGO path.

That remains true as a statement about what had been found in XGO BIN, but it must **not** be interpreted as proof that the HC15xx driver has no auto-start/prebuffer mechanism.

The recovered HC15xx API explicitly defines `start_threshold` as a number of periods required to auto-trigger start. [UP]

Therefore startup occupancy remains OPEN for XGO until the old driver's start transition is mapped.

## Availability semantics [UP]

`snd_core.c` makes the modern family contract explicit:

```text
frames = platform->driver->get_avail(platform)
if frames < xfer->frames:
    transfer fails / caller waits
else:
    platform->driver->transfer(...)
```

Polling likewise wakes when:

```text
get_avail() >= avail_min
```

This is an excellent conceptual match for XGO `0x802FD5A4`: read hardware cursor geometry, compare against a threshold, and allow the upper transfer only when sufficient lower capacity is available. [UP/BIN/INF]

The XGO callback can therefore safely be described as an **availability/readiness predicate**. Exact field-name identity remains OPEN.

## Underrun is a first-class HC15xx event [UP]

The public HC15xx API defines:

```text
SND_EVENT_UNDERRUN
```

This materially narrows the earlier XGO underrun possibilities: the family architecture has an explicit underrun concept.

However, the open generic sound core does not define the platform-specific response waveform. The concrete I2SO platform implementation that would tell us whether hardware stops, emits zero, repeats, or wraps is not present in the recovered source examined here.

Thus XGO underrun output behavior remains OPEN.

## Pause / drain / teardown ancestry [UP]

The generic HC15xx sound core distinguishes:

- START
- STOP/DROP
- DRAIN
- PAUSE
- RESUME
- HW_FREE

On HW_FREE it mutes through `volume_mute(...,1)`, stops the platform, frees hardware resources, and then stops/frees linked DAIs.

This provides a source-ancestry model for the distinct XGO transition behaviors already observed. It does not prove that the XGO firmware uses the identical call order.

## Important geometry caveat

The numerical identity:

```text
XGO lower allocation = 131,328 bytes
```

can be factored in ways resembling the HC15xx period contract, but the current evidence does **not** uniquely prove XGO's exact `period_size` field.

Do not rename XGO `+0x48 = 8208` to `period_size` merely from arithmetic.

What is BIN-proven remains:

```text
+0x48 = lower circular modulus
1 cursor unit = 16 copied bytes
allocation = 131,328 bytes
```

## New source-guided reverse-engineering targets

The SDK vocabulary gives exact concepts to search for in XGO BIN:

1. auto-start after N periods;
2. available-frame calculation;
3. delay/queued-frame calculation;
4. drain condition;
5. pause/resume trigger;
6. underrun event/status path;
7. DMA address/size reporting;
8. period boundary interrupt.

Finding XGO equivalents of `get_avail` and `delay` should allow steady-state occupancy and latency to be expressed in frames rather than guessed from total ring capacity.

## Hardware gate

Not reached. The source crosswalk creates additional offline targets; no firmware candidate or hardware test is justified yet.
