# Arcade Refresh four-family offline closure — pass 1

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **ARCHAEOLOGY IN PROGRESS — NO HARDWARE CANDIDATE**

This pass applies the repository-first and architectural-ancestor gates before any Arcade implementation.

## 1. Architectural ancestors selected

Arcade Refresh is a composite feature. No single historical implementation is the correct parent for every component.

| Component | Closest proven ancestor | Why |
|---|---|---|
| stable append / preserve indices | Test08 + Test74/Test75 | existing entries remain in place; append only; synchronized triplets |
| slot1/slot2 fallback | Test08/Test74/Test75 | basename/friendly fallback already compatible with browser/search semantics |
| catalog cache reload | stock browser + Test08 | shared count array starts `0x80D2894C`; zeroing one list slot invokes native lazy reload |
| image decode/resize | Test64-derived enrichment family | already-proven JPEG -> 144x208 RGB565 concept |
| Arcade physical wrapper | stock XGO ZFB path | Arcade ZFB is a reference object, not console WQW |
| transaction hardening | Test106 MD | only mature recoverable catalog transaction lineage |
| selector invocation | current post-GBC/GBA golden firmware | command 6 is reserved/inert and must be the only new selector route |
| CLASSIC | none | explicitly separate; list 11/MAME2000 must not be touched |

Conclusion: do not clone a console materializer wholesale and do not revive the old Test08 all-system scanner as the runtime architecture.

## 2. Exact stock family descriptors

XGO resource table establishes:

```
ID 7  CPS1
  mswb7.tax / msdtc.nec / mfpmp.bvs

ID 8  CPS2
  kjbyr.tax / djoin.nec / ke89a.bvs

ID 9  IGS/PGM
  subst.tax / aepic.nec / sensc.bvs

ID 10 NeoGeo
  rmapi.tax / pcadm.nec / ntdll.bvs
```

Original captured counts were 26 / 28 / 6 / 117.

The common count-cache base is `0x80D2894C`, indexed by list ID. Therefore the predicted cache slots are mechanically:

```
ID 7  0x80D28968
ID 8  0x80D2896C
ID 9  0x80D28970
ID 10 0x80D28974
```

Classification: the base/index rule is BIN/SRC established by the browser/Test08 lineage. The four addresses above are arithmetic consequences and remain to be instruction-level audited in the current golden binary before candidate authorization.

Important collision discovered: later handheld work records GBC/GBA caches at addresses that overlap this simple arithmetic projection. That discrepancy must be resolved from the current binary rather than assumed away. **Do not encode the projected Arcade cache addresses yet.**

## 3. ZFB evidence correction

Earlier Test06 notes inferred an Arcade ZFB layout from filename/size arithmetic:

```
thumbnail
+ four zero bytes
+ ZIP basename
+ trailing NULs
```

But Test06 and Test07 hardware both rejected parsers that assumed the wrapper was still available in `ROM_BUFFER` at the external CPS1 hook. Later BIN work closed the actual stock launch handoff differently: stock firmware had already resolved the selected archive and stores the current directory/archive filename in persistent frontend globals before the runtime hook.

Therefore:

- lightweight ZFB/reference semantics remain strongly supported by card inventory and stock path construction;
- **the exact byte boundary must not be promoted to current XGO BIN/HW proof solely from Test06 arithmetic**;
- representative physical ZFB byte audit remains mandatory before writing a generator.

This corrects the overly strong wording in the initial plan.

## 4. Family-folder classification

The proposed input namespaces remain sound:

```
/ARCADE/CPS1/import
/ARCADE/CPS2/import
/ARCADE/IGS/import
/ARCADE/NEOGEO/import
```

Family classification should come from the folder selected by the user, not from heuristics over ZIP contents.

This avoids:
- driver-database duplication in the Refresh helper;
- ambiguity in clones/parents;
- accidental cross-page insertion;
- dependence on a modern FBA/FBNeo database that may not match the XGO hybrid engine.

The importer may still validate ZIP shape/name, but it must not reinterpret the requested family.

## 5. Runtime-output model

Subject to physical-ZFB byte closure, the expected stock-shaped output is:

```
input family/import/<driver>.zip
    -> /ARCADE/bin/<driver>.zip

optional art/meta
    -> /ARCADE/<friendly title>.zfb

catalog append
    -> exactly one family triplet
```

The actual ZIP basename is runtime identity for FBA; the outer ZFB/catalog filename is frontend identity.

This separation is useful: a friendly display title does not require renaming the driver ZIP.

## 6. Idempotence/collision model

First implementation should use two identities:

```
runtime identity = driver ZIP basename
frontend identity = generated ZFB filename
```

Required decisions:

1. If target `/ARCADE/bin/<driver>.zip` already exists byte-identically, reuse it.
2. If same driver basename exists with different bytes, fail that import; never silently overwrite a working stock set.
3. If target ZFB already exists and references the same driver, reuse it.
4. If target ZFB exists but references another driver, fail as a display-name collision.
5. If family slot0 already contains exact ZFB filename, do not append.
6. If another family already catalogs that same ZFB, do not silently duplicate; record cross-family collision for explicit policy.
7. Metadata/title changes after initial import are not deletion/reconciliation; defer them rather than creating duplicate catalog identities.

## 7. Commit ordering

The catalog must never become the first committed object.

Safer order:

```
validate source ZIP/art/meta
-> materialize or verify /ARCADE/bin ZIP
-> materialize and verify ZFB
-> build complete synchronized new triplet in RAM
-> transactionally commit triplet
-> verify triplet
-> invalidate/reload affected list
-> report Games Updated
```

If materialization fails, catalog remains untouched.

For the first implementation, source files remain in the family staging folders after success, matching the console enrichment workflow.

## 8. Transaction decision

Arcade has four independent canonical triplets. The mature Test106 transaction model should be adapted per family rather than inventing another persistence protocol:

```
CLEAN state
-> ignore stale recovery copies

not CLEAN / interrupted
-> validate live/recovery
-> recover before new work

before canonical mutation
-> validate old triplet
-> create + verify recovery triplet
-> mark ACTIVE
-> write all three canonical files
-> reopen + verify new triplet
-> mark CLEAN
```

Whether one shared Arcade transaction marker or four family-specific markers is safer remains OPEN. Family-specific markers are currently preferred because Refresh can fail/recover one family without conflating the other three.

## 9. BIOS/dependency policy remains open

Do not copy a BIOS into every imported set and do not attempt to synthesize parent archives.

NeoGeo and IGS/PGM may have BIOS/parent dependencies determined by the stock hybrid FBA database. The first importer should preserve user-provided ZIPs and validate only the storage/reference contract unless XGO-local evidence proves additional files are mandatory.

A compatibility validator can be a later PC-side feature; on-device Refresh should not pretend to know a modern ROM-set database.

## 10. Offline evidence still required

Before code emission:

- obtain/read the current physical baseline's actual `ARCADE/*.zfb`, `ARCADE/bin/*`, and four catalog triplets;
- byte-decode representative ZFBs from all four families;
- build complete ZFB -> driver ZIP -> family/index matrix;
- classify the seven historical unindexed ZFBs;
- resolve the count-cache-address discrepancy against current `bisrv.asd`;
- trace command 6 from the current golden selector into the available cave/dispatcher;
- identify exact free/helper placement and size budget;
- compare Test64 JPEG worker and current handheld materializers for reusable image code;
- decide transaction-marker naming/placement;
- mechanically audit every proposed patch region before packaging.

No hardware question exists yet. Continue offline.
