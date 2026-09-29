# Arcade Test12 — four-family Test11 parity

Date: 2026-09-28

User-directed scope: preserve Test11 HW-PASS behavior and apply the same procedure to CPS1, CPS2, IGS/PGM and NeoGeo before adding quarantine or cleanup complexity.

No validator-policy redesign. No quarantine/rename. No artwork workspace cleanup. No hardcoded game names. No fixed import counts.

CPS1 is preserved byte-for-byte from Test11 HW PASS:
- 5a3abb3cfe9841fc761f7778ae0b9cfc53afdd335d5f6393dc326e18e233549d

Mechanical family specializations:
- CPS2 81fc5a43f57aad69e89ac9e951750bfa4ffeb362d7c64cc361aa716c92a7bf68
- IGS 71b5fb9740b1ef73a604bc7592e12506367125f8cc3a6483342e1d9243bdd26c
- NEOGEO 049276b684dc606ac101ae1005ff785ae296772f4724b6f827f17d70ab699d6c

Shared:
- compat-safe.xgc 503eb939cb5124a4ae71eecf427b238a511ab3db79addbc4bc87270cf59faed1
- .xgo-compat 86a798ab9e0c8042a84b99a37fcfacd8708706d0010e0459726420d92ab7c0f5

NeoGeo's longer .refresh-set pathname does not fit the inherited 0x24-byte CPS1 slot. It is relocated to verified-zero +0x3000 and the single staging-path reference at +0x21D8 is retargeted. The obsolete CPS1 staging literal is zeroed. This is a mechanical path-capacity specialization, not a behavior change.

Package:
- xgo-arcade-test12-four-family-parity.zip
- SHA256 1851cc99485a25ac16235cef5e049a63a88e2e293adc4e15a257ea93800566bf

HW objective: with known-compatible ROM(s) in each desired family import folder, one Refresh should process the populated families through the same Test11 procedure. Verify additions, artwork and launch per populated family. Cleanup and incompatible-file policy remain explicitly deferred.


## HW result — CPS2 PASS

Test ROM: compatible `1944.zip` set (the second supplied archive, host/XACM result COMPATIBLE: 0 missing, 0 size mismatches).

Observed on hardware:
- Refresh processing completed;
- CPS2 entry was added;
- artwork displayed;
- launch read the ZIP contents and then showed a black screen for a noticeably long interval;
- after the extended load, the game started and ran successfully.

Result: **CPS2 four-family-parity path PASS.** The initial black screen is load latency for this working set and must not be recorded as a launch failure.

The earlier supplied modern/encrypted-layout 1944 archive reached publication but did not establish gameplay and remains separate evidence for later validator tightening. Per scope freeze, validator cleanup remains deferred until family parity is complete.


## Combined IGS + NeoGeo HW probe — Refresh Failed

User tested IGS `theglad.zip` and NeoGeo `bstars.zip` together and Refresh returned **Refresh Failed**.

Immediate offline XACM recheck against the exact Test12 manifest:
- IGS `theglad`: **COMPATIBLE**, 0 unresolved required ROMs, 0 size mismatches.
- NeoGeo `bstars`: **INCOMPATIBLE** with the XGO compiled `bstars` contract: unresolved required `002-p1.bin`.

Correction: the earlier recommendation that the supplied `bstars.zip` was a valid Test12 NeoGeo candidate was wrong; archive-shape inspection was insufficient and should not have replaced exact XACM validation.

Because Test11-family preflight maps incompatible/unsupported to no-change rather than validator error, the incompatible `bstars` alone does not yet explain an aggregate Refresh Failed. The next discriminating HW probe is IGS `theglad` alone (remove NeoGeo import candidate) to determine whether the failure is in the IGS family specialization/materializer or only appears in combined-family execution. Do not change validator/cleanup architecture during this isolation.


## Isolation result — IGS specialization FAIL; NeoGeo candidate correctly withheld

Further HW isolation:
1. Removed `theglad`, left `bstars` NeoGeo candidate alone -> **No New Games**. Nothing added. This is consistent with current preflight withholding the XACM-incompatible `bstars` set and is not a NeoGeo materializer execution result.
2. Removed `bstars`, restored compatible `theglad` in IGS import -> **Refresh Failed**. Nothing added.

Therefore Test12 family parity currently stands:
- CPS1 PASS
- CPS2 PASS
- IGS FAIL before successful publication; family specialization/build must be investigated offline
- NeoGeo NOT YET TESTED through materialization because the supplied bstars set was rejected at preflight

Do not attribute the original combined failure to simultaneous-family execution. The isolated IGS path reproduces Refresh Failed by itself.
