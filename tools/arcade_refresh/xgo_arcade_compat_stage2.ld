OUTPUT_ARCH(mips)
ENTRY(compat_validate)
SECTIONS {
 . = 0x87300000;
 .text : { *(.text.compat_validate) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 . = ALIGN(16);
 __bss_start = .;
 .bss : { *(.bss*) *(COMMON) }
 __bss_end = .;
 __stage2_end = .;
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) *(.reginfo*) *(.MIPS.abiflags*) }
}
ASSERT(__stage2_end < 0x87400000, "Arcade compat Stage2 overlaps catalog workspace")
