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
