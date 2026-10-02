# Maintained-family single-speaker mono fold is exact and asymmetric

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **UP — PINNED FAMILY SOURCE; XGO POLICY IMPLICATION ONLY**

## Exact family implementation

Pinned source:

```text
Trademarked69/sf2000_multicore
commit d973e5dd0bfe5a77ea7a11f42391e7f39294e8b0
src/libretro_frontend/core_api.c
```

implements both libretro batch and single-sample wrappers for a single-speaker device.

Batch path:

```c
for (size_t i=0; i < frames*2; i+=2)
{
    ((int16_t*)data)[i] = (data[i] >> 1) + (data[i+1] >> 1);
    // second channel deliberately left unchanged
}
retro_audio_sample_batch_cb(data, frames);
```

Single-sample path:

```c
int16_t mixed = (left >> 1) + (right >> 1);
int16_t data[2] = {mixed, right};
retro_audio_sample_batch_cb(data, 1);
```

Thus the family frontend does **not** duplicate mono into both digital channels.

It transforms:

```text
L' = (L >> 1) + (R >> 1)
R' = R
```

and relies on the physical single-speaker route hearing the first channel.

## Why this matters for XGO

This is strong family precedent for the user's requirement that neither left-only nor right-only game content disappear on a one-speaker handheld.

For the internal-speaker channel:

- left-only survives at approximately half amplitude;
- right-only is folded into the audible first channel at approximately half amplitude;
- centered correlated content remains near its original amplitude rather than being doubled/clipped.

The implementation also avoids a potentially unnecessary write to the second channel.

## Important distinction from XGO Test13

The old XGO Arcade Test13 diagnostic used:

```text
M = (L + R) / 2
L' = M
R' = M
```

Conceptually both are ordinary half-sum mono folds for the audible channel, but the family implementation preserves the original right digital channel instead of replacing it.

That distinction is potentially valuable if the external/AV path carries stereo.

## External-stereo opportunity

If XGO's physical internal speaker consumes the first digital channel while an external route still consumes both channels, the family pattern:

```text
L' = mono
R' = original R
```

would **not preserve true external stereo**, because external left would already be folded.

Therefore the family implementation is evidence of a single-speaker strategy, not proof that it is correct for XGO's unknown external topology.

The preferred XGO policy remains:

- fold only when the internal-speaker route is active, if a reliable route discriminator can be proven;
- preserve original L/R for an external stereo route.

## Arithmetic caveat

The exact family expression:

```text
(L >> 1) + (R >> 1)
```

is overflow-safe for signed 16-bit input.

It is nearly equivalent to `(L+R)/2`, but integer right-shift rounding can differ by one least-significant unit for odd/negative values.

This difference is negligible for the architecture decision but should be preserved if reproducing family behavior exactly.

## Evidence discipline

- exact family code: **UP**
- XGO stock frontend remains stereo pass-through: **BIN**
- XGO has one physical speaker: **HW**
- exact XGO internal-speaker channel wiring: **OPEN**
- exact external/AV audio topology: **OPEN**

No global XGO mono patch is promoted from this family source alone.

## Hardware gate

Not reached.
