# Test105 deterministic recovery hardware closure

Status: HW PASS.

## Hardware sequence

Starting state:
- Test105 staged hardened MD catalog architecture already HW-proven for boot, repeated no-change Refresh, immediate MD frontend entry, artwork, launch, and gameplay.
- A deterministic complete recovery sentinel was then installed containing the coherent known-good 788-entry MD catalog generation.
- Live Resources were not replaced by the fixture.

Observed recovery invocation:
- Refresh result: "Games Updated"
- device remained responsive

Immediate post-recovery consumption, with no reboot and no second Refresh:
- Mega Drive games visible
- artwork/images visible
- games launch normally

## Evidence classification

HW:
- complete recovery-triplet presence is accepted by Test105 without freeze/reboot;
- recovery invocation completes through a successful update path;
- resulting catalog is immediately consumable by the stock frontend;
- resulting metadata/artwork relationship is healthy;
- resulting games launch normally;
- no reboot is required.

BIN + fixture construction:
- the only fixture additions were .xgo-cat-tax.bak, .xgo-cat-nec.bak, .xgo-cat-bvs.bak containing the coherent 788 generation.
- therefore the change from the previously repeatable "No new games" state to "Games Updated" is strong evidence that the recovery sentinel altered the Stage2 path as designed.

Inference:
- because the current ROM set contains games beyond the 788 generation, the intended sequence is recovery of OLD followed by normal rebuilding of the current generation. The final visible frontend state is consistent with that sequence.
- without a post-run filesystem capture, deletion of all three recovery files and exact final live-file hashes are not independently HW-observed yet.

## Closure

Test105 now has hardware evidence for:
1. unchanged-firmware boot;
2. Stage1 load of relocated Stage2;
3. repeated healthy no-change execution;
4. immediate MD frontend/artwork/gameplay;
5. deterministic complete-recovery-sentinel execution;
6. successful immediate frontend/artwork/gameplay after recovery.

Actual power-loss durability remains OPEN and should not be tested by deliberately interrupting SD writes.

Next safe validation, if desired, is a post-run SD filesystem capture to confirm:
- recovery triplet removed;
- live TAX/NEC/BVS coherent and expected;
- no unexpected files modified.

That capture is forensic confirmation only; no additional Refresh invocation is required.
