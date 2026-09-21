# Test85/Test106 diagnostic selector mechanism — exact binary closure

Date: 2026-09-20
Status: **BIN; explains the ugly current UI and gives a clean entry seam**

## Important baseline fact

The exact Test106 firmware SHA is identical to Test85/Test97:

```text
b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e
```

Therefore Test106 still contains the Test85 diagnostic User Menu selector machinery even though MD helper behavior is supplied externally.

## Why the current menu looks wrong

Test106's state-14 User Menu terminal constants are already patched from stock 2 to 3:

```text
80359AA4  li t9,3
80359E60  li v0,3
```

So the stock three-row User Menu has been expanded to four rows globally.

At `0x80359EA8`, row dispatch jumps into the Test85 diagnostic handler:

```text
80359EA8  j 0x80A385F0
```

The handler begins:

```text
80A385F0  lui t0,0x80A4
80A385F4  lw  t0,0x89C0(t0)   # selector_active
80A385F8  bne t0,zero,0x80A38648
...
80A38600  li t0,2
80A38604  beq v1,t0,0x80A38620
80A3860C  li t0,3
80A38610  beq v1,t0,0x80A38628
```

Row 3 enters diagnostic selector mode:

```text
80A38628  lui t0,0x80A4
80A3862C  li  t1,1
80A38630  sw  t1,0x89C0(t0)   # selector_active = 1
80A38634  sw  zero,0x1A4(sp)  # selection = 0
...
80A38640  j 0x80359ABC        # redraw User Menu
```

Thus the old UI is literally the User Menu being reused as a four-row diagnostic selector. This is the mechanism the user wants removed.

## Active-mode behavior

When `selector_active != 0`, the same four-row screen is reused.

The active path at `0x80A38648` treats rows below 3 as module commands and row 3 as exit/back:

```text
row 0..2:
    module_id = row
    selector_active = 0
    j 0x807DB5CC

row 3:
    selector_active = 0
    selection = 3
    j 0x80359ABC
```

This precisely explains why the diagnostic selector cannot simply be extended visually: its presentation and command semantics are entangled with the ordinary four-row User Menu.

## Clean migration seam

We can preserve one useful behavior and discard the rest:

```text
normal User Menu row 3
        |
        v
ENTER REFRESH GAMES OVERLAY
```

The row-3 entry branch is already a proven state-14 seam. Instead of setting the old diagnostic flag and redrawing the same cards, final code should:

1. set private `refresh_selector_active = 1`;
2. set private `selected_row = 0`;
3. invoke the dedicated text selector renderer;
4. remain under the state-14 lifecycle.

The old active-mode four-row renderer/dispatcher can then be retired.

## Why this is materially different

Old Test85:

```text
User Menu cards
 -> row 3
 -> same User Menu cards relabeled/reinterpreted
 -> only 3 modules + back
```

Final:

```text
User Menu
 -> REFRESH GAMES
 -> dedicated stock-font eight-row overlay
 -> module IDs 0..7
 -> native Refresh lifecycle
```

Only the proven entry seam is inherited; the diagnostic presentation is not.

## Evidence boundary

- Test106 == Test85/Test97 firmware SHA: **BIN**
- state-14 terminal 3 constants: **BIN**
- row-3 diagnostic entry: **BIN**
- active rows 0..2 command / row3 exit behavior: **BIN**
- replacing active presentation with dedicated eight-row text overlay: **DESIGN**
