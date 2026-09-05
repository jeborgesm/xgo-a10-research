# XGO stock libretro audio transport and timing

Status: **corrected and confirmed by direct disassembly of the stock FBA AV-info path, frontend audio callback, run loop, and sound-driver initialization**.

## Correction to earlier interpretation

An earlier version of this finding treated the stock run-loop values:

```text
PAL  sound_len = 3528
NTSC sound_len = 2940
```

as enforced per-frame PCM byte budgets and therefore inferred a hard-wired 44.1-kHz frontend pacing model.

That interpretation is **not supported by the executable data flow**.

Direct reference analysis of the preserved XGO firmware shows that the globals receiving `3528` and `2940` are written during PAL/NTSC setup but are not subsequently read by executable code. The values are associated with the diagnostic string:

```text
pal_ntsc:%d system_clock:%d sound_len:%d
```

and should not be treated as a ring-buffer consumption quota.

The actual stock audio transport accepts the sample count supplied by each core.

## Batch callback ABI

`retro_audio_sample_batch_cb` at `0x8035e7d8` forwards:

```text
a0 = sample buffer
a1 = frame count
```

to `run_sound_advance` at `0x8035cba0`.

`run_sound_advance` computes:

```text
byte_count = frame_count << 2
           = frame_count * 4
```

and copies exactly that many bytes into the circular stock PCM buffer.

Therefore the stock libretro boundary is standard:

```text
interleaved stereo signed 16-bit PCM
4 bytes per libretro audio frame
```

There is no sample duplication or 2x expansion in this callback.

## The core-advertised sample rate drives sound-driver initialization

After the active core's `retro_get_system_av_info` callback returns, `run_emulator()` reads the `sample_rate` double, converts it to an integer, and passes it to the stock sound-driver initialization path at `0x8035c998`.

Thus the frontend does **not** force every core to 44.1 kHz.

## Stock FBA explicitly advertises 22.05 kHz

The stock arcade wrapper installs:

```text
gfn_get_system_av_info = 0x8036c028
```

Inside that function the preserved firmware loads the double at:

```text
0x809a50a8 = 22050.0
```

The stock FBA load path independently initializes:

```text
nBurnSoundRate = 22050
nBurnSoundLen  = 367
```

Therefore stock arcade's effective libretro/sound-driver boundary is genuinely based on **22.05-kHz audio**, not 48 kHz and not a hidden 44.1-kHz frontend requirement.

The FBA audio batch sent by `retro_run()` is copied into the ring buffer at the count actually supplied by the core.

## Scheduler timing is frame-period based

The stock run loop uses the region callback to select ordinary PAL/NTSC cadence:

```text
PAL:
  nominal fps        50
  frame period       20 ms
  diagnostic usec    20000
  diagnostic sound_len 3528

NTSC:
  nominal fps        60
  frame period       17 ms
  diagnostic usec    16667
  diagnostic sound_len 2940
```

The values actively used by the timing loop are the millisecond period and FPS bookkeeping.

The adaptive frameskip decision compares elapsed time against the current frame period. If the frontend is more than one additional frame period late, it invokes the active core's private `gfn_frameskip(1)`; otherwise it invokes `gfn_frameskip(0)`.

For stock FBA that hook disables drawing while continuing emulation and audio.

## Consequence for external cores

The previous rule that an external core must advertise 44.1 kHz to fit the stock scheduler is withdrawn.

The actual compatibility requirements are:

- standard stereo signed 16-bit libretro audio;
- a truthful sample rate in `retro_get_system_av_info`;
- audio batches whose frame counts correspond to that core's own sample production;
- compatibility with the stock sound driver at that advertised rate.

A 44.1-kHz external core can still work naturally because the sound driver is initialized from the core's advertised rate, but 44.1 kHz is not a scheduler requirement.

## Conserved stock-FBA optimization

Family comparison now shows that XGO, SF2000 08/03 and GB300 v2 all retain the vendor FBA configuration:

```text
22050 Hz
367 samples/frame
```

This is a conserved HC15xx-family arcade optimization layered together with:

- C68K as the ordinary 68000 backend;
- adaptive render-only frameskip;
- alternating FBA frame buffers;
- stock frontend frame pacing and audio-ring transport.

## Confidence

### CONFIRMED

- stock audio callback copies exactly `frames * 4` bytes;
- audio format is stereo signed 16-bit PCM;
- `run_emulator()` initializes the sound driver from the core-advertised sample rate;
- stock FBA advertises `22050.0`;
- stock FBA initializes `nBurnSoundRate = 22050` and `nBurnSoundLen = 367`;
- `3528/2940` are not read back as executable ring-buffer quotas;
- scheduler lateness decisions are driven by frame-period timing.

### SUPERSEDED

The earlier claim that stock XGO's per-frame audio scheduling is hard-wired to 44.1 kHz is superseded by this corrected data-flow analysis.
