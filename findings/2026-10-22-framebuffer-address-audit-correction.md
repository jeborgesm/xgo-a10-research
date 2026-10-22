# Corrected binary offsets — 2026-10-22

Rechecked firmware from XGO_TV_Text_Left24_Bold_P1_P2_PAL_Pending_TEST.zip. The earlier framebuffer-source claim was incorrect because MIPS immediate displacements are signed.

At 0x80A38AC8, lhu with immediate 0xFA14 following LUI 1 and framebuffer addition loads from framebuffer+0xFA14, **not +0x1FA14**. At 0x80A38AD4, addiu immediate 0xFA50 yields framebuffer+0xFA50, **not +0x1FA50**. Both are near row 50 for a 1280-byte stride. Refresh compositor clears 560 x 360 RGB565 pixels using the same sample color and 1280-byte row stride.

Also correct previous interpretation of jal 0x0C0D4A29: it calls address 0x803528A4, not 0x80354A29. PAL render root cause remains open. Both Refresh and Handle submenus are invisible in PAL (HW). Bold captions approved; no additional SD flash until substantial PAL fix and final TV-text adjustment are bundled.