# Test122 individual Refresh command wiring audit

Date: 2026-09-21
Status: BIN/SRC audit. UI command capture is HW-proven; per-system execution mapping is **not yet closed for all eight rows**.

## What Test122 definitely does

Test119/Test122 active A stores the selected row at `0x80A389C4`, clears selector_active, normalizes the ordinary User Menu selection to 3, and enters native Refresh at `0x807DB5CC`.

Therefore the eight rows are real command inputs, not visual-only rows.

## Existing execution architecture recovered from repository

The protected Test106 firmware descends from Test85/Test97 selective Refresh work.

Repository BIN findings establish:
- native Refresh creates its `0xB0` frame and workspace first;
- workspace pointers are initialized at `0x807DB658..0x807DB678`;
- selective hook is at `0x807DB67C`;
- historical selective dispatcher occupies `0x80A386BC..0x80A38854`;
- stock native scanner is `0x807DAE4C(a0=list_id)`;
- stock list IDs are:
  - 0 FC
  - 1 SFC
  - 2 MD
  - 3 GB
  - 4 GBC
  - 5 GBA
- CLASSIC is not a stock-list call. Its safe contract is native workspace first, then `s5=0; j 0x80A38000`.
- stock cumulative Test75 scanned 0..5 and then continued to CLASSIC.

## Important gap

The current UI command IDs 0..7 match FC/SFC/MD/GB/GBC/GBA/Arcade/Classic by design, but matching numeric labels are not proof that the current Test106/Test119 post-workspace dispatcher consumes all eight IDs with those exact meanings.

In particular:
- stock native scanner directly closes IDs 0..5 only;
- Arcade needs its own historical module/path;
- CLASSIC needs the continuation contract above;
- Test106's inherited selective dispatcher was originally a diagnostic/selective implementation and must be disassembled exactly before claiming current row isolation.

## Hardware evidence already available

CLASSIC was selected during Test118 and reached the native status path, producing `No New Games`; therefore at least that UI action caused real Refresh execution. This does not by itself prove that only CLASSIC ran.

## Next closure

Disassemble protected Test122/Test119 around:
- `0x807DB67C`;
- `0x80A386BC..0x80A38854`;
- every load/reference of `0x80A389C4`.

Build an exact command-to-path table. No new hardware candidate is required for this audit.

Only after the table is closed should we test individual rows with controlled filesystem fixtures.

## Exact Test122 dispatcher closure — BIN

Direct disassembly of the protected Test122 firmware closes the current mapping. Native Refresh still hooks at:

```
807DB67C  j 0x80A386BC
```

The inherited selective dispatcher begins:

```
80A386CC  li   s0,0
80A386CC..D0
80A386CC  ...
80A386CC  # aggregate result init
80A386CC  lui  t0,0x80A4
80A386D0  lw   t0,0x89C4(t0)   # selected command
80A386D4  li   t1,0
80A386D8  beq  t0,t1,0x80A386F4
80A386E0  li   t1,1
80A386E4  beq  t0,t1,0x80A38750
80A386EC  j    0x80A387AC
```

Therefore the current command decode is only three-way:

| UI command | Current Test122 execution |
|---|---|
| 0 Famicom | FC selective helper pair at 0x80A386F4 |
| 1 Super Famicom | SFC selective helper pair at 0x80A38750 |
| 2 Mega Drive | MD selective helper pair at 0x80A387AC |
| 3 Game Boy | **MD path** |
| 4 Game Boy Color | **MD path** |
| 5 Game Boy Advance | **MD path** |
| 6 Arcade | **MD path** |
| 7 Classic | **MD path** |

This is direct BIN evidence. The UI command capture is eight-way, but the inherited Test85/Test97 execution dispatcher is only FC/SFC/else-MD.

### Correction to prior interpretation

The Test118 observation that selecting Classic produced `No New Games` did **not** prove CLASSIC execution. With this dispatcher closure, command 7 falls through to the MD path. The observed status was therefore consistent with an MD no-change Refresh. Retract any earlier implication that Test118 proved the CLASSIC module was invoked.

### Consequence

Test122 is HW-proven as a selector/UI/lifecycle checkpoint, but only rows 0/1/2 currently have matching execution identities. Rows 3..7 are mislabeled aliases of MD and should not be used as functional Refresh commands until a new post-workspace dispatcher is implemented.

The next implementation must expand the post-workspace command decoder without changing the HW-proven Test122 UI/input/presentation lifecycle. Stock FC/SFC/MD should preserve their existing proven helper paths; GB/GBC/GBA, Arcade and CLASSIC require their own evidence-backed module routes. CLASSIC must use the already-proven native-workspace continuation contract rather than a standalone call.
