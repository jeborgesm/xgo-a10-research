# Audio low-rate conversion — exact stock algorithm closure

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC BIN CLOSURE — NO HARDWARE CANDIDATE**

## Provenance

Direct disassembly of preserved stock XGO `bisrv.asd`, size 12,768,452 bytes, SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`, runtime base `0x80000000`.

This extends the already closed path:

```text
libretro stereo S16
 -> 18,432-byte / 4,608-frame frontend ring
 -> 576-source-frame consumer quantum
 -> 0x8035C4A8 descriptor handoff
 -> audio-device +0x70 callback
```

## Concrete audio-device callback table [BIN]

The XGO audio device is allocated/configured by the driver attach path beginning at `0x80309C34`.

The callback assignments relevant to the frontend submission path are:

```text
device +0x5C = 0x802FD5A4   readiness
device +0x70 = 0x802FDF54   PCM submission/conversion path
device +0x74 = 0x80304C50   following device operation
```

Important address-recovery detail: the `+0x5C` and `+0x70` targets use `lui 0x8030` followed by a negative `addiu`; sign extension places them at `0x802F....`, not `0x8030....`.

This closes the concrete callback behind the previously identified generic device wrapper.

## Exact low-rate converter [BIN]

The `+0x70` submission callback at `0x802FDF54` checks the retained source-rate field at device-private offset `+0x104`.

For low-rate input it calls helper:

```text
0x802FDED4(source, 0x80D1CD78, frame_count, source_rate)
```

The helper selects a repetition factor from the source rate:

```text
source_rate == 22050 -> repeat = 2
source_rate == 11025 -> repeat = 4
otherwise            -> repeat = 0 / no low-rate repetition path
```

Its inner loop is mechanically simple:

```text
for each 32-bit source word:
    repeat the same 32-bit word N times into destination
```

Because the established frontend PCM ABI is interleaved stereo signed 16-bit, each 32-bit word is one complete stereo frame (16-bit L + 16-bit R).

Therefore XGO's stock 11.025/22.05-kHz conversion is **zero-order hold by whole stereo-frame repetition**:

```text
22050 -> 44100 : L,R  L,R
11025 -> 44100 : L,R  L,R  L,R  L,R
```

There is no linear interpolation, FIR filtering, averaging, or newly calculated intermediate sample in this conversion helper.

## Scratch-buffer handoff [BIN]

Low-rate input is expanded into the fixed scratch area beginning at:

```text
0x80D1CD78
```

After conversion, the submission descriptor's source pointer(s) are replaced with this scratch address and its frame/count field is scaled by the same ratio:

```text
22050 source count -> count * 2
11025 source count -> count * 4
```

The normal frontend consumer supplies 576 source frames, so one low-rate submission becomes:

| Source profile | Source frames | Expanded 44.1-kHz frames | Expanded PCM bytes |
| --- | ---: | ---: | ---: |
| 22050 Hz | 576 | 1152 | 4608 |
| 11025 Hz | 576 | 2304 | 9216 |

The time represented by the block is preserved:

```text
576 / 22050 = 1152 / 44100 ~= 26.122 ms
576 / 11025 = 2304 / 44100 ~= 52.245 ms
```

## Fidelity consequence [BIN/INF]

The major stock low-rate fidelity mechanism is now closed.

For 22.05-kHz cores, every stereo sample is held for two 44.1-kHz output frames. For 11.025-kHz cores, every stereo sample is held for four output frames.

This is the lowest-complexity integer-ratio upsampler. It preserves timing and sample values exactly but performs no reconstruction filtering or interpolation. Any audible high-frequency imaging/stairstep character introduced by this stage is therefore attributable to a proven stock algorithm rather than an inferred hardware limitation. [BIN/INF]

This finding does **not** by itself authorize replacing the algorithm. A fidelity experiment must remain separate from latency, scheduler, buffer-size, mute, and Audio OSD changes.

## 960 question narrowed again [BIN]

The conversion produces 1152 frames for a 576-frame 22.05-kHz block and 2304 frames for a 576-frame 11.025-kHz block.

Neither result is 960.

Therefore the lower-level `960` configuration value is not:

- the frontend source quantum;
- the 22.05-kHz expanded quantum; or
- the 11.025-kHz expanded quantum.

Its semantics remain downstream and independent of the integer-ratio sample-repetition stage.

## Revised end-to-end rate path [BIN]

```text
core PCM at source rate
 -> stereo S16 frontend ring
 -> fixed 576-source-frame dequeue
 -> 0x8035C4A8
 -> audio device +0x70 / 0x802FDF54
 -> if 22050: repeat each stereo frame 2x into 0x80D1CD78
 -> if 11025: repeat each stereo frame 4x into 0x80D1CD78
 -> scaled descriptor/count
 -> lower SND/I2SO submission
 -> DAC/output
```

For 44.1/48-kHz profiles this specific low-rate repetition helper is not used.

## Remaining fidelity questions

The exact **software upsampling algorithm is closed**. Remaining fidelity archaeology is now narrower:

- whether SND/I2SO performs any additional filtering/rate processing after repetition;
- whether the DAC/output path itself applies filtering;
- whether a higher-quality replacement can fit the existing scratch-buffer/count contract without changing scheduling or queue geometry;
- whether stock sibling firmware uses the same repetition helper or a different converter.

## Next offline work

1. Trace the post-conversion descriptor from `0x802FDF54` to the actual SND buffer/DMA submission and close any additional queue depth.
2. Resolve the meaning of the 960 lower-level configuration value.
3. Compare the corresponding low-rate helper in pinned SF2000 08/03 and GB300 v2 binaries.
4. Only after the downstream queue is closed, compute emulator-to-DAC latency bounds separately from this fidelity result.

## Hardware gate

**Not reached.** No hardware candidate is authorized by this finding.
