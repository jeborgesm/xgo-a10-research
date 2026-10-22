# Second render stage — binary finding

Firmware: XGO_TV_Text_Left24_Bold_P1_P2_PAL_Pending_TEST.zip.
The first Refresh composer at 0x80A38A58 restores state at 0x80A38E9C and jumps to 0x807DB9D4 at 0x80A38EF0.
0x807DB9D4 is executable second-stage render code. It saves register context, checks the pending flag at 0x80A389C0 at 0x807DBA10, and draws further text when active. It is not unrelated data.
Thus PAL disappearance must be traced through both composers and original draw/flip callbacks, not blamed on the first fill loop alone.
Previous offset analysis corrected: source pixel framebuffer+0xFA14; fill starts framebuffer+0xFA50. Text draw jal target is 0x803528A4.
Confirmed hardware: Refresh and Handle submenus are invisible after PAL selection, while their control effects occur. Approved bold captions must remain. No combined PAL fix yet.
Next: compare invocation and display states for the two-stage custom render chain on PAL versus NTSC before producing combined test ZIP.