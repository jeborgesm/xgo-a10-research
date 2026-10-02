# Native 22050 FBA experiment has a three-word stock-binary patch surface

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN PATCH-SURFACE CLOSURE — NO FIRMWARE CANDIDATE BUILT**

## Goal

Identify the smallest isolated binary change that can test native 22050-Hz FBA playback while preserving:

- stock 60-Hz scheduler;
- stock 576-source-frame frontend quantum;
- stock 960 hardware-count value;
- stock 482 lower admission predicate;
- SNES 11025->44100 behavior;
- Audio OSD and all protected gameplay behavior.

The exact stock binary exposes a remarkably small patch surface.

## 1. Stop normalizing 22050 to 44100

In `0x80306CDC`, low-rate configuration distinguishes 11025 and 22050.

For 22050, the current body reaches:

```text
0x80306E00  ori v0,zero,0xAC44     ; v0 = 44100
0x80306E04  sw  v0,0x100(s1)      ; selected hardware rate
0x80306E08  sw  s2,0x104(s1)      ; retained source rate = 22050
```

A native-22050 experiment only needs the selected hardware-rate value at +0x100 to remain 22050.

The natural one-word replacement is conceptually:

```text
v0 = s2
```

at `0x80306E00`, leaving the following stores and the 11025 branch untouched.

The already-proven low-level configuration then receives 22050 and enters the dedicated native 22050 divider branch.

## 2. Disable x2 conversion for 22050 in submission path

The PCM submission callback `0x802FDF54` contains two structurally parallel paths selected by another object state.

Both paths test retained source rate +0x104 against 22050 before calling the repetition helper.

First comparison:

```text
0x802FDFC4  lw    v1,0x104(s3)
0x802FDFC8  li    v0,22050
0x802FDFCC  bne   v1,v0,0x802FE014
...
0x802FDFE4  jal   0x802FDED4
0x802FDFE8  a3 = 22050
```

Second comparison:

```text
0x802FE064  lw    v1,0x104(s3)
0x802FE068  li    v0,22050
0x802FE06C  bne   v1,v0,0x802FE0B4
...
0x802FE084  jal   0x802FDED4
0x802FE088  a3 = 22050
```

Changing the two 22050 comparison immediates to a value that normal configuration never supplies makes 22050 take the ordinary non-low-rate submission path.

The 11025 comparisons immediately following each branch remain intact, so SNES behavior is unaffected.

## Minimal conceptual patch

The isolated experiment therefore requires only three instruction-word changes:

```text
0x80306E00  selected hardware rate: 44100 -> requested 22050
0x802FDFC8  bypass 22050 x2-conversion test
0x802FE068  bypass duplicate 22050 x2-conversion test
```

No code cave is required for the basic native-rate proof.

## What remains stock

Crucially, this test does **not** require changing:

```text
frontend quantum        576
frontend ring capacity  4608 source frames
sample_num              960
admission threshold     482
precision               16
channels                2
scheduler               60 FPS
SNES 11025 conversion   x4 -> 44100
mono/stereo policy      unchanged
```

This is exactly the isolation wanted for the first hardware fidelity test.

## Expected data path

Stock FBA:

```text
367-frame callbacks
 -> 576-source-frame frontend blocks
 -> x2 repeat to 1152 @44100
 -> lower SND
```

Native experiment:

```text
367-frame callbacks
 -> 576-source-frame frontend blocks
 -> no repetition: 576 @22050
 -> native 22050 SND clock
```

PCM byte traffic through the conversion/lower-copy boundary is approximately halved.

## Known limitation of this first proof

The fixed-367 producer remains:

```text
367 * 60 = 22020 frames/s
```

so this minimal native-rate proof retains the small 0.136% long-term producer/drain deficit.

That is intentional.

The first test answers only:

> Does native 22050 improve CPS1/FBA sound quality and remain stable on the exact XGO hardware?

If successful, rate correction can be added as a separate second experiment.

## Why not correct the rate simultaneously?

Combining native output with a new fractional converter would prevent attribution:

- if sound improves, we would not know whether native clocking or rate correction mattered;
- if sound breaks, we would not know whether the low-level clock or new converter caused it.

The three-word proof is therefore the cleanest hardware boundary.

## Safety / reversibility

This note identifies addresses and semantics only.

No patched firmware ZIP has been produced yet.

Before building, the three original instruction words should be pinned byte-for-byte and the resulting image should be checked against the protected firmware-modification rules established after Test106.

## Hardware gate

**Nearly reached for the first CPS1 fidelity A/B test.**

Remaining offline work is to pin exact original/replacement words and verify that the stock lower submission path accepts the unexpanded 576-frame descriptor without another hidden 44.1-kHz assumption.
