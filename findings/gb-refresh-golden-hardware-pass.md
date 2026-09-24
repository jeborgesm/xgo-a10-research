# Game Boy Refresh — golden hardware checkpoint and preservation record

Date: 2026-09-24  
Branch: `research-refresh-gb-gbc-gba`  
Status: **HARDWARE PASS / GOLDEN CHECKPOINT**

## Final hardware result

The complete Game Boy Refresh path is hardware-proven:

```text
/GB/import/<source>.gb
        |
        v
GB/refresh.xgc
  - accepts two-character .gb suffix
  - derives the complete stem
  - resolves metadata title
  - creates stock-style .zgb wrapper
        |
        v
GB/catalog.xgc
  - scans top-level /GB/*.zgb
  - detects wrappers missing from the stock GB triplet
  - appends the synchronized catalog records
        |
        v
native Refresh status / frontend
```

The controlled fixture used during closure produced `/GB/Tetris.zgb`. The final hardware test succeeded after the explicit catalog stage was made reachable. The existing wrapper was propagated into the GB stock catalog/list without requiring wrapper recreation.

## Golden artifact identity

Hardware-passed package:

`xgo-gb-md-parity-complete-two-stage.zip`

SHA-256:

`21bcc7e18459244912469035bd3dd4a10e0f2ae6b9b1905985a126ecfe73f71d`

Members relevant to GB:

```text
bios/bisrv.asd
SHA-256 b4b1ffa3e92c61d042b77345a21c16d67fcf586c8af6127dbc545997942f5542
LCFG CRC-32/MPEG-2 0xBB3E41F0

GB/refresh.xgc
size 1,056,520
SHA-256 34f4714ecbe5affc97b7a0b87726944c253286c3baa3531e437e982174bda238

GB/catalog.xgc
size 2,642
SHA-256 66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb
```

The final package deliberately does **not** use the experimental GB `catalog-safe.xgc` / MD Test106 transaction port. GB uses the simpler Test74/Test75-style explicit catalog merge.

## What led to the working materializer

The recovered Test132 GB materializer initially rejected ordinary `Tetris.gb`. Exact binary analysis localized the first failure to helper offset `+0x009C`: the inherited FC/SFC predicate still used four-character raw-extension geometry.

For a two-character `.gb` suffix the repair is:

```text
+0x009C: 05 -> 06
ori s4,s7,0x0005 -> ori s4,s7,0x0006
```

This moves the dot test from `filename[length-4]` to `filename[length-3]` while preserving the existing case-folded `g` and `b` tests.

Hardware then proved wrapper creation, but the generated stem was clipped by one character. The inherited FC/SFC stem helper at `+0x0DCC` still removed a four-character raw suffix. The already-known MD two-character correction applied exactly:

```text
+0x0DF8: FB -> FC
adjustment -5 -> -4
```

The combined two-byte materializer SHA is the golden value above. Hardware then proved:

- `/GB/import` discovery;
- ordinary `.gb` acceptance;
- correct stem derivation;
- metadata lookup;
- metadata-derived/sanitized output title;
- correct `.zgb` wrapper generation;
- changed return -> `Games Updated`.

**Freeze this materializer.** GBC/GBA work must not modify it.

## Why wrapper creation was not enough

After the corrected materializer generated `Tetris.zgb`, the game was still absent from the visible GB list. The uploaded GB Resources triplet remained coherent at 974 records and contained no Tetris entry:

```text
GB list ID 3
vdsdc.tax / umboa.nec / qdvd6.bvs
```

This reproduced the earlier SFC boundary that led to Test74: materialization and catalog propagation are separate stages. The correct architecture is therefore explicit:

```text
materialize first -> catalog merge second
```

The Test74 SFC and Test75 FC hardware records are the relevant proven ancestors for the GB catalog merge. The later MD Test106 transaction layer solved MD-specific durability/recovery problems and is not required merely to establish GB enrichment.

## Critical dispatcher defect that delayed closure

The decisive failure was not inside the catalog helper.

The GB adapter contained the catalog code beginning at `0x80A39084`, but the materializer-only continuation still contained:

```text
0x80A3907C  j 0x80A38808
0x80A39080  nop
```

Therefore the catalog block was **dead code**. The machine executed `GB/refresh.xgc`, aggregated its result, and exited directly to the native status path. Repeated `No New Games` results after `Tetris.zgb` already existed were therefore materializer-only results; they were not evidence that either catalog implementation had run.

This also explains why the Stage2 diagnostic marker remained unchanged: the diagnostic catalog Stage1 was never reached.

