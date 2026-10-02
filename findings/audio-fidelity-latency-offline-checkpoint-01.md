# Audio fidelity / noise / latency — offline archaeology checkpoint 01

Date: 2026-09-30  
Branch: `research-audio-fidelity-latency`  
Status: **STATIC ARCHAEOLOGY ONLY — NO HARDWARE CANDIDATE**

## Scope and evidence rule

This checkpoint inventories the audio evidence already present in the repository and reconciles it against the recovered XGO firmware and family comparisons. Evidence labels follow the project convention: **HW / BIN / SRC / UP / INF / OPEN**.

The three experimental lanes remain separate:

1. fidelity / low-rate conversion;
2. noise / mute and analog-gate sequencing;
3. latency / PCM ring occupancy and consumer timing.

No scheduler, Audio OSD, buffer-size, sample-rate, resampler, or mute behavior is changed here.

## Reconciled end-to-end path

Current evidence supports the following stock path:

```text
libretro core
  -> interleaved stereo signed 16-bit PCM
  -> retro_audio_sample_batch_cb @ 0x8035e7d8
  -> run_sound_advance @ 0x8035cba0
  -> circular PCM ring (blocking producer)
  -> stock sound task / consumer
  -> HC15xx SND/I2SO
  -> DAC/output path
  -> board-specific L23 active-high mute/amp gate
  -> one physical speaker
```

### Core -> callback -> ring [BIN]

The batch callback forwards `(data, frames)` to `run_sound_advance`. The writer computes `frames << 2`, proving four bytes per libretro frame and therefore stereo signed 16-bit PCM.

The ring writer:
- computes the producer end position;
- blocks with repeated `dly_tsk(1)` when a write would collide with the consumer region;
- uses one `memcpy` for contiguous writes or two across wrap;
- advances the producer pointer only after the copy.

This producer algorithm is conserved in XGO, SF2000 08/03, and GB300 v2. The callback additionally measures writer duration and records a timing tick when the blocking call takes at least 21 ms. [BIN/UP]

### Rate selection and hardware transport [BIN]

`run_emulator()` normally initializes sound from the core-advertised sample rate. Stock FBA advertises 22050 Hz and uses 367 samples/frame. SNES family 0x08 is an explicit exception: XGO bypasses generic AV-info setup and initializes a fixed 11025-Hz stereo profile.

The vendor sound layer maps:
- 11025 -> 44100 hardware-facing rate;
- 22050 -> 44100;
- 44100 -> 44100;
- 48000 -> 48000.

The original low rate is retained separately, so low-rate handling is not merely relabeling the stream. The exact conversion/interpolation algorithm is **not yet recovered**. [BIN/OPEN]

The active HC15xx transport is two-channel, 16-bit. Active setup supports 44.1 and 48 kHz hardware-facing rates and normally receives a 960-sample working count. The 960 value is confirmed as an active configuration argument, but whether it is the DMA period, a driver staging count, or a hard hardware requirement remains OPEN. [BIN/INF/OPEN]

### Output gate [BIN/HW/INF]

GPIO L23 is driven active-high for mute/disable and low for unmuted output. The physical volume transition is ordered:

```text
new volume == 0:
    L23 = 1
    set_audio_volume(0)
else:
    L23 = 0
    set_audio_volume(nonzero)
```

L23 is also toggled around frontend/game transitions. Its semantic role as speaker/amplifier gate is strong executable evidence; the exact downstream analog component remains OPEN.

## Corrections preserved from earlier work

Two earlier interpretations must not be resurrected:

1. PAL/NTSC values 3528/2940 are diagnostic/write-only state, **not** hard PCM ring quotas.
2. An apparent GB300-only ring recovery helper was a disassembly-window artifact. The corresponding producer/blocking behavior is conserved across SF2000, GB300 v2, and XGO.

These corrections matter because neither provides evidence for a special sibling latency fix.

## Lane A — fidelity / resampling

### Established [BIN]

