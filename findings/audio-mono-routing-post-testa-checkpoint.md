# XGO audio mono-routing — post-Test-A investigation checkpoint

Date: 2026-10-02
Branch: `research-audio-mono-routing`
Status: **BIN/UP/INF closure — one hardware/electrical boundary remains**

## Protected ancestor

This branch starts from merged main after the native-22050 Test A promotion.

Protected audio behavior:
- FBA source remains fixed at 367 frames/emulated frame;
- FBA hardware playback uses native 22050 Hz;
- the two 22050 -> 44100 zero-order-hold repetition decisions are bypassed;
- full requested regression suite passed;
- rejected Test B 367/368 modulation remains negative evidence.

Do not alter that transport while investigating mono routing.

## XGO facts already closed

**BIN**
- libretro/frontend PCM is interleaved stereo S16: L16,R16, four bytes/frame.
- lower SND transport is configured for two channels.
- stock callback copies both channels; no software mono fold precedes the frontend ring.
- L23 is the known XGO audio mute/internal-amplifier gate.
- LCD/TV detector reads GPIO L15 at `0x8035C70C`.
- LCD/TV switching changes display/video controls including L24/R05, but does not call L23, volume control, or reconfigure the recovered PCM/SND path.

**HW**
- specimen has one physical internal speaker.

Therefore the digital two-channel transport and one-speaker acoustic output are separate proven facts.

## Maintained-family precedent

Pinned maintained SF2000-family frontend source uses:

```text
L' = (L >> 1) + (R >> 1)
R' = R
```

for single-speaker output.

The family authors explicitly put the fold in the first digital channel and leave the second channel unchanged. This is strong UP evidence that a related single-speaker implementation consumes channel 0 for the internal speaker.

It is **not** XGO proof.

## What offline evidence now rules out

The stock XGO LCD/TV transition does not contain a software audio-route switch. Consequently there is no existing stock branch we can simply intercept to prove:

```text
LCD = internal mono
TV  = external stereo
```

L15 can identify the display mode, but BIN evidence does not establish the electrical audio topology behind the AV connector.

A permanent global fold remains unsafe because it could alter external stereo if AV receives both DAC channels.

## Minimal diagnostic boundary

The old Arcade Test13 demonstrated an available pre-ring interception point at:

```text
retro_audio_sample_batch_cb  0x8035E7D8
run_sound_advance            0x8035CBA0
call site                    0x8035E800
```

That old candidate duplicated averaged mono into both channels and belongs to obsolete lineage; it must not be reused as firmware.

For the current investigation, the desired diagnostic is narrower and based on the HW-PASS Test-A lineage:

- no resampler/rate/scheduler/queue changes;
- preserve stereo-shaped S16 transport;
- synthesize unmistakably different left/right diagnostic content only under a controlled probe;
- determine which digital channel(s) are audible from the built-in speaker;
- separately characterize AV only if the user's physical setup exposes audio there.

A normal-game subjective comparison is weaker than a channel-identification probe because many game mixes are centered.

## Remaining boundary

Offline archaeology cannot establish PCB-level channel wiring from the firmware evidence presently preserved.

Exactly one question remains before choosing permanent mono policy:

> On this exact XGO specimen, does the built-in speaker reproduce digital channel 0, channel 1, or a hardware combination of both?

If channel 0 only is HW-proven, the maintained-family asymmetric fold becomes a strong XGO candidate:

```text
internal: L' = half(L)+half(R), R' = R
```

If channel 1 only is proven, the symmetric policy must be mirrored.

If both are already hardware-summed, no software fold should be added.

External AV stereo remains a separate preservation check before any permanent global policy.

## Gate

The hardware gate is now reached, but the next candidate must be a **diagnostic channel-identification build**, not a permanent mono patch.
