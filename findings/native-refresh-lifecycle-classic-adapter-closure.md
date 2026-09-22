# Native Refresh lifecycle map — CLASSIC-only adapter closure

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **BIN closure from recovered Test75/Test92 binaries; no hardware candidate yet**

## Result

The missing control-flow detail is now closed far enough to explain Test92 and define the safe CLASSIC-only adapter shape.

The Refresh handler is a real function beginning at `0x807DB5CC`. It saves essentially the complete caller-visible machine state before any scanner/module work.

### Entry prologue

Recovered Test75 firmware:

```text
807DB5CC  addiu sp,sp,-0xB0
807DB5D0..638
          save v0,v1,a0-a3,t0-t7,s0-s7,t8,t9,gp,fp,ra
807DB63C  mfhi  t0
807DB640  sw    t0,0x7C(sp)
807DB644  mflo  t0
807DB648  sw    t0,0x80(sp)
```

This is important: CLASSIC was historically entered while this Refresh frame was live.

## Native workspace initialization

Before module selection/scanning:

```text
807DB64C  lw    s0,-3228(gp)
807DB650  lui   t0,0x0210
807DB654  addu  s0,s0,t0

807DB658  lui   t0,0x807E
807DB65C  addiu t0,t0,-18132
807DB660  sw    s0,0(t0)          # 0x807DB92C

807DB664  lui   t9,0x0006
807DB668  addu  t0,s0,t9
807DB66C  addiu t0,t0,4096

807DB670  lui   t1,0x807E
807DB674  addiu t1,t1,-18128
807DB678  sw    t0,0(t1)          # 0x807DB930
```

Thus both native catalog-workspace pointers are initialized while the Refresh frame is active.

## Test75 cumulative path

```text
807DB67C  jal   0x80A38240        # stock enrichment pre-scan
807DB680  nop

807DB684  move  a0,s4
807DB688  lui   t9,0x807E
807DB68C  addiu t9,t9,-20916      # 0x807DAE4C
807DB690  jalr  t9                # native scanner(list=s4)
807DB694  nop
807DB698  bltz  v0, failure
807DB69C  beqz  v0, next
807DB6A4  li    s5,1              # aggregate changed
807DB6A8  addiu s4,s4,1
807DB6AC  li    t0,6
807DB6B0  bne   s4,t0,807DB684
807DB6B4  nop

807DB6B8  j     0x80A38000        # CLASSIC bootstrap wrapper
807DB6BC  nop
```

## CLASSIC bootstrap is a continuation, not an ordinary callable function

At `0x80A38000`:

```text
80A38000  addiu sp,sp,-0x18
80A38004  sw    ra,0x14(sp)
80A38008  sw    s5,0x10(sp)
80A3800C  jal   0x80A38050        # external-helper loader
...
80A38014  restore s5
80A38018  restore ra
80A3801C  addiu sp,sp,0x18
```

Then it does **not return with `jr ra`**.

It branches directly into the still-live native Refresh function's status continuations:

```text
helper < 0       -> 0x807DB718     # Refresh Failed
helper > 0       -> 0x807DB6C0     # Games Updated
helper == 0 and
stock changed    -> 0x807DB6C0     # Games Updated
helper == 0 and
stock unchanged  -> 0x807DB6EC     # No New Games
```

This is the exact reason Test92's direct call was structurally unsafe.

The bootstrap assumes:
- the `0x807DB5CC` Refresh frame exists;
- saved registers/HI/LO exist at that frame's offsets;
- `s5` contains the prior changed aggregate;
- the common status continuation will perform the final full epilogue.

Calling `0x80A38000` from an unrelated selector frame therefore eventually jumps into a Refresh epilogue that restores registers from the wrong stack layout.

That is a concrete BIN explanation for the Test92 hard lock.

## Native common status continuations

```text
UPDATED:
807DB6C0  state/status = 1
807DB6D0  jal 0x8030FEC8
807DB6D8  store return in 0x807DB93C
807DB6E4  -> common epilogue

NO CHANGE:
807DB6EC  state/status = 2
807DB6FC  jal 0x8030FEC8
807DB704  store return in 0x807DB93C
807DB710  -> common epilogue

FAILED:
807DB718  state/status = 3
807DB728  jal 0x8030FEC8
807DB730  store return in 0x807DB93C
```

Common epilogue begins `0x807DB73C`, restores HI/LO and the complete saved register set, then releases the `0xB0` Refresh frame.

Therefore these status paths must only be reached from a valid Refresh frame.

## Safe CLASSIC-only adapter shape

We do **not** need to synthesize a fake lifecycle frame and we do **not** need to call the bootstrap from the menu.

The native Refresh entry already creates exactly the required frame and workspace. The lowest-risk adapter is a dispatch branch **after** workspace initialization:

```text
native Refresh entry 0x807DB5CC
        |
        v
full native save frame
        |
        v
workspace init through 0x807DB678
        |
        v
module selector
        |
        +-- CLASSIC selected:
        |      li s5,0
        |      j 0x80A38000
        |
        +-- stock selected:
               module-specific path
```

For CLASSIC-only execution, `s5=0` is the correct aggregate seed because no stock module has reported a change.

This preserves:
- native Refresh frame;
- native workspace setup;
- stock `$gp`;
- CLASSIC helper loader;
- helper result mapping;
- native status display;
- native complete epilogue.

It skips all six stock scanners and therefore does not mutate unrelated stock catalogs.

## Test92 binary confirms the mistake

Recovered Test92 firmware changes `0x807DB67C` to:

```text
807DB67C  j 0x80A386BC
```

Its selector handles CLASSIC selection by ultimately jumping to:

```text
80A38854  j 0x80A38000
```

But the selector itself first allocates/restores its own `0x20` stack frame and does not reproduce the stock loop's `s5` initialization semantics. The historical direct CLASSIC route was therefore mixing two continuation conventions.

The correct replacement is simpler: while still inside the native Refresh frame, branch to the CLASSIC continuation with a defined `s5=0`.

## Consequence for final UI

This closes the CLASSIC invocation problem independently of the ugly Settings UI.

The future REFRESH GAMES selector only needs to communicate a module ID into the native Refresh function. The Refresh function itself can own dispatch after `0x807DB678`.

The UI must **not** call module internals.

```text
native UI list
   |
   | selected module ID
   v
native Refresh entry
   |
   | owns frame + workspace + module dispatch
   v
module
   |
   v
native status + epilogue
```

That separation is the target architecture.

## Evidence status

- Refresh prologue/frame: **BIN**
- workspace initialization: **BIN**
- stock scanner loop: **BIN + prior HW lineage**
- CLASSIC transition `0x807DB6B8 -> 0x80A38000`: **BIN + HW**
- CLASSIC external helper behavior: **HW**
- status continuations/epilogue relationship: **BIN**
- Test92 direct-path hard lock: **HW**
- stack/continuation explanation for Test92: **BIN-derived causal explanation**
- proposed CLASSIC-only branch after workspace init: **DESIGN**, not yet HW.

## Next gate

Before a package:
1. recover the exact module-selection variable currently used by the Test85 diagnostic selector;
2. determine whether it can be set by a future native list without retaining the Settings-page visual hack;
3. construct an offline patch where CLASSIC selection enters native Refresh, reaches post-workspace dispatch, sets `s5=0`, and jumps to `0x80A38000`;
4. byte-audit that stock paths and Test106 MD hardening remain untouched.

No hardware test is requested by this finding alone.
