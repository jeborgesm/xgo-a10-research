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
