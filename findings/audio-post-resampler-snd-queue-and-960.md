# Audio post-resampler SND queue and 960 semantics

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN ARCHAEOLOGY — NO HARDWARE CANDIDATE**

## Scope

Continue from the closed low-rate path:

```text
576 source frames
 -> 0x8035C4A8
 -> device +0x70 / 0x802FDF54
 -> 22050: 1152 frames @ 44100
 -> 11025: 2304 frames @ 44100
 -> lower SND path
```

Direct stock-firmware disassembly was used. Preserved `bisrv.asd` SHA-256: `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.

## 960 is a lower SND working-buffer count [BIN]

The constant 960 is supplied by the SND/I2SO setup callers, not by the libretro frontend and not by the low-rate repetition helper.

The setup routine retains this value in lower-driver state and derives transfer/buffer geometry from it together with precision/channel configuration. It is therefore a **lower SND working-buffer count**, independent of the frontend's 576-source-frame dequeue.

It must not be labeled a libretro audio quantum, source-frame budget, or resampler output size.

## Queue boundary [BIN]

The post-resampler descriptor is handed into a lower SND producer path that has its own working-buffer/transfer state before the hardware register layer.

This establishes a second queueing boundary below the already closed frontend PCM ring:

```text
frontend ring
 -> 576-source-frame dequeue
 -> optional 2x/4x repetition
 -> lower SND working-buffer/transfer state
 -> I2SO/DAC
```

Thus emulator-to-DAC latency cannot be calculated from frontend-ring occupancy alone.

## Why 576 and 960 do not need to match [BIN/INF]

The two numbers belong to different contracts:

- 576 is the **source-domain frontend consumer quantum**.
- 960 is a **lower SND setup/working count**.

The resampler output for low-rate cores is 1152 or 2304 frames, so there is no one-block identity between frontend dequeue and the lower 960 count. The driver is permitted to span/refill lower working regions across frontend submissions.

## Latency consequence [INF]

A full latency number remains premature. The proven contributors now include at least:

1. occupancy ahead of the consumer in the 4,608-source-frame frontend ring;
2. one 576-source-frame submission block boundary;
3. lower SND working-buffer/transfer occupancy;
4. hardware/I2SO/DAC serialization.

Only (1) and (2) have exact source-domain geometry. The lower queue's normal occupancy and hardware consumption cadence are still OPEN.

## Underrun boundary [BIN/OPEN]

The frontend consumer still waits rather than fabricating a partial/zero block when fewer than 576 source frames are available. The lower SND layer can therefore continue consuming whatever was already accepted below that boundary while the frontend waits.

What the DAC emits after that lower accepted audio is exhausted remains OPEN until the lower empty/underrun branch is closed.

## 960 — safe wording

Use:

> `960` is a stock lower-SND working/configuration count used in the I2SO setup path.

Do not use:

> `960` is the PCM ring period / libretro block size / resampler output block.

The exact unit attached to the lower count still needs one more closure at the DMA/register programming boundary.

## Next target

Trace the lower working-buffer indices/thresholds and the hardware-consumption interrupt/refill path. Specifically close:

- the exact unit of 960;
- number of 960-unit regions/periods resident;
- producer/consumer or DMA ownership transition;
- empty/underrun behavior;
- additional milliseconds queued below the resampler.

Then compare the same lower path against SF2000/GB300 family references.

## Hardware gate

**Not reached.** No hardware candidate is authorized.
