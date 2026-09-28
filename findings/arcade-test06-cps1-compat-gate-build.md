# Arcade Test06 CPS1 compatibility-gate build checkpoint

Date: 2026-09-28

## Evidence/result

The on-device compatibility Stage2 now builds successfully under the pinned Codescape GNU Tools 2019.09-03-2 workflow. GitHub Actions run 36378065831 passed.

Artifacts:
- compat-safe.xgc: 3,929 bytes, SHA256 6cf8d8bab0a26a582111336b005c057387a0ab6a6e03ec3d0eff07b37deafc8a
- compat hook: 768 bytes, SHA256 d75a1c35ac4d62bea39429880336643e5323aa2d86ed573340228348f86bc64b
- no undefined Stage2 or hook symbols
- compat_validate = 0x87180000
- Stage2 BSS end = 0x87190F75, below catalog workspace 0x87200000
- hook link base = 0x87002600, below JPEG decoder 0x87100000

The XACM was regenerated independently from exact firmware SHA256
869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf.
It reproduced the pinned manifest exactly:
- JSON SHA256 c78e74bafe327dda636f36932024c010e84d9b6e4236a63ea62e458dc7cfd6df
- XACM SHA256 86a798ab9e0c8042a84b99a37fcfacd8708706d0010e0459726420d92ab7c0f5
- 678 drivers / 10,404 ROM descriptors.

## Build failures retained

The pre-HW build cycle exposed and corrected:
1. literal \\n corruption in the C engine;
2. incorrect host compilation of device-only Reader/entry units;
3. strict-compiler misleading-indentation findings;
4. accidental removal of the compressed-size local while cleaning warnings;
5. workflow path filtering that failed to trigger on a helper-only change.

The workflow now preserves host compiler diagnostics as an artifact even on failure and triggers for tools/arcade_refresh/**.

## Test06 integration

Parent is HW-proven Test05A CPS1 materializer SHA256
2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2.

Only the external CPS1 materializer is changed:
- audited hook inserted at +0x2600 in a verified zero cave;
- +0x0530..+0x0537 replaced by j 0x87002600 / nop;
- no bisrv.asd modification;
- Test05A artwork scratch repair is preserved.

Resulting CPS1 refresh.xgc:
- SHA256 75f3106adbcac01dd406ad218b94797001b58a4774a087c4917e68d8267d97e7

Package:
- xgo-arcade-test06-cps1-compat-gate.zip
- SHA256 4bfc148c866a5526ee82a6cca08a641573cc9bfbd8c1256d7e361c35495fac7f
- includes /ARCADE/CPS1/refresh.xgc, /ARCADE/compat-safe.xgc, /ARCADE/.xgo-compat
- contains no ROM payload and no firmware image.

## First HW probe

Use the already-known incompatible modern 1941 archive but name it 1941j.zip in
/ARCADE/CPS1/import/. Both known 1941 archives are incompatible with the stock
1941j descriptor because the four Japanese program ROM descriptors are unresolved.

Expected:
- Refresh completes as No New Games;
- no 1941j publication;
- existing working 1941 remains intact/playable;
- source 1941j.zip remains in import (quarantine rename is intentionally deferred).

This is a rejection/publication-boundary probe only. Do not reopen the historical
non-reproduced Test04 freeze/cache issue.


## HW result — PASS

HW observation: with the known-incompatible archive installed as `/ARCADE/CPS1/import/1941j.zip`, one Refresh returned **No New Games** with no issues observed.

This is the first HW proof that the CPS1 compatibility gate can reject a non-publishable import without destabilizing Refresh. The rejection/publication-boundary half of Test06 is therefore HW PASS. No cache/freeze regression was observed.
