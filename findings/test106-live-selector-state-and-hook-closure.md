# Test106 live selector-state correction and exact hook closure

Date: 2026-09-21
Status: **BIN closure from exact Test106 firmware bytes**

Exact firmware inspected:
- size: 12,768,452 bytes
- SHA-256: `b66dbcd86ad785875a6804bb7d07c6eb1195ceedb01c0bce8107f65eee2ab66e`

The firmware was extracted directly from the preserved Test106 hardware-candidate ZIP and independently matches the loose `bisrv.asd` copy.

## Important correction: 0x80A389C0/C4 are live data

The earlier zero-run audit correctly observed zero bytes but overclassified the whole `0x80A389B8..` area as executable cave. Zero initialization does **not** mean unowned.

Exact Test106 code references prove:
```text
80A385F4  lw t0,0x89C0(t0)
80A38630  sw t1,0x89C0(t0)
80A38658  sw v1,0x89C4(t0)
80A3865C  sw zero,0x89C0(t0)
80A3866C  sw zero,0x89C0(t0)
80A38690  lw t0,0x89C0(t0)
80A386D0  lw t0,0x89C4(t0)
807DBA14  lw t0,0x89C0(t0)
```

Thus:
- `0x80A389C0` = live diagnostic selector-active state;
- `0x80A389C4` = live selected Refresh command;
- they MUST NOT be overwritten as code while the inherited Test85/Test106 control path exists.

Safe contiguous zero-code allocation therefore begins at **0x80A389C8**, not 0x80A389B8, unless the old state references are first completely removed.

This correction is evidence-significant and supersedes any prior statement treating C0/C4 as free cave.

## Exact inherited diagnostic selector

Test106 still contains the Test85 selector:
```text
80A385F0  load selector_active
80A38628  row3 -> set selector_active=1, selected row=0, redraw
80A38648  active confirm dispatcher
80A38658  selected command -> 80A389C4
80A38660  j native Refresh 0x807DB5CC
80A38688  confirm hook entry
80A386BC  selective Refresh dispatcher
```

The state-14 confirm site is:
```text
80359E94  j 0x80A38688
80359E98  nop
```

## Exact inherited diagnostic renderer

Test106 also still contains the old diagnostic overlay hook:
```text
80359BA8  j 0x807DB9D4
80359BAC  nop
```

At `0x807DB9D4`, the hook saves caller-visible temporaries, tests `0x80A389C0`, and when active draws:
```text
REFRESH GAMES
TL=FC  TR=SFC  BL=MD  BR=BACK
```
using stock `TEXT_DRAW=0x803528A4`.

The strings are at:
```text
807DBB40  "REFRESH GAMES"
807DBB50  "TL=FC  TR=SFC  BL=MD  BR=BACK"
```

This directly explains the ugly diagnostic UI. It is not a mystery resource or Settings bitmap: it is an injected text overlay.

## Exact navigation sites from Test106

Up-wrap path:
```text
80359A90  lw fp,0x1A4(sp)
80359A94  bne fp,zero,80359C3C
80359AA4  li t9,3
80359AA8  sw t9,0x1A4(sp)
...
80359C3C  lw s0,0x1A4(sp)
80359C48  addiu t0,s0,-1
80359C50  b 80359AB0
80359C54  sw t0,0x1A4(sp)
```

Down-wrap path:
```text
80359E60  li v0,3
80359E64  beq t4,v0,8035AC6C
80359E6C  lw a0,0x1A4(sp)
80359E78  addiu t5,a0,1
80359E7C  sw t5,0x1A4(sp)
80359E8C  b 80359ABC
```

Therefore conditional terminal 3/7 can be implemented without any controller decoder:
- replace `80359AA4/AA8` with jump+nop to an up-terminal helper that chooses 3 or 7, stores `sp+0x1A4`, then returns to `80359AAC`;
- replace `80359E60/E64` with jump+nop to a down-terminal helper that chooses 3 or 7, compares current row, then absolute-jumps to either `8035AC6C` or `80359E6C`.

## Evidence grades

- firmware SHA/bytes: **BIN**
- live C0/C4 ownership: **BIN**
- old overlay strings/render path: **BIN**
- exact up/down paths: **BIN**
- conditional 3/7 helper strategy: **DESIGN based on closed BIN continuations**
- hardware behavior of replacement: **OPEN**
