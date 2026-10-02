# Native 22050 reduces FBA downstream PCM work as well as removing zero-order hold

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN + ARITHMETIC PERFORMANCE LEAD**

## Why this matters for heavy CPS1 games

The native-rate experiment is not only a fidelity change.

Stock FBA takes each 576-source-frame block and:

1. reads 576 stereo S16 frames;
2. writes 1152 repeated frames into scratch `0x80D1CD78`;
3. submits/copies the expanded 1152-frame block through the lower SND path.

Native 22050 bypasses the repetition helper and submits the original 576-frame block at the native clock.

## Sustained PCM bandwidth

At the actual fixed-367/60-Hz producer cadence:

```text
source frames/s = 22020
stereo S16      = 4 bytes/frame
```

Original source stream:

```text
22020 * 4 = 88,080 bytes/s
```

Stock x2 conversion produces:

```text
44040 output frames/s
44040 * 4 = 176,160 bytes/s
```

So native output halves the PCM byte rate presented to the lower SND path.

## Scratch-write elimination

The stock x2 helper additionally writes the expanded stream into the fixed scratch buffer before lower submission.

That is approximately another:

```text
176,160 bytes/s
```

of sequential scratch writes, plus source reads and loop/control work.

Native 22050 eliminates that expansion pass entirely.

At minimum, compared with the stock low-rate path, the native experiment removes roughly:

- 176 KB/s of expanded scratch writes;
- about 88 KB/s of excess lower PCM payload versus native;
- the per-frame repetition loop/control overhead.

This is not a huge bandwidth number on a modern machine, but XGO is a constrained HC15xx-class device running CPU-heavy emulation, so removing unnecessary work from the audio path is directionally valuable.

## What it does not reduce

Native rate does **not** reduce:

- CPS1 CPU emulation;
- YM/ADPCM/QSound synthesis cost inside FBA;
- libretro callback frequency;
- frontend producer copies of the original source stream;
- video rendering cost.

Therefore it cannot rescue a game whose core emulation is fundamentally too slow.

But if a heavy CPS1 title is near the real-time boundary, eliminating unnecessary audio expansion is preferable to adding a more expensive resampler before first proving native output.

## Why native rate should precede linear interpolation

A 44.1-kHz linear/interpolating resampler would improve fidelity over zero-order hold but would retain:

- doubled output PCM bandwidth;
- scratch output;
- interpolation arithmetic.

Native 22050 potentially improves fidelity **and** reduces downstream work.

Given the user's priority of stable CPS1 gameplay audio, that makes native 22050 the stronger first A/B experiment if the remaining lower-path assumptions close.

## Rate-correction sequencing

The first native proof intentionally retains the small fixed-367 deficit.

If native playback is stable and audibly cleaner, a second candidate can add exact 22020->22050 fractional correction.

That second change should be evaluated specifically for recurring micro-underrun/choppiness rather than bundled into the native-clock proof.

## Hardware gate

No candidate built yet.
