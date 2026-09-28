# Arcade Test08 — isolate compatibility Stage2 from JPEG workspace

Date: 2026-09-28

Test07 HW materially refined the failure: `/ARCADE/.xgo.rgb565` was successfully produced, while the newly generated ZFB preview remained zero. The root scratch placement is therefore preserved; it is not the defect.

Test07's broad clearing of 0x87180000..0x87190F7F was also rejected as an unsafe correction because the inherited JPEG machinery owns state in the 0x8718xxxx region.

Test08 returns to the exact Test06 loader/hook lifetime semantics and instead relocates the compatibility Stage2 itself:
- old Stage2 base: 0x87180000
- Test08 Stage2 base: 0x87300000
- upper assertion: < 0x87400000
- materializer hook remains at 0x87002600
- Test05A shared root scratch paths remain unchanged
- no writes/clears are made to JPEG-owned 0x8718xxxx by compatibility cleanup.

Codescape audit run 36465940966: PASS.

The purpose of Test08 is one boundary only: determine whether removing the compatibility executable/BSS footprint from 0x8718xxxx restores the already-HW-proven Test05A RGB565→ZFB artwork path while retaining compatibility filtering.


## Final offline build

Codescape run `36465940966` passed.

Audited build:
- Stage2 entry `compat_validate = 0x87300000`
- Stage2 end `0x87310F75` (< `0x87400000`)
- `compat-safe.xgc`: 3,929 bytes, SHA256 `503eb939cb5124a4ae71eecf427b238a511ab3db79addbc4bc87270cf59faed1`
- resident hook: 768 bytes, SHA256 `2a6538fdd5ef4042101fed34de51daeb69bc9927018dfc8796a633b18b067460`
- hook end `0x87002900`
- undefined symbol lists empty.

Test08 materializer was rebuilt from the exact HW-proven Test05A parent, not Test07:
- parent SHA256 `2d6503ae20937bd9d525d68a18ee845d942667b582e71e2371450a83d8d29ad2`
- Test08 refresh.xgc SHA256 `b1350ae6bdb10f11e5003fa7e32af70560c3eb4f907331c826ee6e080fc07362`

Package `xgo-arcade-test08-cps1-stage2-relocation.zip` SHA256 `ed9d1f014f5d81c0ba5a3763cbbe0257472e9e2c34754bf477a9931d7912ff24`.

First HW probe: compatible 1941 only; force regeneration of 1941.zfb. Expected: Games Added, nonzero/visible artwork, playable game. If pass, repeat incompatible 1941j on the same binary to confirm rejection remains No New Games.
