# Arcade Test07 — compatibility gate / JPEG workspace coexistence fix

Date: 2026-09-28

## Root cause of Test06 black artwork

Test06 HW proved both validator verdict directions, but a compatible newly published 1941 ZFB had an all-zero 59,904-byte RGB565 preview.

BIN comparison closed the integration error. The inherited JPEG decoder tail itself constructs and uses address `0x871821DC` (LUI 0x8718 at materializer tail offsets +0x10018C and +0x10068C). Test06 loaded compatibility Stage2 at `0x87180000`, with code/BSS through `0x87190F75`. Therefore the validator remained resident across the JPEG call and occupied the decoder's private workspace.

This is not a regression of the Test05A scratch-path repair. It is a Test06 lifetime/ownership collision at 0x8718xxxx.

## Fix

Keep the already-HW-proven validator location and gate ABI, but make Stage2 transient:
1. load Stage2 at 0x87180000;
2. validate one import;
3. preserve verdict;
4. zero 0x87180000..0x87190F7F;
5. reset loader cookie so the next ZIP reloads Stage2;
6. only then resume the compatible materialization/JPEG path or skip the incompatible item.

This avoids inventing another unproven RAM region and restores the decoder's pre-Test06 zero workspace before artwork generation.

Codescape audit run 36455464940: PASS.

Artifacts:
- compat-safe.xgc: 3,929 bytes, SHA256 `6cf8d8bab0a26a582111336b005c057387a0ab6a6e03ec3d0eff07b37deafc8a`
- resident hook: 832 bytes, SHA256 `709e14f0b91b53cd2716887d03bf902e950488620d9e48276057d109d79ef659`
- hook end: 0x87002940
- release routine: 0x870026C0
- release loop ends at 0x87190F80.

Test07 CPS1 materializer:
- parent remains HW-proven Test05A SHA256 `2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2`
- output SHA256 `f88769795c48f2dd9ba435cf56a01fb0782c4d59b68e09b4bfe388458a402f7f`

Package:
- `xgo-arcade-test07-cps1-compat-artwork-fix.zip`
- SHA256 `f63a3cc53e3e28ca1722a0a23fc5fa257bb39732fdec8e4b52963db9e59f1d87`
- no bisrv.asd, no ROM payload.

## HW probe

Use compatible 1941 import/runtime ZIPs and force regeneration of the generated 1941 ZFB. Expected: Games Added/materialization succeeds, newly generated 1941 has non-black artwork, and launches normally. This is specifically the Test06 artwork regression retest. After that passes, repeat the known-incompatible 1941j rejection once to ensure transient reload did not regress filtering.
