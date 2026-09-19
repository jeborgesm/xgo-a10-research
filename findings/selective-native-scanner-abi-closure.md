# Selective native-scanner ABI closure and Test103 patch shape

Continued static audit after commit 1163462a.

## Native scanner ABI is now closed enough for a surgical selective call

Correct scanner entry:
- 0x807DAE4C
- input: a0 = stock list ID
- MD list ID = 2
- return: v0 = -1 failure, 0 no additions, 1 additions
- preserves/restores s0-s7 and ra
- uses stock $gp and native globals

The Test97 selective dispatcher does not write $gp anywhere in 0x80A386BC..0x80A38854, so a direct call from the dispatcher retains the same stock GP context used by the original caller.

## Required native workspace is initialized BEFORE the selective hook

Original Refresh function performs this before 0x807DB67C jumps to our selector:

```
807DB64C  lw    s0,-3228(gp)
807DB650  lui   t0,0x0210
807DB654  addu  s0,s0,t0
807DB658  lui   t0,0x807e
807DB65C  addiu t0,t0,-18132
807DB660  sw    s0,0(t0)          # -> 0x807DB92C

807DB664  lui   t9,0x0006
807DB668  addu  t0,s0,t9
807DB66C  addiu t0,t0,4096
807DB670  lui   t1,0x807e
807DB674  addiu t1,t1,-18128
807DB678  sw    t0,0(t1)          # -> 0x807DB930

807DB67C  j     0x80A386BC        # selective hook
```

Scanner 0x807DAE4C immediately loads 0x807DB92C at entry. Therefore the selective hook is reached only after the native scanner workspace has been initialized exactly as in the stock/cumulative path.

## List-to-triplet table confirmed

Scanner computes table index = list ID + 1, each entry 12 bytes. Table at 0x80A3C32C resolves:

- list 0 FC  -> rdbui.tax / fhcfg.nec / nethn.bvs
- list 1 SFC -> urefs.tax / adsnt.nec / xvb6c.bvs
- list 2 MD  -> scksp.tax / setxa.nec / wmiui.bvs
- list 3 GB  -> vdsdc.tax / umboa.nec / qdvd6.bvs
- list 4 GBC -> pnpui.tax / wjere.nec / mgdel.bvs
- list 5 GBA -> vfnet.tax / htuiw.nec / sppnp.bvs

Thus a0=2 is unambiguous for MD.

## Minimal MD selective patch

Current Test97 MD catalog stage:

```
80A387D8  lui   a0,0x80A4
80A387DC  addiu a0,a0,<MD/catalog.xgc>
80A387E0  li    a1,2642
80A387E4  jal   0x80A382E0
80A387E8  nop
80A387EC  li    t0,0
80A387F0  slt   t1,v0,t0
80A387F4  bne   t1,zero,FAIL
...
80A387FC  or    s0,s0,v0
```

Surgical replacement can occupy the existing four setup/call words:

```
80A387D8  li    a0,2
80A387DC  jal   0x807DAE4C
80A387E0  nop
80A387E4  nop
80A387E8  nop
```

Existing return handling from 0x80A387EC onward remains valid unchanged:
- v0 < 0 -> Refresh Failed
- s0 |= v0
- s0 != 0 -> Games Updated
- s0 == 0 -> No New Games

No custom MD/catalog.xgc execution occurs.

This is a very small firmware diff and restores the exact native scanner/list ABI that Test75 used after enrichment.

## Native scanner no-change semantics

Tail confirms:
- successful update -> v0=1 at 0x807DB560
- no additions -> v0=0 at 0x807DB56C
- error cleanup -> v0=-1 at 0x807DB598

This exactly matches the selective dispatcher aggregation contract.

## Important unresolved persistence detail

0x807D40A8 was previously labeled remove(path). That label is now suspect and must be corrected before designing any transaction layer. It is a wrapper around 0x802ABC30; the call sites/argument behavior do not cleanly match the prior remove interpretation.

Do NOT design backup/rename/sync logic using 0x807D40A8 until its ABI is identified.

## Current gate

The native scanner substitution itself is now statically well-supported, but do not package Test103 yet. Next:
1. fully map scanner persistence calls and identify 0x807D40A8 / filesystem durability behavior;
2. determine whether native scanner already issues a flush/commit operation after catalog writes;
3. identify safe native rename/unlink/sync primitives if present;
4. design recovery protection around a known-consistent catalog triplet;
5. only then prepare a single controlled candidate.
