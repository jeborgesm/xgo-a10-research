# XGO Audio Fidelity / Noise / Latency Investigation

Date: 2026-09-30
Branch: `research-audio-fidelity-latency`

## Mission

Investigate whether XGO audio fidelity, noise behavior, and latency can be improved while preserving normal device operation and every current golden feature.

This is an archaeology-first investigation. No hardware candidate is authorized until offline evidence identifies one narrow unknown that cannot be resolved statically.

## Protected baseline

Start from merged `main`, including:
- Mapper v19 and per-game mapping persistence
- CPS1 pacing/performance work
- Audio OSD v8 behavior
- cumulative Refresh work
- CLASSIC runtime/save-state work
- four-family Arcade Refresh golden closure through NeoGeo Test28

Do not regress, reconstruct from memory, or replace a proven implementation when the exact implementation is recoverable.

## Known XGO audio contract

Current evidence establishes:
- libretro audio boundary: interleaved stereo signed 16-bit PCM
- batch callback copies exactly `frames * 4` bytes
- core-advertised sample rate drives stock sound initialization
- stock FBA advertises/uses 22050 Hz; lower rates are normalized through the 44.1-kHz hardware path
- HC15xx SND/I2SO transport is two-channel and 16-bit
- normal hardware-facing rates include 44.1 and 48 kHz
- normal lower-level working block observed: 960 samples
- one physical speaker
- GPIO L23 is the XGO speaker/amplifier mute gate
- stock volume API accepts arbitrary uint8 values; frontend's historical 0/33/66/99 policy was not a transport limitation
- Audio OSD must remain outside the audio hot path

## Investigation lanes

Keep these independent:
1. Fidelity / resampling
2. Noise / mute / analog-gate sequencing
3. Latency / ring-buffer occupancy and consumer timing

Do not combine behavioral changes across lanes in one hardware candidate.

## First offline questions

1. Recover the complete producer/consumer path from core batch callback through circular PCM buffer, SND/I2SO consumer and DAC/output gate.
2. Recover the exact 11025/22050 -> 44100 normalization/interpolation algorithm.
3. Determine circular-buffer capacity, read/write indices, refill threshold, normal occupancy, underrun behavior, and whether 960 samples is a hard hardware contract or vendor batching choice.
4. Determine queue/reset behavior across frameskip, pause, menu entry/exit, sound restart and emulator teardown.
5. Determine what reaches the DAC during digital silence and the exact ordering of L23 mute/unmute versus buffer/SND transitions.
6. Compare XGO with recovered SF2000/GB300/family implementations before inventing a replacement.

## Evidence discipline

Label conclusions HW / BIN / SRC / UP / INF / OPEN.

GitHub is the source of truth. Important findings must not exist only in chat.

Failed experiments remain evidence. Golden artifacts are immutable.

Do not infer physical SD state from an incomplete uploaded archive.

## Hardware gate

Before requesting hardware testing, record:
- exact unresolved question
- exact HW-proven ancestor and hashes
- exact patch surface
- mechanical binary audit
- why offline archaeology cannot answer it
- one expected observation that distinguishes the competing hypotheses

One test must buy one clear piece of information.

## Safety / preservation rules

- No broad sound-driver replacement.
- No blind buffer-size reduction.
- No sample-rate increase merely because a higher number sounds preferable.
- No audio callback instrumentation in the first phase.
- No scheduler modification as part of an audio-quality experiment.
- Preserve L23 mute semantics unless the experiment is specifically about gate sequencing.
- Preserve Audio OSD v8 exactly.
- Preserve core compatibility and normal frontend/menu/save behavior.
- Prefer policy-only or algorithm-only changes over importing an entire sibling runtime.
- Compare exact binaries/source before patching.
- Stop and document contradictions rather than patching around them.

## Initial direction

The first work is static archaeology only. The likely high-value surfaces are:
- quality of the conserved low-rate -> 44.1-kHz conversion;
- actual buffered milliseconds between libretro callback and DAC;
- mute/unmute and queue behavior that could cause pops, hiss, stale audio, or avoidable delay.

No firmware candidate should be emitted merely to begin the investigation.
