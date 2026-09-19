# Refresh root-cause consolidation: second-pass failure, native scanner, and safe architecture

## 1. Second MD Refresh failure is no longer evidence of an idempotency bug

The current recovered triplet is provably inconsistent:
- scksp.tax: 839 records
- setxa.nec: 839 records
- wmiui.bvs: 788 records (restored pristine backup)

MD/catalog.xgc validates the three counts before scanning:
- TAX count loaded at 0x1C4
- NEC count loaded at 0x220
- BVS count loaded at 0x27C
- 0x2D4 rejects TAX != NEC
- 0x2DC rejects TAX != BVS
- rejection returns -1

Therefore the current direct-after-reboot MD Refresh MUST return Refresh Failed at catalog stage even if MD/refresh.xgc correctly skips every existing wrapper.

More importantly, the earlier post-Test97 second-run failure occurred after the first successful Test97 update was followed by the immediate MD frontend hard-lock and forced power cycle. Windows later proved wmiui.bvs filesystem-corrupted. Thus the cleanest explanation is:
1. materializer/catalog update succeeded;
2. frontend state was stale and hard-locked;
3. forced power cycle occurred while FAT/catalog persistence was vulnerable;
4. wmiui.bvs became unreadable/corrupt;
5. next Refresh materializer could return 0, but catalog.xgc then failed opening/validating the damaged triplet.

Do NOT retain “MD second-pass/idempotency defect” as established. It is storage-confounded and presently explained by catalog corruption.

## 2. Correct native stock scanner address and architecture

The generalized native stock scanner is 0x807DAE4C (not 0x807EAE4C; the latter is data/nops in this firmware).

Test75 proven flow:
- 0x807DB67C calls custom pre-scan enrichment bootstrap 0x80A38240
- 0x807DB684..6B4 loops list IDs 0..5
- each iteration calls native scanner 0x807DAE4C
- after all stock lists, 0x807DB6B8 jumps to CLASSIC bootstrap 0x80A38000
- common status paths follow.

Test97/Test85 replaces 0x807DB67C with a jump to selective dispatcher 0x80A386BC, bypassing the entire native list scanner loop.

## 3. Native scanner does more than write catalog files

0x807DAE4C:
- loads the selected triplet into native in-memory catalog workspace;
- validates all three structures and equal counts;
- scans the selected system directory;
- compares wrapper filenames against native loaded catalog;
- constructs updated catalog structures;
- writes the triplet when additions exist;
- invalidates the selected frontend count cache at base 0x80D2894C + list*4;
- returns 1/0/-1.

Crucially, even when there are no additions, invoking this function reloads/validates the selected catalog into the native workspace used by the frontend lifecycle.

Our custom catalog.xgc instead operates on isolated buffers 0x87200000/0x87210000/0x87220000 and only clears the count cache. It does not rebuild the native catalog workspace.

This is now the strongest explanation for the immediate post-update hard-lock:
- custom catalog writes valid persistent files;
- frontend/native catalog workspace remains from before the update;
- count cache is cleared, causing frontend to consult/rebuild against inconsistent live/native state;
- entering MD hard-locks;
- reboot reconstructs native state from disk and MD works.

## 4. Minimal architecture correction

For stock systems, do NOT use custom catalog.xgc as the final catalog authority.

Preferred selective flow:
```
selected materializer refresh.xgc
        |
        v
native stock scanner 0x807DAE4C(selected list ID)
        |
        v
native in-memory catalog state + persistent triplet updated together
        |
        v
common Refresh status
```

For MD list ID = 2.

This reuses the exact native scanner that was hardware-proven in the Test75 cumulative FC/SFC enrichment path and restores the lifecycle stage Test85 bypassed.

The custom materializer remains useful because it creates enriched wrappers/artwork; native scanner then performs the stock catalog merge.

## 5. Persistence safety caveat

The native scanner itself also rewrites the three live catalog files sequentially with fopen(...,"wb"), fwrite, fclose. Therefore it is not a transactional filesystem writer either.

However, unlike custom catalog.xgc, it also maintains the native in-memory state. If this removes the immediate post-Refresh hard-lock, the dangerous forced-power-cycle immediately after catalog writes disappears.

This should be treated as the first safety repair, not the complete power-failure solution.

Before broader Refresh rollout, investigate a recoverable transaction/journal layer:
- preserve a known-good triplet before native mutation;
- use a transaction marker;
- on next Refresh entry, detect incomplete transaction and restore/repair before scanning;
- avoid deleting the last known-good triplet until new triplet is validated.

Do not introduce guessed rename/sync calls until their native ABI is proven.

## 6. Test103 gate

A Test103 hardware package is not yet authorized by this finding alone. Before building:
- statically patch a copy of Test97 selector to replace MD/catalog.xgc runner call with native scanner(list=2);
- verify register/GP/stack contract;
- verify success aggregation 0/1/-1;
- verify native scanner global workspace pointer is initialized before the hook (it is set at 0x807DB658..678, but confirm all dependencies);
- ensure no custom catalog write occurs;
- document exact binary diff and recovery procedure.

Only then consider one controlled hardware test from a known-consistent triplet.
