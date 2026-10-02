# Native-22050 lower descriptor path is rate-agnostic after conversion bypass

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — FINAL LOWER-PATH GATE CLOSED FOR MINIMAL NATIVE PROOF**

## Question

Before building a native-22050 CPS1 proof, one concern remained:

> Does the lower write/service path assume that every 22050 source block has already been expanded to 44100?

Direct binary inspection now closes that concern.

## Rate-specific logic is localized before generic submission

In the active PCM callback `0x802FDF54`, the only 22050-specific decisions are the two already identified conversion branches:

```text
0x802FDFC8  compare retained source rate with 22050
...
0x802FE068  compare retained source rate with 22050
```

When selected, they call `0x802FDED4`, replace the descriptor source pointers with scratch `0x80D1CD78`, and double the descriptor frame count.

When those comparisons are bypassed, the original descriptor remains:

```text
source pointer = frontend PCM
frame count    = 576
format         = stereo S16
```

and falls through the same generic descriptor-building/write path used by non-low-rate PCM.

## No downstream 22050 conversion dependency [BIN]

A scan of the active lower submission/service region after the conversion branch finds no additional 22050-rate comparison before the SND hardware configuration layer.

The 22050 constants in the active audio region are confined to:

- low-rate repetition selection;
- high-level normalization/configuration;
- low-level clock/rate programming.

The lower queue/copy/service machinery itself operates on:

- descriptor frame/count values;
- channel/precision format;
- cursor units;
- buffer offsets;
- commit/playback cursors.

It does not reclassify 576 frames as invalid merely because the hardware clock is 22050.

## 576-frame generic shape is already normal

A 576-frame stereo-S16 descriptor is not exotic to the lower path.

The fixed frontend consumer always emits 576 source frames.

For native-rate profiles, the generic path already handles that count without the low-rate scratch expansion.

The low-rate helper is therefore an optional preprocessing stage rather than a structural requirement of the lower descriptor contract.

## Low-level hardware rate path is independent

The selected hardware rate stored at private +0x100 is passed through:

```text
0x80306514
 -> 0x8030C0DC
```

where the exact XGO binary contains the dedicated 22050 divider/programming case.

Thus the proposed minimal native path is coherent end-to-end:

```text
FBA source PCM       22050 metadata
frontend block       576 stereo S16 frames
conversion helper    bypassed
descriptor count     remains 576
lower queue          generic frame/count path
SND hardware clock   dedicated native 22050 configuration
```

## No 960 change required for the proof

The 960 `sample_num` / hardware-count configuration remains untouched.

Its coupled 482 admission ceiling remains untouched.

The exact FBA queue model shows that native 22050 does not require the queue to fill to that ceiling.

Therefore there is no remaining software-contract reason to change 960 merely to perform the native-rate A/B proof.

## Remaining uncertainty is now hardware-only

The remaining question is no longer a missing software contract.

It is:

> Does the exact physical XGO audio output sound correct and remain stable when its already-present native 22050 clock configuration is actually used for continuous CPS1/FBA playback?

That is a genuine hardware-test boundary.

## What the first proof should NOT include

The first native candidate should not also change:

- 367 producer rate correction;
- frontend quantum;
- lower admission threshold;
- auto-resume;
- mono folding;
- scheduler;
- SNES;
- transition gating.

Those are subsequent isolated experiments.

## Hardware gate

**Reached for the minimal native-22050 FBA fidelity proof.**

The three-word patch manifest plus LCFG reseal procedure is sufficient to produce the first controlled A/B artifact when the investigation moves from archaeology to hardware testing.
