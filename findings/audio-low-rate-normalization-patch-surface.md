# Low-rate normalization state and native-rate patch surface

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — ARCHITECTURE/PATCH SURFACE ONLY, NO CANDIDATE**

## Purpose

Exact-XGO low-level code now proves native 11025/22050 rate programming exists.

This note closes where the higher layer prevents those rates from reaching the hardware and why bypassing only one branch would be incomplete.

## Active configuration function

`0x80306CDC` receives:

```text
a0 = sound object
a1 = requested/source sample rate
a2 = sample_num
a3 = precision
```

The function retains the requested rate in `s2`.

Private sound state contains three important words:

```text
+0x100 = selected hardware-facing sample rate
+0x104 = retained source/original sample rate
+0x108 = sample_num
```

## Low-rate normalization [BIN]

The branch around `0x80306DC0..0x80306E0C` explicitly recognizes:

```text
11025
22050
```

For either low source rate it writes:

```text
private +0x100 = 44100
private +0x104 = original 11025 or 22050
private +0x108 = sample_num
```

The selected `+0x100` value is then reloaded into `s2` and passed as the sample-rate argument to:

```text
0x80306514
 -> 0x8030C0DC
```

Thus the low-level hardware routine never sees 11025/22050 during normal emulator playback even though it has explicit cases for both.

## Why changing only the hardware-rate branch is insufficient

The PCM submission path separately checks the retained source rate at private `+0x104`.

For:

```text
+0x104 = 22050
```

it invokes x2 frame repetition.

For:

```text
+0x104 = 11025
```

it invokes x4 frame repetition.

Therefore simply changing:

```text
+0x100 = source rate
```

without also changing the conversion decision would feed expanded PCM into a lower hardware clock running at the original low rate.

That would be incorrect.

A true native-rate experiment must keep these two decisions coherent:

```text
selected hardware rate
conversion ratio
```

## Minimal conceptual native-rate contract

For a future experiment, the intended *conceptual* state would be:

### FBA

```text
source/original = 22050
hardware rate   = 22050
conversion      = 1x
```

### SNES

```text
source/original = 11025
hardware rate   = 11025
conversion      = 1x
```

This is an architecture statement, not authorization to patch/build.

## Better implementation principle

Rather than special-casing “do not repeat” independently, the eventual conversion decision should logically derive from:

```text
hardware_rate / source_rate
```

when the ratio is one of the proven supported paths.

That prevents the selected clock and PCM expansion from silently disagreeing.

Any implementation must still preserve the existing 44100/48000 paths and be tested separately from queue-threshold changes.

## Lower-threshold warning

Native rate changes the time represented by one cursor unit while the current threshold remains 482 units.

Therefore a native-rate fidelity candidate and a latency-preserving threshold-rescale candidate are distinct experiments.

Do not hide threshold rescaling inside the first native-rate test.

## Hardware gate

Not reached.