- libretro input to the stock ring is unmodified stereo S16 PCM;
- 11025 and 22050 source rates are normalized to a 44100 hardware-facing path;
- 44100 remains 44100; 48000 remains 48000;
- the source rate is retained separately;
- stock FBA deliberately operates at 22050/367;
- XGO SNES family 0x08 deliberately operates at 11025 stereo.

### OPEN

The repository currently establishes the **rate mapping**, not the algorithm. It does not yet prove whether conversion is:
- zero-order hold/sample repetition;
- linear interpolation;
- another fixed-ratio interpolator;
- hardware-assisted SND resampling;
- a staged software/hardware combination.

Priority static target: trace the retained source-rate field from sound initialization into the consumer/SND setup and identify the code or hardware control that expands 2:1 and 4:1 low-rate streams.

## Lane B — latency / ring and consumer

### Established [BIN/UP]

- producer is a circular ring writer with collision blocking;
- producer waits in 1-ms yields rather than overwriting unread data;
- callback duration >=21 ms is observable to the frontend timing state;
- frameskip suppresses drawing but continues emulation and audio generation;
- emulator wrappers stop the stock sound task by clearing bit 0 of `g_snd_task_flags` and waiting for the flag word to reach zero before core replacement;
- pause/audio re-entry has a sound-driver stabilization wait and timing reset.

### OPEN

The existing findings do **not** yet record:
- ring base and exact byte capacity;
- exact producer and consumer global addresses/semantics;
- consumer transfer quantum;
- refill/start threshold;
- normal occupancy;
- underrun output policy;
- maximum and typical queued milliseconds;
- whether 960 samples correspond directly to one consumer/DMA period;
- whether pause/menu entry drains, freezes, discards, or restarts queued PCM;
- whether teardown leaves unread PCM that can become stale audio.

Therefore no latency number should yet be claimed.

Priority static target: disassemble the XGO consumer paired with `run_sound_advance`, map its globals back to the producer, and derive capacity/threshold/occupancy in bytes and milliseconds at 11025, 22050, 44100 and 48000 source profiles.

## Lane C — noise / silence / mute sequencing

### Established [BIN/HW/INF]

- L23 is active-high mute/gate;
- volume zero asserts L23 before applying software volume zero;
- nonzero volume deasserts L23 before applying software volume;
- L23 also participates in frontend/game transitions;
- digital transport and analog output gate are distinct layers.

### OPEN

Static evidence has not yet closed:
- what samples the consumer submits on underrun/digital silence;
- whether DAC/I2SO continues clocking zeros while L23 is muted;
- exact stop/start ordering among ring reset, SND enable, DAC state and L23;
- whether stale queued PCM can be emitted before/after unmute;
- whether sibling firmware changes this ordering.

Priority static target: reconstruct every caller of the L23 helper together with sound init/stop/restart and the ring consumer, then compare the equivalent SF2000/GB300 gate sequencing without importing sibling GPIO identities.

## Family comparison status

Current family evidence says the **producer/ring blocking path is not better in SF2000 or GB300 v2**; it is conserved. The family comparison has not yet established a superior sibling low-rate converter, consumer threshold, underrun policy, or mute sequence.

Thus the next comparison must be mechanism-specific:
- low-rate conversion implementation;
- consumer/ring geometry;
- underrun behavior;
- gate ordering.

A sibling difference is only actionable after its semantic role is proven and translated to XGO's board-specific L23 route.

## Immediate next offline work

1. Recover exact `run_sound_advance` GP globals and ring geometry from XGO machine code.
2. Identify the paired consumer task/function and derive its read-index update, transfer quantum, threshold and underrun branch.
3. Follow the retained low source-rate field into the 44.1-kHz path to recover the exact 2x/4x conversion algorithm.
4. Enumerate L23 callers and interleave them chronologically with sound-task/SND/DAC start-stop operations.
5. Repeat those exact semantic traces against SF2000/GB300/HC15xx references.
6. Only after those are closed, calculate the queue's minimum/normal/maximum latency and decide whether any remaining question is genuinely hardware-only.

## Hardware gate

**Not reached.** No hardware candidate is authorized by this checkpoint.
