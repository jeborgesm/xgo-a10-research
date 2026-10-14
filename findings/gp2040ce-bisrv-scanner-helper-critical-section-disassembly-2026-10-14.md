# bisrv.asd scanner helper disassembly — critical-section evidence (2026-10-14)

Source: user-provided `XGoAnalisis.zip`, `bios/bisrv.asd` (12,768,452 bytes). File offsets coincide with virtual address low 24 bits in this mapped code region; original bytes inspected offline. No firmware changed.

## Helper 0x802e0750

```asm
802e0750 addiu sp,sp,-24
802e0754 sw    ra,16(sp)
802e0758 jal   0x80049da4
802e075c nop
802e0760 lw    v0,0x9b10(gp)
802e0764 addiu v0,v0,1
802e0768 sw    v0,0x9b10(gp)
802e076c lw    ra,16(sp)
802e0770 jr    ra
802e0774 addiu sp,sp,24
```

## Helper 0x802e0778

```asm
802e0778 addiu sp,sp,-24
802e077c sw    ra,16(sp)
802e0780 lw    v0,0x9b10(gp)
802e0784 addiu v0,v0,-1
802e0788 bgtz  v0,0x802e0798
802e078c sw    v0,0x9b10(gp)
802e0790 jal   0x80049df4
802e0794 sw    zero,0x9b10(gp)
802e0798 lw    ra,16(sp)
802e079c jr    ra
802e07a0 addiu sp,sp,24
```

Note: the `sw zero` in the delay slot executes before entering the callee. This pair maintains a nested counter and calls two low-level routines. It is **not** a fixed-time delay pair.

## Callee evidence

At `0x80049da4` and `0x80049df4`, both begin with `mfc0 t0,$12` (CP0 Status), then bit operations and `mtc0 t0,$12`. This is strong evidence of an interrupt-state/critical-section mechanism. Exact nested semantics and all branches still need verification; do not equate call cost with a calibrated DATA settling delay.

## Implications for Test28/29

The host scanner calls the nested critical-section helpers while transitioning GPIO and sampling B15 and L0. Test29's faster falling-edge response slowed observed held-button repeat (~2s vs ~1s on Test28) but did not remove punch mixing. The evidence does not yet establish the serial slot or physical GP2040-CE input for SFII HP or MK, nor the sampling edge for slots 1–11.

**Preserve Test28 hardware-proven baseline.** Do not introduce Test30 based on a presumed helper delay. Next: full host scanner disassembly with branch/delay-slot handling and GP2040 button-to-attack mapping verification.
