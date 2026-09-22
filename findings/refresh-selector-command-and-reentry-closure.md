# Refresh selector command and re-entry closure

Date: 2026-09-21
Branch: `research-classic-refresh-resurface`
Status: source/BIN closure; next candidate must be generated from deterministic source

## HW input from Test118

Test118 proved selector-active B cancellation:
- B closes REFRESH GAMES;
- normal Setup is revealed;
- device remains responsive.

Additional HW observation after selecting CLASSIC:
- selector closes;
- native Refresh runs;
- `No New Games` is displayed and expires;
- selecting Refresh Games afterward does not reopen the selector.

## Command-dispatch defect

The Test113/Test118 eight-row presentation inherited Test106's diagnostic active dispatcher. Test106 encoded row 3 as its diagnostic Back row:

```text
80A38648  li  t0,3
80A3864C  beq v1,t0,80A38668

80A38654  module_id = v1
80A3865C  selector_active = 0
80A38660  j 807DB5CC

80A38668  selector_active = 0
80A38674  User Menu selection = 3
80A38680  j 80359ABC
```

In the eight-row UI, row 3 is Game Boy. Therefore A/confirm must no longer use the inherited row-3 Back special case.

Final command semantics:

```text
A row 0..7:
    refresh_command = selected row
    selector_active = 0
    enter native Refresh 0x807DB5CC

B:
    selector_active = 0
    return/redraw normal User Menu
```

There is no implicit Refresh All. A future explicit ninth `Refresh All` row is a separate feature after all eight individual commands are closed.

## Re-entry finding

The post-CLASSIC symptom is consistent with an incomplete separation between:
- ordinary User Menu row-3 entry;
- selector-active state;
- native Refresh command state;
- the old Test85/Test106 diagnostic dispatcher.

The old dispatcher is still used both to enter and to execute selector commands. That makes selector lifetime dependent on inherited diagnostic state rather than a clean entry/command split.

The source-level correction is to make the state-14 confirm seam a true two-mode dispatcher:

```text
if selector_active == 0:
    preserve normal User Menu semantics
    row 3 -> initialize selector and redraw

if selector_active != 0:
    row 0..7 -> store refresh_command
    clear selector_active
    enter native Refresh
```

B-active remains the Test118 HW-proven cancel path.

After native Refresh status/epilogue completes, there must be no selector-specific persistent state required to reopen the selector: a later ordinary User Menu row-3 A press must initialize it from scratch.

## Important state ownership correction

The reconstruction previously described `selected_row` as a private word, but Test106/Test113 navigation actually uses the stock state-14 selection in the live frame (`0x1A4(sp)`) while `0x80A389C0` is selector-active state and `0x80A389C4` carries the selected command into Refresh.

Do not introduce a second independent selected-row variable unless required by evidence. The final source should model the stock frame selection directly.

## Hardware gate

Before another package:
1. remove the row-3 Back special case from active A dispatch;
2. prove ordinary row-3 entry always reinitializes selector-active state after a completed Refresh;
3. keep Test118 B behavior byte/semantics equivalent;
4. preserve Test113 renderer epilogue exactly;
5. emit from a deterministic builder with original-word checks and complete diff manifest.
