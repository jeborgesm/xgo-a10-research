# In-game audio optimization scope and acceptance target

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **PROJECT SCOPE — USER TARGET**

## Primary goal

The audio investigation is now explicitly focused on **continuous gameplay**, not menu/transition polish.

Highest-priority workload:

> CPS1 / stock FBA gameplay, with Street Fighter II as a stable reference and heavier Arcade titles such as Cadillacs and Dinosaurs as stress cases.

Success means:

1. sound remains synchronized with gameplay;
2. no recurring choppiness/underrun artifacts under sustainable game load;
3. no avoidable resampling distortion;
4. latency is minimized without destabilizing playback;
5. the one-speaker output preserves meaningful content from both source channels;
6. improvements respect the physical limitation of the small internal speaker rather than trying to compensate with aggressive DSP.

## Deprioritized

Unless they are found to affect in-game playback, these are no longer gating work:

- menu-tail audio;
- transition pops;
- L23 reinit gating;
- startup/re-entry cosmetic silence;
- post-unload queue cleanup.

Existing archaeology on those mechanisms remains preserved because it documents the platform, but it should not delay gameplay-audio experiments.

## Experiment discipline

Gameplay improvements remain separated into four lanes:

### A. Rate accuracy / underrun resistance

Ensure the amount of PCM supplied per real second matches the configured hardware drain rate.

### B. Resampling fidelity

Replace or bypass the proven x2/x4 zero-order-hold repetition without silently changing scheduler behavior.

### C. Queue latency

Reduce time-depth only after rate/fidelity stability is established; do not trade lower latency for choppy CPS1 audio.

### D. Single-speaker presentation

Preserve left-only and right-only content without clipping centered material. Keep external stereo intact if an external stereo route is later proven.

## Hardware-test gate

The remaining offline deep dive should end in a **small matrix of isolated A/B candidates**.

The first candidate should not bundle scheduler, resampler, queue, mono and transition changes.

A small audible improvement is considered worthwhile if it is stable and does not regress the protected gameplay baseline.
