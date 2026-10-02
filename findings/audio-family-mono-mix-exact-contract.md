# Maintained family mono-mix implementation and XGO implications

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **UPSTREAM FAMILY SOURCE; XGO POLICY INFERENCE ONLY**

## Pinned source

`Trademarked69/sf2000_multicore` at pinned commit:

`d973e5dd0bfe5a77ea7a11f42391e7f39294e8b0`

File:

`src/libretro_frontend/core_api.c`

## Exact maintained-family behavior [UP]

The maintained frontend installs a mono-mixing wrapper for single-speaker output.

For batch audio it iterates interleaved S16 stereo frames and computes:

```c
left_out = (left >> 1) + (right >> 1);
right_out = right;
```

The source comment explicitly states that the mix is placed in the first channel for the single speaker and that the second channel is left unchanged because it is not heard on that output.

The single-sample wrapper uses the same contract:

```c
mixed = (left >> 1) + (right >> 1);
data[0] = mixed;
data[1] = right;
```

It then forwards the stereo-shaped buffer to the stock batch callback.

## What this establishes

For this maintained SF2000-family frontend:

- the software authors treat the physical single-speaker path as effectively consuming the **first digital channel**;
- they intentionally fold both source channels into that first channel;
- they do not need to duplicate mono into both channels to make the internal speaker preserve right-only content;
- they retain the original right channel in the second transport channel.

This is stronger family precedent than the earlier generic statement that the maintained frontend performs a mono mix.

## Arithmetic detail

The implementation uses:

```text
(L >> 1) + (R >> 1)
```

rather than a wider intermediate `(L + R) / 2`.

For ordinary signals this is an averaging fold with bounded S16 range. Integer rounding differs by at most a small least-significant amount from a widened sum/divide implementation.

## XGO relevance [INF, not promoted to BIN/HW]

XGO's stock software transport is independently proven to remain two-channel and the physical specimen has one internal speaker.

The family implementation therefore supplies a plausible low-risk **shape** for an XGO internal-speaker preservation experiment:

```text
channel 0 = mono fold of L+R
channel 1 = original R
```

Advantages over duplicating mono into both transport channels:

1. internal first-channel speaker would receive both L and R content if XGO follows the family wiring;
2. second channel remains original rather than being destroyed globally;
3. downstream ABI/ring/SND geometry remains stereo S16.

But this must not yet be promoted to an XGO candidate because exact XGO analog/AV routing is still OPEN.

If external AV exposes both DAC channels, this policy would produce:

```text
external L = mono(L,R)
external R = original R
```

which is not faithful stereo.

Thus family precedent solves the **single-speaker missing-channel mechanism**, but does not solve route policy.

## Comparison with historical XGO Arcade Test13

Test13 used:

```text
M=(L+R)/2
L=M
R=M
```

That guarantees either downstream channel contains all ordinary content, but destroys stereo everywhere.

The maintained-family approach instead uses:

```text
L=M
R=R
```

which is sufficient if the internal amplifier is wired to channel 0 and is less destructive to channel 1.

The correct eventual XGO choice depends on proving which digital channel feeds L23/internal amplifier and what the AV connector exposes.

## Next evidence target

Search XGO/family board and driver evidence for:

- DAC channel-to-internal-amplifier wiring;
- whether L23 gates only the channel-0/internal-speaker analog branch;
- whether AV exposes both channels;
- whether LCD/TV detection can safely select mono-fold policy.

## Hardware gate

Not reached.
