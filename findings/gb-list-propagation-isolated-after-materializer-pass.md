# GB materializer PASS — list propagation isolated

Date: 2026-09-23
Branch: `research-refresh-gb-gbc-gba`
Status: HW boundary closure / catalog-scanner next

Hardware confirms the corrected GB materializer creates `/GB/Tetris.zgb` and returns Games Updated, but the new wrapper does not appear in the Game Boy frontend list.

This cleanly separates materialization from list propagation.

Existing BIN/SRC evidence already closes the native list identity:
- native scanner entry: 0x807DAE4C(a0=list_id)
- GB stock list ID: 3
- GBC: 4
- GBA: 5

The Test122 audit also established that stock cumulative Test75 scanned lists 0..5 before CLASSIC.

Therefore the next GB work is not another materializer change. Preserve the HW-passed GB/refresh.xgc exactly and inspect the current post-helper path for command 3. The intended terminal list stage is the stock native scanner with a0=3, executed only after the native Refresh workspace has been initialized.

Do not patch bisrv.asd casually. Post-Test100 boot evidence makes a direct firmware edit unsafe unless derived through the currently proven selector builder and boot-integrity constraints.

Next offline gate:
1. recover exact current Test123-derived command-3 dispatcher bytes;
2. identify the current GB materializer-only bypass used by Test132;
3. restore/route the post-materializer stage to native scanner 0x807DAE4C(list=3), preserving native workspace lifecycle;
4. prove no FC/SFC/MD/CLASSIC path changes;
5. build deterministically from protected current firmware; only then emit hardware candidate.

Expected result after that route is restored: existing `/GB/Tetris.zgb` should be appended/discovered by the stock GB catalog triplet and visible without changing the materializer.
