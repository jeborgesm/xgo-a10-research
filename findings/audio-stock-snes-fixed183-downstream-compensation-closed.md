# Stock SNES fixed-183 output has no compensation in the recovered frontend/downstream path

Date: 2026-10-01  
Branch: `research-audio-fidelity-latency`  
Status: **BIN — DOWNSTREAM COMPENSATION QUESTION CLOSED; SCHEDULER-CADENCE EFFECT STILL OPEN**

## Question

The built-in SNES path computes:

```text
increment = trunc(11025 / video_refresh)
```

and normal NTSC resolves to a fixed 183 source frames per emulated frame.

Does any later XGO stage restore the discarded fractional part?

## Callback-side behavior [BIN]

The SNES audio upload path maintains `pending @ GP+E904`.

Every normal audio update:

```text
pending += GP+E8F4
```

with `GP+E8F4 = 183` for the normal NTSC profile.

If `pending >= 129`, it mixes exactly `pending` stereo frames, calls the installed audio-batch callback with exactly that frame count, and then:

```text
pending = 0
```

Because 183 already exceeds 129, normal NTSC reaches the callback every emulated frame with exactly 183 frames. There is no 183/184 alternation at this boundary.

## Frontend behavior [BIN]

The stock libretro batch callback forwards the exact supplied frame count to `run_sound_advance`.

The frontend PCM ring aggregates source frames until at least 576 are available, but it does not synthesize extra source frames.

Therefore batching changes *when* the 183-frame contributions are submitted downstream; it does not restore the missing fractional source-frame production.

## Low-rate conversion [BIN]

For SNES 11025, the recovered low-rate converter repeats each incoming stereo frame exactly four times:

```text
1 source frame -> 4 output frames
```

Thus:

```text
183 source frames -> 732 output frames
```

for each normal emulated-frame contribution.

The converter contains no fractional-rate accumulator, interpolation clock correction, or occasional extra-frame insertion.

## Lower SND behavior relevant to rate [BIN]

The hardware-facing rate is normalized to 44100 for the 11025 path.

The lower queue receives the x4-expanded output. Its admission/backlog logic controls queue occupancy, but does not alter the number of output frames represented by the submitted PCM.

Therefore there is **no compensation after the SNES batch callback** for the fractional part discarded by the fixed-183 calculation. [BIN]

## Conditional long-term rate arithmetic [BIN + INF]

If emulation/audio production is paced at the same NTSC refresh value used to derive the AV profile, then source-frame production per second is:

```text
183 * video_refresh
```

For a Snes9x2005-lineage NTSC refresh around 60.1 Hz this is about 10.998 kframes/s, below the nominal 11025-Hz source rate by roughly 0.24%.

After exact x4 repetition the same proportional mismatch remains relative to the 44100-Hz hardware clock.

This arithmetic is real, but its audible/system consequence is not yet fully closed because the exact stock scheduler cadence and lower-driver response to the long-term producer/consumer mismatch must be reconciled.

Do **not** yet label it a measured pitch error.

## What compensation possibilities remain?

Downstream compensation is now excluded.

Remaining possibilities are upstream or temporal:

1. the SNES mixer itself is intentionally clocked to the fixed 183-frame cadence rather than a true 11025-Hz timeline;
2. the actual stock emulation scheduler cadence differs slightly from the AV-info refresh value;
3. the lower queue periodically reaches underrun/fade because production is slightly slower than the nominal 44100-Hz drain;
4. another upstream timing adjustment changes emulated-frame cadence.

The maintained family Snes9x2005 implementation's fractional accumulator avoids this mismatch by occasionally producing the extra frame. Stock XGO does not do so at the recovered callback layer.

## Why this matters for fidelity work

A future resampler improvement must not accidentally preserve a stock timing defect merely because it reproduces the same x4 nominal-rate contract.

Before selecting the fidelity candidate, reconcile:

```text
183 frames/emulated frame
vs
actual stock emulated-frame cadence
vs
44100 hardware drain
```

If the mismatch is genuine, the correct improvement may involve both *quality* and *rate accuracy* — but those effects must still be measured separately.

## Next target

Recover the exact stock SNES scheduler cadence/timing constant used by `run_emulator` for family 0x08 and compare it numerically against:

```text
11025 / 183 = 60.245901639... Hz
```

Only a cadence near 60.2459 Hz would make fixed 183 exactly equal nominal 11025-Hz production.

Also inspect whether the lower SND underrun-fade path would mask the resulting slow queue depletion at the actual cadence.

## Hardware gate

Not reached.
