# Arcade Refresh — cache/lifecycle and command-6 closure

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **SRC/BIN ARCHITECTURE CLOSURE — NO HARDWARE CANDIDATE**

## 1. Resolve the apparent count-cache contradiction

Earlier notes appeared to conflict:
- native scanner notes describe a 4-byte-per-list array at `0x80D2894C`;
- the enrichment helper lineage uses FC/SFC/MD cache addresses `0x80D2894C / 0x80D28954 / 0x80D2895C`, an 8-byte stride.

Repository recovery already closed this during Test125: these are **different implementation conventions** and must not be mixed.

The HW-proven enrichment/helper lineage used by the final GB/GBC/GBA helpers is the 8-byte descriptor/cache lineage:

```
FC  -> 0x80D2894C
SFC -> 0x80D28954
MD  -> 0x80D2895C
GB  -> 0x80D28964
GBC -> 0x80D2896C
GBA -> 0x80D28974
```

This is not evidence that Arcade continues the same linear table. The Arcade browser/list IDs are 7..10 in the resource table, but no repository HW-proven helper currently pins their cache words. Therefore do not extrapolate `0x80D2897C..` into code without current-binary proof.

For Arcade, safest first design is to avoid a guessed cache write. Either:
1. recover exact Arcade cache/state words from current BIN/browser code; or
2. route completion through a native lifecycle that reloads the selected Arcade page without a direct custom cache poke.

Option 1 remains preferred for deterministic parity.

## 2. Current golden command-6 behavior is precisely bounded

Current golden firmware SHA:
`ea442b74bdc07cd5e05ec2de8da5c997848a76ed3125681c1955fbcb29b66152`

The final GBC/GBA dispatcher continuation at `0x80A397E0` has:
- command 4 -> GBC body;
- command 5 -> GBA body;
- command 7 -> exact CLASSIC unwind + `s5=0; j 0x80A38000`;
- command 6/default -> existing native No New Games path.

Thus Arcade command 6 currently has **no mutation path and no helper ABI to preserve**. The new Arcade implementation can be introduced as a command-6-only extension while leaving commands 0..5 and 7 byte-identical.

This is the ideal regression boundary.

## 3. Correct command-6 execution shape

Do not make command 6 mean one stock list. It is an orchestrator for four independent family workers:

```
command 6
  -> CPS1 descriptor/worker
  -> CPS2 descriptor/worker
  -> IGS descriptor/worker
  -> NeoGeo descriptor/worker
  -> aggregate result
  -> existing native Refresh status/epilogue
```

Result aggregation follows existing Refresh semantics:
- any family failure -> Refresh Failed;
- otherwise any family addition -> Games Updated;
- otherwise -> No New Games.

A family with an empty/nonexistent import directory is a zero/no-change result, not a failure.

## 4. Worker split

Keep materialization and catalog mutation conceptually separate even if later linked into one helper.

Materializer responsibilities:
- scan only its authoritative family import folder;
- validate bounded `.zip` filename;
- resolve optional matching TXT/JPG/JPEG;
- refuse destructive same-name/different-content collisions;
- place/verify `/ARCADE/bin/<driver>.zip`;
- generate/verify `/ARCADE/<friendly>.zfb`.

Catalog responsibilities:
- load exact family triplet;
- validate equal counts/offset structures;
- compare generated outer ZFB filename against slot0;
- stable append only missing ZFB identities;
- preserve all old indices/order;
- append friendly title to slot1/slot2;
- commit with transaction/recovery discipline;
- invalidate/reload only the exact family frontend state once its address/lifecycle is BIN-closed.

## 5. Size/loader decision

Do not force the Arcade implementation into the tiny firmware cave. The current project already has HW-proven external-helper loading/execution.

Preferred architecture:
- firmware command 6 remains a small dispatcher/orchestrator;
- Arcade implementation lives in external fixed-size helper(s), source-built and hash-pinned;
- large JPEG/materialization/catalog logic stays outside `bisrv.asd`;
- firmware delta can remain command-6 routing + path/descriptor data.

Whether to use:
A. one common `ARCADE/refresh.xgc` with four descriptors, or
B. one tiny orchestrator plus per-family helpers
remains an implementation-size decision.

Prefer A if the existing proven JPEG/materializer code can be specialized cleanly and the loader budget permits it. Prefer B only if fixed-size/proven runner constraints make A unsafe.

## 6. Family order

Use deterministic stock page order:
```
CPS1 -> CPS2 -> IGS -> NEOGEO
IDs 7 -> 8 -> 9 -> 10
```

Do not use DY19's swapped IGS/NeoGeo ordering.

## 7. Failure atomicity across families

Each family is its own catalog transaction. Do not create a four-family global transaction that rolls back already-completed independent families.

If CPS1 succeeds and CPS2 later fails:
- CPS1 remains a valid committed addition;
- command result reports failure;
- next invocation sees CPS1 idempotently as unchanged and retries CPS2 onward.

This matches practical per-system Refresh semantics and limits recovery scope.

## 8. Current next BIN task

Before implementation emission, recover from the current golden firmware:
- exact Arcade browser count/state access for list IDs 7..10;
- page-entry reload path after a zeroed/invalidated count;
- any per-Arcade-family state adjacent to count;
- command-6 available cave/continuation bytes relative to current `0x80A397E0` decoder;
- exact generic-runner contract and safe external-helper size strategy in the current cumulative image.

No hardware test is needed for these questions.
