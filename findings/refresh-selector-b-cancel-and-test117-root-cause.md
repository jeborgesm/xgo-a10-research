# Refresh selector B-cancel closure and Test116/117 corruption cause

Date: 2026-09-21
Branch: `research-classic-refresh-resurface`
Status: **BIN closure from exact Test106/Test113/Test116/Test117 artifacts + HW correlation**

## Executive result

The recent B-button experiments were not valid tests of the intended cancel logic because their helper was placed at `0x80A38F90`, which is **not free space in Test113**.

Test113's selector renderer has a live register-restore epilogue at:

```text
0x80A38F70..0x80A38FC8
```

Tests116/117 overwrote that epilogue.

This directly explains the sudden regression/hard lock and removes the apparent mystery around the B path.

The first actually free post-Test113 cave byte is:

```text
0x80A38FD0
```

through the previously audited upper bound `0x80A391F8`.

## Exact Test113 renderer tail

The hardware-positive Test113 image contains:

```text
80A38F70  lw s1,0x5c(sp)
80A38F74  lw s0,0x58(sp)
80A38F78  lw fp,0x54(sp)
80A38F7C  lw ra,0x50(sp)
80A38F80  lw t9,0x4c(sp)
80A38F84  lw t8,0x48(sp)
80A38F88  lw t7,0x44(sp)
80A38F8C  lw t6,0x40(sp)
80A38F90  lw t5,0x3c(sp)
80A38F94  lw t4,0x38(sp)
80A38F98  lw t3,0x34(sp)
80A38F9C  lw t2,0x30(sp)
80A38FA0  lw t1,0x2c(sp)
80A38FA4  lw t0,0x28(sp)
80A38FA8  lw a3,0x24(sp)
80A38FAC  lw a2,0x20(sp)
80A38FB0  lw a1,0x1c(sp)
80A38FB4  lw a0,0x18(sp)
80A38FB8  lw v1,0x14(sp)
80A38FBC  lw v0,0x10(sp)
80A38FC0  addiu sp,sp,0x80
80A38FC4  j 0x807DB9D4
80A38FC8  nop
```

Test116 begins its new helper at `0x80A38F90`, destroying restore instructions from `t5` onward.

Test117 likewise begins at `0x80A38F90` and destroys the same live epilogue.

Therefore:

- Test116's strange B behavior is contaminated by renderer-frame corruption.
- Test117's Setup hard lock is causally consistent with corruption of the renderer restore/return sequence.
- Neither result falsifies a selector-active conditional B dispatch by itself.

## Exact answer: what Test113 does when Game Boy is selected

The eight-row selector reuses the inherited Test106 active dispatcher.

The confirm seam is:

```text
80359E94  j 0x80A38688
```

At `0x80A38688`, when `selector_active != 0`, control goes to the inherited active dispatcher at `0x80A38648`.

That dispatcher has a special case for row value 3:

```text
80A38648  li  t0,3
80A3864C  beq v1,t0,0x80A38668

80A38668  lui t0,0x80A4
80A3866C  sw  zero,0x89C0(t0)   # selector_active = 0
80A38670  li  t0,3
80A38674  sw  t0,0x1A4(sp)      # restore User Menu selection = 3
80A38678  li  fp,1
80A3867C  li  s2,1
80A38680  j   0x80359ABC        # stock User Menu redraw
```

In the new eight-row presentation, row 3 is labelled **Game Boy**. Consequently, in Test113, selecting Game Boy does **not** enter native Refresh. It executes the inherited diagnostic selector's old row-3 **close/back operation**.

That is the exact close operation the user observed and asked to reuse for B.

Rows other than 3 take the inherited command path:

```text
module_id = selected row
selector_active = 0
j 0x807DB5CC
```

This also exposes a second source defect: the Test113 eight-row UI was ahead of its command dispatcher. Game Boy was still semantically the old diagnostic Back row.

## Correct B semantic target

For the current selector architecture, B while `selector_active != 0` must perform the same selector-close state transition as the proven row-3 inherited close path:

```text
selector_active = 0
User Menu selection = 3
fp = 1
s2 = 1
j 0x80359ABC
```

B while `selector_active == 0` must preserve the exact stock B path.

The stock translated B decision is BIN-pinned:

```text
80356C54  li  s2,0x2000
80356C58  beq v0,s2,0x80359E94   # A
80356C5C  li  s1,0x4000
80356C60  bne v0,s1,0x80356BFC   # not B
80356C64  li  s2,1
80356C68  li  s6,1               # B path
80356C6C  sw  s6,0x1AC(sp)
80356C70  lbu s6,-3564(gp)
80356C74  b   0x803560E0
80356C78  sb  s6,-3572(gp)
```

A selector-aware dispatch here is acceptable only if:
1. inactive execution reproduces these instructions exactly;
2. active execution routes to the already-BIN-proven selector close operation;
3. the helper lives in verified free space at/after `0x80A38FD0`;
4. displaced delay-slot semantics are reproduced exactly;
5. the complete Test113 renderer epilogue remains byte-identical.

This is no longer a guessed close target.

## Source/family evidence boundary

The public SF2000 Multicore source is valuable for stock runtime symbols, ABI, `$gp`, callbacks and emulator lifecycle. It does **not** provide the proprietary stock frontend state-14 menu source or this XGO selector extension.

Therefore the B-cancel closure here is primarily **XGO BIN**, not UP.

Relevant pinned family source remains:
- `madcock/sf2000_multicore` commit `207a6f57e9cd89826927cbee6ad2b1f170626d58` for the early extracted stock runtime API;
- current family tree `12263bb45e8d352299e4f830e7f7435540cf284d` for the maintained stock runtime map.

Do not claim those sources prove the XGO state-14 menu path.

## Additional required repair before hardware

The command dispatcher must be disentangled from the inherited diagnostic row-3 Back semantic. In the final eight-row selector:

```text
A row 0..7 -> command 0..7 -> native Refresh dispatch
B          -> selector close/redraw
```

Game Boy can no longer share the old `v1 == 3` close branch.

This must be corrected in source and deterministic build before another candidate.
