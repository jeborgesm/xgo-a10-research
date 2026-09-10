# Correction: Test21 already implements the family IRQ-GP behavior

Date: 2026-09-08

During the family-lift audit, direct source comparison showed that Test21's
`repair_irq_gp()` already copies the XGO startup GP initialization words from
0x80001270/74 into the IRQ path at 0x80049744/48.

This is not a one-time GP assignment. Once patched, those instructions execute
on every interrupt entry. Therefore it is functionally the same newer
SF2000/GB300 Multicore strategy for restoring the stock firmware GP during
external-core execution.

Consequences:
- do NOT create another hardware test whose only change is IRQ GP restoration;
- the earlier hypothesis that Test21 lacked live IRQ GP restoration is rejected;
- Test21 hardware success already proves this family requirement was present;
- the remaining meaningful family delta is the core ABI/ownership model.

Next target:
```
list 11 loader
 -> upper-RAM core
 -> entry returns retro_core_t API table
 -> stock-side loader installs callbacks/active gfn slots
 -> stock run_emulator owns runtime
```

This should replace the custom `entry(filename, load_state)` frontend ownership
model used by the failing MAME candidates.

Non-regression rule remains: compose from golden Test08 and alter list 11 only.
