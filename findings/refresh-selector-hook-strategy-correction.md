# Refresh Games selector — hook strategy correction

Date: 2026-09-21
Status: **architecture correction before emission**

The v0 source reconstruction intentionally left selector event interception OPEN. A fresh review of the proven state-14 lineage shows we should not force a new raw/translated-event hook merely because the button identities are known.

## Key observation

The stock state-14 lifecycle already performs navigation and confirm before the known terminal/dispatch sites:

- `0x80359AA4` — navigation terminal/wrap constant;
- `0x80359E60` — navigation terminal/wrap constant;
- `0x80359E94` — current User Menu row is loaded for confirm dispatch;
- `0x80359EA8` — later row dispatch seam.

Historical Test05/Test85 hardware proves that changing the terminal from 2 to 3 causes the stock input machinery to navigate four rows without any new controller polling.

Therefore the safest first selector should continue to exploit **stock navigation state**, not add a second event decoder.

## Consequence for eight-row overlay

While selector-active, we need 0..7 navigation. The cleanest implementation target is conditional behavior at the two already-proven terminal sites, using the same stock selection variable/frame slot the state-14 code already updates.

This means:
- inactive: retain terminal 3 for normal four-row User Menu;
- active: terminal 7;
- confirm: reuse stock confirm lifecycle and substitute the private/module row at the proven confirm seam;
- cancel/B remains the only action that still requires a separately pinned state-14 Back path if stock Back does not naturally redraw state14.

This is safer than installing a general event hook because it preserves debouncing/repeat semantics and normal frontend cadence.

## First UI hardware gate refinement

The UI-only gate should not enable Refresh execution. A on a selector row may temporarily redraw/return without mutation until the native command dispatcher is independently byte-audited. Navigation should be driven by stock state-14 machinery.

## Evidence

- Test05 0..3 wrap after terminal changes: **SRC + HW lineage**
- Test85/Test106 terminal=3 and diagnostic selector: **BIN**
- stock confirm row load at 0x80359E94: **BIN/SRC lineage**
- conditional terminal 3/7 selector behavior: **DESIGN**
- exact conditional-hook encoding: **OPEN until displaced words/continuations are audited**