A second routing defect was identified during the same audit: the intended catalog runner must explicitly load `a0 = /mnt/sda1/GB/catalog.xgc` before calling the generic helper runner. The final adapter fixes **both** requirements.

Final two-stage shape:

```text
GB/refresh.xgc
  -> v0 < 0 ? Refresh Failed
  -> s0 |= v0
  -> CONTINUE, do not exit

load a0 = /mnt/sda1/GB/catalog.xgc
load a1 = 0x0A52
call generic helper runner 0x80A382E0
  -> v0 < 0 ? Refresh Failed
  -> s0 |= v0
  -> common native status/epilogue
```

The key reachability correction is:

```text
OLD  0x80A3907C -> 0x80A38808   # exit
NEW  0x80A3907C -> 0x80A39084   # catalog stage
```

## Offline catalog audit before final hardware test

Before the final SD-card cycle, the GB catalog helper was audited against the real fixture rather than treated as a black box.

The GB helper is the Test74-style 2,642-byte merge specialized for:

```text
wrapper suffix   .zgb
directory        /GB
TAX              vdsdc.tax
NEC              umboa.nec
BVS              qdvd6.bvs
GB count cache   0x80D28964
```

The `.zgb` predicate uses the normal four-character wrapper geometry:

```text
filename[length-4] == '.'
filename[length-3] == 'z'
filename[length-2] == 'g'
filename[length-1] == 'b'
```

The actual fixture passed every offline gate:

```text
catalog count                         974
Tetris.zgb exact slot-0 duplicate     NO
.zgb predicate                        PASS
filename length 10 (<128)             PASS
missing-wrapper capacity 1/256        PASS
projected count                       975
projected TAX size                    27,536
projected NEC size                    21,764
projected BVS size                    11,544
catalog image ceiling                 65,536
```

The final hardware PASS therefore validates the predicted explicit merge behavior.

## Negative experiments retained as evidence

Do not erase these failures; they establish boundaries:

- Test132 materializer-only: `No New Games`; exact predicate geometry rejected ordinary `.gb`.
- One-byte suffix repair: wrapper materialized but stem clipped.
- Two-byte materializer repair: correct `Tetris.zgb` created with metadata-derived title; list propagation still absent.
- Native scanner after materialization: wrapper could be recreated and status could change, but Tetris remained absent because same-operation pre-materialization directory/catalog state was insufficient for this path.
- SFC-derived GB catalog attempt before route closure: `Refresh Failed`; **not valid evidence against the helper**, because catalog invocation was not correctly wired.
- MD-derived Test106 GB Stage1/Stage2 attempt before route closure: `Refresh Failed`; likewise not valid evidence that the Stage2 algorithm itself executed.
- CLEAN! bootstrap did not cure the failure; later reachability analysis showed this was looking below an execution boundary that had not been crossed.
- Stage2 `S2LOAD` diagnostic marker remained `CLEAN!`; later reachability closure explains why.
- first explicit catalog-path repair still returned `No New Games` because the old unconditional materializer exit jumped around the catalog block.
- second Test74-lineage package also returned `No New Games` for the same unreachable-code reason.
- final deep audit found the unconditional jump; correcting it produced the hardware PASS.

## Engineering rule extracted from this investigation

**Prove reachability before diagnosing a helper.**

For every future external-helper stage:

1. reconstruct the complete caller control flow offline;
2. prove the helper call is reachable from the selected command;
3. prove all call arguments, especially pathname and byte count, are initialized at that exact call;
4. prove success/failure aggregation and the return continuation;
5. run the helper algorithm against the actual filesystem/catalog fixture offline;
6. only then request a hardware test.

A helper binary can be perfectly correct and still appear broken if the dispatcher exits before it.

## GBC propagation gate

Do **not** repeat the GB exploratory sequence.

GBC must start from this hardware-proven GB architecture and mechanically specialize only the system contracts. Before the first GBC SD-card test, close all of the following offline:

- exact GBC raw-ROM extension predicate/stem geometry;
- GBC wrapper extension and top-level directory;
- GBC catalog triplet and list/cache identity;
- materializer -> catalog reachability;
- explicit catalog pathname initialization before the generic runner;
- return aggregation and native status continuation;
- real-fixture duplicate/eligibility/catalog-size simulation;
- byte-diff manifest proving GB, FC, SFC, MD and CLASSIC paths are unchanged;
- LCFG CRC reseal and final firmware hash.

No GBC candidate is authorized merely because the selector has a GBC row.

## Protected conclusion

The Game Boy Refresh implementation is now a **golden hardware checkpoint**. Future work must preserve the exact GB materializer, explicit GB catalog merge, and two-stage reachable dispatcher contract unless new hardware evidence requires a change.
