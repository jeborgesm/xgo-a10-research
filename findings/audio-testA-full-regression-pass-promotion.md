# XGO gameplay audio — Test A full regression PASS and promotion authorization

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **HW PASS — PROMOTION AUTHORIZED**

## Protected candidate

Test A firmware:

- SHA-256: `060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7`
- LCFG CRC-32/MPEG-2: `0x17CBBF35`
- cumulative ancestor: `b5f1651b146b52070f2e89d51cc2694852af565150568f78d06404e9f9f461ab`

Exact semantic delta remains the three-word native-22050 transport patch plus LCFG reseal.

## Hardware regression result

After rejecting Test B for constant crackling, the SD card was reverted to Test A and the requested regression suite was executed.

User result:

> reverted to test a and all the tests passed

The regression gate requested immediately before this result covered:

- stock Arcade: Street Fighter II and Cadillacs & Dinosaurs;
- SNES / untouched 11025-Hz audio path;
- Audio OSD volume-button behavior;
- normal gameplay exit/return;
- representative non-Arcade console launch;
- Refresh/CLASSIC smoke verification.

**HW: all requested checks passed.**

## Promotion decision

Test A is now authorized for promotion into the cumulative golden lineage.

This closes the experimental choice between:

```text
Test A: fixed FBA 367 + native 22050       -> HW PASS + regression PASS
Test B: alternating FBA 367/368            -> HW FAIL, constant crackling
```

The stock fixed-367 FBA producer quantum remains protected. No producer-cadence correction, stereo-to-mono patch, scheduler change, frontend-quantum change, or lower-threshold change is included.

## Closed audio behavior

Hardware evidence now supports:

- native 22050 hardware playback for the stock FBA 22050 source path;
- bypass of the old 22050 -> 44100 zero-order-hold repetition path;
- complete observed SFII audio;
- improved recovery from transient SFII slowdown without persistent audio lag;
- no constant crackling present on Test A;
- untouched SNES/11025 path remains functional;
- Audio OSD remains functional;
- gameplay exit/return and representative console operation remain functional;
- Refresh/CLASSIC smoke checks remain functional.

## Branch disposition

The rate-conversion experiment is complete enough to merge. Further audio work, if any, must start from this promoted checkpoint and address a separately observed defect rather than reopening the already-rejected 367/368 correction.
