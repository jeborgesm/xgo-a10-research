# Arcade live-list count cache — direct current-BIN closure

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **BIN CLOSED — exact Arcade browser count slots recovered**

## Why this was reopened

Test04 hardware:
- Refresh appended the CPS1 1941 catalog entry;
- immediately entering CPS1 hard-froze;
- after reboot the CPS1 catalog was readable and the new row appeared.

The Test04 Arcade catalog helper deliberately removed the inherited GBA helper's write to `0x80D28974` because that address had not been proven for CPS1.

That caution was correct. The exact browser indexing has now been recovered from the current XGO firmware.

## Direct browser code

Current `bios/bisrv.asd`, runtime `0x80357ED4..0x80357F50`, contains the live built-in-browser count calculation.

Key instructions/semantics:

```
80357ED4  3C0A80D3      lui   t2,0x80D3
80357EDC  254B894C      addiu t3,t2,0x894C
...
80357F30  8782F2A0      lh    v0,-0x0D60(gp)    # active list id
80357F34  3C1880D3      lui   t8,0x80D3
80357F3C  2706894C      addiu a2,t8,0x894C      # count-array base
80357F40  00021880      sll   v1,v0,2           # list_id * 4
80357F44  00662021      addu  a0,v1,a2           # &count[list_id]
80357F48  24050004      li    a1,4
...
```

Earlier in the same path the selected count is read through the same base/index construction.

Therefore the visible browser's count array is exactly:

```
count[list_id] = *(uint32_t *)(0x80D2894C + list_id * 4)
```

When the count is zero, the native browser's existing lazy path reads four bytes from the selected catalog into this slot.

## Exact Arcade slots

Using XGO-native list IDs:

```
7  CPS1    -> 0x80D28968
8  CPS2    -> 0x80D2896C
9  IGS     -> 0x80D28970
10 NeoGeo  -> 0x80D28974
```

These are now **BIN-authorized** live-browser invalidation targets.

## Important correction to the historical cache model

The older enrichment/catalog-helper lineage recorded an 8-byte progression:

```
FC  0x80D2894C
SFC 0x80D28954
MD  0x80D2895C
GB  0x80D28964
GBC 0x80D2896C
GBA 0x80D28974
```

That progression must not be described as the visible browser's contiguous per-list count array.

The current browser directly proves a separate 4-byte-indexed array beginning at the same base.

For example, under the current browser formula:
- list 1 FC -> `0x80D28950`
- list 2 SFC -> `0x80D28954`
- list 3 MD -> `0x80D28958`
- list 4 GB -> `0x80D2895C`
- list 5 GBC -> `0x80D28960`
- list 6 GBA -> `0x80D28964`

The overlap between some historical helper addresses and different browser-list slots explains why address-pattern extrapolation was unsafe.

This also supplies a new interpretation for earlier live-refresh anomalies such as MD: a helper could successfully mutate disk catalogs while clearing a nearby but wrong resident slot. Do not retroactively promote that interpretation to HW closure without re-auditing the exact historical candidate.

## Test04 consequence

Test04's CPS1 helper performed no Arcade count invalidation. The exact CPS1 browser slot is now known to be `0x80D28968`.

The narrow repair after a successful CPS1 triplet commit is therefore:

```
*(uint32_t *)0x80D28968 = 0;
```

The stock browser can then use its already-proven zero-count lazy reload path on next CPS1 entry.

For the four-family helpers, invalidate only the family whose catalog transaction actually committed:
- CPS1 -> `0x80D28968`
- CPS2 -> `0x80D2896C`
- IGS -> `0x80D28970`
- NeoGeo -> `0x80D28974`

No invalidation is required for an empty/no-change family.

## Evidence classification

- base `0x80D2894C`: BIN
- active-list index multiplied by 4: BIN
- lazy four-byte reload into computed slot: BIN
- Arcade list IDs 7..10 and family mapping: BIN + existing HW/resource evidence
- exact Arcade count slots above: BIN-derived arithmetic from closed instructions
- stale CPS1 count as cause of Test04 immediate-entry freeze: **strong causal hypothesis**, not yet HW-proven until repaired behavior is tested.

## Next gate

Patch the Arcade catalog-helper source to emit these exact per-family invalidations after successful commit, then mechanically audit all four helpers.

Do not add broader frontend resets unless the exact count invalidation proves insufficient on hardware.
