# Exact XGO low-level SND clock programming supports native 11025 and 22050 Hz

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **BIN — EXACT-XGO HARDWARE CONFIGURATION SUPPORT CLOSED**

## Major fidelity closure

Earlier family evidence showed that related HC15xx systems can run I2SO natively at 22050 Hz.

The stock XGO binary now provides stronger evidence:

> XGO's own low-level active SND clock/rate programming routine contains explicit native cases for both **11025 Hz** and **22050 Hz**.

Therefore the frontend's forced low-rate conversion to 44100 is a software policy choice, not an absence of low-level XGO rate programming.

## Active call chain [BIN]

The active sound configuration path includes:

```text
0x80306CDC
  -> 0x80306514
       -> 0x8030C0DC(SND/clock state, sample_rate)
```

`0x80306514` passes the selected sample rate into `0x8030C0DC` on the active configuration branch.

The higher-level `0x80306CDC` currently normalizes:

```text
11025 -> 44100
22050 -> 44100
44100 -> 44100
48000 -> 48000
```

before that low-level configuration is reached.

## Low-level explicit rate cases [BIN]

`0x8030C0DC` contains direct comparisons and distinct register-programming sequences for multiple rates, including:

```text
8000
16000
32000
...
11025
22050
44100
...
48000
```

The relevant exact-XGO branches include:

### 11025

At approximately `0x8030C368`:

```text
compare requested rate with 11025
 -> program clock/control registers
 -> return through common success path
```

### 22050

At approximately `0x8030C3E4`:

```text
compare requested rate with 22050
 -> program a distinct clock/control combination
 -> return through common success path
```

### 44100

The next comparison at `0x8030C4D4` uses the 44100 constant loaded in the preceding delay slot and enters the 44100 programming body at `0x8030C4DC`.\n\nThis address correction is important MIPS evidence discipline: the earlier checkpoint identified the right supported rates but attached the labels one branch too early by overlooking the comparison-chain delay slots.

These are not dead family-source declarations; they are machine-code cases in the exact preserved XGO firmware and are reached from the active sound-device configuration stack.

## Consequence

The existing low-rate conversion:

```text
FBA 22050 -> x2 repeat -> 44100
SNES 11025 -> x4 repeat -> 44100
```

is not required merely because the XGO low-level clock programmer lacks those source rates.

This substantially upgrades the native-rate fidelity lead:

```text
family native-rate evidence: UP
exact XGO low-level rate cases: BIN
```

What remains unproven is whether the complete board/output path is stable and acceptable when the higher-level normalization is bypassed.

## Important latency warning

Native low-rate output is **not automatically a latency improvement**.

The lower queue admission threshold is currently:

```text
482 cursor units
1 cursor unit = 4 stereo S16 frames
```

If the same threshold is retained while the hardware output rate is reduced:

```text
44100 -> 43.719 ms threshold depth
22050 -> 87.438 ms threshold depth
11025 -> 174.875 ms threshold depth
```

Likewise a native 576-source-frame block without x2/x4 expansion would occupy 144 cursor units, but its represented wall-clock duration remains:

```text
22050: 26.122 ms
11025: 52.245 ms
```

So a naive “just stop upsampling” patch could improve sample fidelity while increasing the wall-clock depth represented by the unchanged lower admission threshold.

That is exactly why fidelity and latency must remain separate experimental lanes.

## SNES rate mismatch remains

Native 11025 hardware output would remove the x4 zero-order-hold conversion, but it would **not** repair the fixed-183 producer mismatch:

```text
183 * 60 = 10980 frames/s produced
native drain = 11025 frames/s
```

The same 0.408% long-term deficit remains.

Thus SNES has two independent fixes to evaluate:

1. native/better-rate conversion for fidelity;
2. fractional producer correction for rate accuracy.

## Candidate-design implication

A future native-rate experiment must explicitly decide what to do with lower queue policy.

Possible isolated experiments later may include:

- native rate with stock threshold, measuring fidelity only;
- native rate plus threshold rescaled to preserve approximately the original time-depth;
- improved 44.1-kHz resampling while leaving lower timing untouched.

Do not combine these in the first hardware candidate.

## Evidence boundary

Proven:

- exact XGO low-level clock/rate branches for 11025 and 22050;
- active call chain from sound configuration to that routine;
- higher layer currently prevents those rates from reaching it by normalization.

Still OPEN:

- complete exact-board analog behavior at native 11025/22050;
- whether all SND/DAC subblocks tolerate those rates identically;
- whether external AV route remains correct;
- best threshold scaling policy.

## Hardware gate

Not reached.
