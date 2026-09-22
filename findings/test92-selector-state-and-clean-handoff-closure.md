# Test92 selector-state ownership and clean handoff closure

Date: 2026-09-20
Branch: `research-classic-refresh-resurface`
Status: **BIN closure from recovered Test92 firmware; no hardware candidate**

## Recovered state words

Direct disassembly of recovered `xgo-stock-test92-selective-refresh-classic-proof.zip` closes the two private words used by the diagnostic selector:

```text
0x80A389C0  selector_active / pending flag
0x80A389C4  selected module ID
```

The selector dispatcher at `0x80A386BC` reads `0x80A389C4`.

Its dispatch is:

```text
module 0 -> FC materializer + FC catalog helper
module 1 -> SFC materializer + SFC catalog helper
module 2 -> MD materializer + MD catalog helper
module 3 -> CLASSIC continuation
```

The CLASSIC branch is visible at:

```text
80A38840  li    t1,3
80A38844  beq   t0,t1,80A38854
...
80A38854  j     0x80A38000
```

The last jump is the already-known unsafe Test92 direct CLASSIC route.

## Writer/consumer relationship

The module word is not a guessed global. The same Test92 injected region writes it:

```text
80A38654  lui   t0,0x80A4
80A38658  sw    v1,0x89C4(t0)     # selected module ID
80A3865C  sw    zero,0x89C0(t0)   # clear pending/active flag
80A38660  j     0x807DB5CC        # enter native Refresh function
```

This is the clean handoff we wanted conceptually:

```text
UI selection
   |
   +-- write module ID
   +-- clear selector pending flag
   |
   v
native Refresh entry 0x807DB5CC
   |
   v
native frame + workspace initialization
   |
   v
module dispatcher
```

The ugly Settings-page selector is therefore **not architecturally required**. It was only one producer of the module ID.

## Important correction

Earlier notes treated `0x80A389C4` as an unresolved Test85 selector variable. It is now directly closed from Test92 BIN evidence.

It is safe to reuse the *handoff concept*, but not necessarily the exact storage address in the final build. The address lies inside the injected Test92 cave/data region and is implementation-owned rather than a stock firmware global.

For the final selector, keep private selector state inside the new injected module itself:

```text
selector_active
selected_row/module_id
```

No persistent SD state and no stock global need to be repurposed.

## CLASSIC repair

Test92 already enters native Refresh correctly at `0x807DB5CC`; the failure occurs later because its dispatcher eventually jumps to CLASSIC using the wrong continuation setup.

The corrected CLASSIC dispatch, after native workspace initialization, is:

```text
selected module == CLASSIC
    li s5,0
    j 0x80A38000
```

while the native Refresh frame remains live.

Thus we do not need:
- a fake Refresh frame;
- a direct menu call to `0x80A38000`;
- a Settings-page callback;
- a new frontend state.

## Evidence boundary

- `0x80A389C0/0x80A389C4` ownership and writes: **BIN**
- module values 0 FC, 1 SFC, 2 MD, 3 CLASSIC: **BIN**
- jump back to native Refresh entry: **BIN**
- Test92 CLASSIC hard lock: **HW**
- corrected post-workspace CLASSIC branch: **DESIGN derived from BIN/HW lifecycle closure**
- final private state address: **OPEN until final cave layout**

## Next construction gate

Build a source-preserved selector/adapter module with:
1. private `selector_active` and `selected_row`;
2. state-14 text renderer/input interception;
3. A -> store row/module ID and enter `0x807DB5CC`;
4. B -> clear selector state and resume stock User Menu;
5. post-workspace Refresh dispatcher with CLASSIC `s5=0 -> 0x80A38000`;
6. byte audit against Test106 protected firmware surfaces.

No hardware package is justified until that module can be reconstructed and audited offline.
