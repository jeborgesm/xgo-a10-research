# Refresh post-operation re-entry — caller selection closure

Date: 2026-09-21
Status: **BIN causal closure from Test118 + native Refresh epilogue**

## New closure

The Test118 post-CLASSIC observation is explained by a state-14 selection leak, not by native Refresh failing to return.

Native Refresh has a complete epilogue and then explicitly redraws User Menu:

```text
807DB7B8  addiu sp,sp,0xB0
807DB7BC  li fp,1
807DB7C0  li s2,1
807DB7C4  j 0x80359ABC
807DB7C8  nop
```

Therefore native Refresh returns to the same state-14 caller frame and redraws it.

Test113/Test118 active A dispatch saves the selected row as command and clears selector-active, but does **not** normalize the caller's state-14 selection before entering Refresh:

```text
80A38654  lui t0,0x80A4
80A38658  sw  v1,0x89C4(t0)   # command
80A3865C  sw  zero,0x89C0(t0) # selector inactive
80A38660  j   0x807DB5CC
```

For CLASSIC, the caller's `0x1A4(sp)` selection remains 7.

After native Refresh completes, the epilogue redraws ordinary User Menu with selector inactive. Its valid terminal is 3, but the inherited caller selection is still 7. This leaves ordinary state-14 in an out-of-domain selection state and explains why Refresh Games does not reopen normally.

## Correct command transition

The command and UI selection are separate values and must be treated that way:

```text
command = selected selector row (0..7) -> 0x80A389C4
selector_active = 0                    -> 0x80A389C0
caller User Menu selection = 3         -> 0x1A4(sp)
enter native Refresh                    -> 0x807DB5CC
```

Native Refresh may then complete through Updated / No New Games / Failed and redraw User Menu with a valid selection of 3.

A subsequent A on Refresh Games enters the selector from scratch.

## Unified active A dispatcher

The inherited diagnostic row-3 Back branch must be removed. All eight rows use the same command transition:

```text
active A row 0..7:
    sw v1, refresh_command
    sw zero, selector_active
    li t0,3
    sw t0,0x1A4(sp)
    j NATIVE_REFRESH
```

This simultaneously:
- makes Game Boy/row3 a real individual Refresh command;
- preserves the selected module ID independently;
- normalizes ordinary User Menu state before native Refresh;
- fixes the post-Refresh re-entry precondition.

B remains the separate Test118 HW-proven close path.

## Evidence classes

- native Refresh full restore + User Menu redraw: **BIN**
- Test118 CLASSIC -> No New Games -> selector fails to reopen: **HW**
- CLASSIC leaves caller selection=7 in current active dispatcher: **BIN**
- ordinary inactive selector terminal=3: **BIN + HW**
- selection-domain mismatch as cause of re-entry failure: **BIN-derived causal closure**
- proposed unified active A transition: **DESIGN directly derived from closed BIN contracts; not yet HW**


## HW closure — Test119

Test119 implemented the unified active-A transition described above and was reported **successful on hardware** on 2026-09-21.

Promote the following from design/BIN-derived expectation to cumulative HW evidence:
- row 3/Game Boy no longer uses the inherited diagnostic Back semantic;
- the selected command survives independently in `0x80A389C4`;
- ordinary state-14 selection normalization to row 3 before native Refresh is compatible with the native Refresh lifecycle;
- Refresh Games can be entered again after the selected Refresh operation returns;
- Test118 B-cancel behavior remains compatible with the corrected A path.

Test119 firmware SHA-256:
`d357a86a79175d7c07877026ccfaa94c352fd571ba7d54b08d1e9acf1cdf4c15`

LCFG CRC-32/MPEG-2:
`0x39A338DE`

Source reproducer:
`tools/refresh_selector/build_test119_from_test106.py`
