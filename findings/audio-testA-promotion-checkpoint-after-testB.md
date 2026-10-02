# XGO gameplay audio — Test A promotion checkpoint after Test B rejection

Date: 2026-10-02
Branch: `research-audio-fidelity-latency`
Status: **HW-PROVEN AUDIO CHECKPOINT**

## Promoted checkpoint

Promote Test A, not Test B, as the current gameplay-audio checkpoint.

Test A firmware:

- SHA-256: `060093e8fd2a3fa559c9b43e207c4bb495de82e87519b672a799d19b304b20b7`
- LCFG CRC-32/MPEG-2: `0x17CBBF35`
- protected cumulative ancestor: `b5f1651b146b52070f2e89d51cc2694852af565150568f78d06404e9f9f461ab`

Semantic delta remains exactly:

- `0x80306E00: 0x3402AC44 -> 0x02401021` — use requested 22050 hardware rate for stock FBA;
- `0x802FDFC8: 0x24025622 -> 0x24025623` — bypass first 22050 x2 repetition path;
- `0x802FE068: 0x24025622 -> 0x24025623` — bypass second 22050 x2 repetition path;
- LCFG CRC reseal.

No stereo-to-mono, scheduler, frontend quantum, lower threshold, Mapper, Refresh, CLASSIC, or Audio OSD change.

## Hardware evidence

Test A: **PASS**.

Observed on Street Fighter II:

- sound good;
- no noticed missing sounds;
- a small slowdown did not leave audio persistently delayed behind gameplay.

Test B then held Test A constant and added alternating FBA producer length 367/368. Test B: **FAIL**, constant background crackling across all games tested.

This negative control strengthens the decision to preserve the stock fixed 367-sample FBA producer quantum.

## Closed decisions

1. Native 22050 transport is retained.
2. Stock FBA fixed 367-sample producer quantum is retained.
3. The 22020-versus-22050 nominal producer mismatch is documented but not corrected by per-frame `nBurnSoundLen` modulation.
4. Stereo-to-mono remains out of scope; it was not required for the successful Test-A result.
5. No further rate/cadence patch is justified without a concrete residual defect observed on Test A.

## Next gate

Before merging/promoting Test A into the cumulative golden lineage, perform focused regression on the existing protected features affected or plausibly adjacent to the generic audio path:

- stock Arcade: SFII plus Cadillacs & Dinosaurs;
- one 11025-Hz/SNES case to verify the untouched 11025 repetition path;
- Audio OSD volume-button behavior;
- normal exit/return from gameplay;
- one representative non-Arcade console launch;
- Refresh/CLASSIC need only smoke verification because Test A's mechanical diff does not touch those regions.

If these remain intact, merge Test A as the audio improvement and close the rate-conversion branch rather than introducing another audio experiment.
