# State-14 confirm hook and module handoff — exact Test92 binary closure

Date: 2026-09-20
Status: **BIN closure; final selector can reuse a proven control seam**

## Exact hook

Recovered Test92 patches the stock User Menu confirm dispatcher itself:

```text
80359E94  j 0x80A38688
80359E98  nop
```

The injected hook is:

```text
80A38688  lw    v1,0x1A4(sp)      # current User Menu row
80A3868C  lui   t0,0x80A4
80A38690  lw    t0,0x89C0(t0)     # selector/pending flag
80A38694  beq   t0,zero,80A386A4
80A38698  li    t6,1
80A3869C  j     0x80A38648        # consume selection
80A386A0  nop

80A386A4  beq   v1,zero,80A386B4  # preserve stock row-0 behavior
80A386A8  li    t6,1
80A386AC  j     0x80359EA0        # preserve stock remaining dispatch
80A386B0  nop
80A386B4  j     0x80357468
80A386B8  li    t6,1
```

When selector/pending is active, the consume path writes the selected row/module ID and enters native Refresh:

```text
80A38648  li    t0,3
80A38654  lui   t0,0x80A4
80A38658  sw    v1,0x89C4(t0)     # module ID
80A3865C  sw    zero,0x89C0(t0)   # clear pending
80A38660  j     0x807DB5CC        # native Refresh entry
```

## Why this matters

We do not need to invent a new A-button polling path.

There is already a narrow state-14 command seam that:
- obtains the selected row from the native User Menu stack state;
- can conditionally consume the action;
- otherwise reproduces the stock row-0 and remaining dispatch continuations;
- enters native Refresh at its real function entry.

This seam is much safer than a controller-task modal or raw input polling.

## Final-selector adaptation

The final first-class selector should retain the **shape** of this hook but replace the diagnostic Settings semantics:

```text
if !selector_active:
    execute original User Menu confirm logic

if selector_active:
    module_id = private selected_row
    selector_active = 0
    jump native_refresh_entry
```

The selected row should come from private selector state, not necessarily the stock User Menu row stored at `sp+0x1A4`, because the final selector has eight rows while the stock User Menu has three.

## Closed vs open

Closed:
- exact state-14 confirm interception site: **BIN**
- stock continuation addresses: **BIN**
- native Refresh entry handoff: **BIN**
- Test85/Test92 diagnostic lineage boots and dispatches stock modules: **HW lineage**

Still open:
- UP/DOWN interception while selector-active;
- B/cancel interception;
- selector background repaint;
- final private cave placement.

This removes one of the four remaining selector blockers: **A/confirm + native Refresh handoff is closed.**
