# HK investigation: input publication versus Arcade mapping gate — 2026-10-14

## Evidence reviewed
SRC: `integrations/gp2040ce-xgo-test01/candidates/test16-offline/XGODriver.cpp`, `integrations/gp2040ce-xgo-test01/src/display/ui/screens/XGODiagnosticScreen.cpp`.
BIN: `findings/gp2040ce-stock-arcade-default-turbo-binary-verification-2026-10-12.md`.
Prior audit: `findings/gp2040ce-sf2-cps1-cross-layer-root-cause-leads-2026-10-12.md`.
HW: Test24 quick HK tap usually missed; hold MP then repeating HK; other actions work normally on taps.

## SRC confirmed
- `map_mask(Gamepad*)` serializes `pressedR1()` into bit0. The `process` method stores this in `xgo_diag_output` and `published_mask` on every invocation.
- The OLED diagnostic source prints `MASK %03X RAW %04X`, reading `xgo_diag_output` and `xgo_diag_raw`. This can verify published mask while button is held, but the OLED refresh rate cannot guarantee capture of very brief taps.
- No direct physical-GPIO sampling is performed by Test16. Earlier Test17 direct-GPIO candidate failed in hardware and should not be revived without stronger evidence.
- Serial slot0 is named R in the XGO host scanner. **It is not inherently named HK**. Its conversion to SFII attack is a distinct game/frontend mapping layer.

## BIN confirmed
- Original stock Arcade default map has no turbo flag set (12 records at 0x8ddc44 in bisrv.asd).
- Supplied archive contains no .kmp members; current SD override state remains OPEN.
- Mapping of this exact SFII runtime to LP/MP/HP/LK/MK/HK is not closed by the stock default table alone.

## Proposed non-destructive investigation
1. Examine actual SFII .kmp (if present) and runtime arcade input map before changing physical serial slots.
2. Verify that OLED diagnostic MASK shows bit0 (`001`) steadily during a held physical HK. This would verify input publication at OLED timescale only, not host sampling.
3. Establish whether HK remains unreliable in native frontend button test or another six-button title. This separates CPS1 mapping from serial reception.
4. For fast taps, need event counters or logic capture; OLED instantaneous display is insufficient.

## Status
No new UF2. Test16 remains best playable baseline. No claim that HK-to-MP proves a one-slot shift. Root cause OPEN.
