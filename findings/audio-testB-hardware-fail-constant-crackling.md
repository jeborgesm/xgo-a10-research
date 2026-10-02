# XGO gameplay audio — Test B hardware FAIL: constant crackling

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **HW FAIL — REJECT Test B**

## Candidate

Test B firmware SHA-256:

`4b4f7f1008bfe965e063b206b8680024fb4ab5f52b556678ce1bb243b5a50d21`

Test B preserved the HW-PASS Test A native-22050 transport and added only the FBA producer cadence correction:

```text
367, 368, 367, 368, ...
```

selected before the FBA frame engine from existing per-`retro_run()` counter parity.

## Hardware result

**FAIL.**

User report:

> No, I don't like this one, it has a background constant crackling noise, in all the games tested.

The defect was not game-specific in the tested sample: constant background crackling was heard across all games tested.

## Comparison to Test A

Test A had previously passed hardware testing:

- sounding good;
- no noticed missing sounds;
- transient SFII slowdown did not leave audio persistently behind gameplay;
- no stereo-to-mono change.

Test B introduces a new constant crackling artifact that was absent from Test A.

Therefore Test B is rejected and must not supersede Test A.

## Interpretation

**HW:** Alternating FBA's producer length between 367 and 368 every emulated frame is not acoustically acceptable on XGO, despite its mathematically exact 22050-frame/s average.

**INF:** The FBA audio generators and/or downstream block-boundary behavior are sensitive to changing `nBurnSoundLen` frame-to-frame. Exact average sample count is insufficient if the producer quantum itself changes each emulated frame.

**INF:** The prior fixed-367 mismatch (22020 generated frames/s versus nominal 22050) is not presently worth correcting by variable `nBurnSoundLen`, because Test A already sounded good and this correction creates a materially worse artifact.

This result does **not** prove that the 30-frame/s mismatch is harmless in every circumstance. It proves that this specific producer-domain correction strategy is worse than the HW-PASS Test A behavior.

## Decision

1. Revert hardware SD to Test A.
2. Preserve Test A as the current positive audio checkpoint.
3. Do not promote Test B to golden.
4. Do not add stereo-to-mono as a reaction to this failure; Test B did not change channel policy and Test A already demonstrated acceptable sound without a mono patch.
5. Do not pursue another producer-length modulation candidate unless new evidence identifies a concrete residual Test-A defect that justifies it.

## Research consequence

The experiment bought a clear result:

```text
fixed 367 + native 22050 transport     -> HW PASS / sounds good
alternating 367/368 + same transport   -> HW FAIL / constant crackling
```

The preferred engineering direction is therefore to keep FBA's fixed producer quantum and Test A's native-rate transport intact rather than forcing mathematical rate exactness at the FBA per-frame generation boundary.
