# Classic Arcade family-lift preservation contract

Date: 2026-09-08
Branch: `research-game-list-arcade-expansion`

## Non-regression contract

The family MAME2000 lift is additive to golden Test08.

The following are explicitly preserved and must not be globally reverted:
- Audio OSD v8 behavior, including in-game Volume-button display, timeout, and gray border;
- hardware-confirmed CPS1 scheduler/performance changes;
- mapper v19;
- native SNES work;
- Refresh Games / multi-system scanner;
- expiring Refresh status;
- stock pause/menu transaction;
- stock Arcade lists 7-10 and their optimized FBA runtime;
- current console-list behavior.

Golden Test08 firmware SHA-256 remains the required composition baseline:
`45831b0ea3c9ae336d82b240e6afe27167e5e83b88037152af237ab758ca1444`

## Family lift adaptation rule

Do not copy SF2000 Multicore's permanent IRQ patch globally.

SF2000 does:
`PATCH_JAL(0x80049744, restore_stock_gp)`

For XGO, the family behavior must be session-scoped:
1. save the original words at 0x80049744/48;
2. install an XGO-specific IRQ GP restoration trampoline while list-11 external MAME is active;
3. flush caches;
4. run external MAME;
5. restore the original IRQ words and flush caches before returning.

The XGO stock GP is:
`0x80c34774`

This preserves all golden firmware behavior outside the external-core session.

## Why this is the next high-value candidate

Test21 proved:
- list-11 loader entry;
- upper-RAM load;
- cache/IRQ preparation;
- execution at 0x87000000;
- return to firmware.

The full MAME core freezes, while the tiny probe succeeds.

SF2000 Multicore explicitly documents live IRQ GP restoration as required to prevent freezes when external/dynamic core execution changes GP around interrupts.

Therefore session-scoped family IRQ handling is the strongest family-proven delta to test before a larger loader/API-table transplant.
