OUTPUT_ARCH(mips)
ENTRY(xgo_compat_materializer_hook)
SECTIONS {
 . = 0x87002600;
 .text : { *(.text.xgo_compat_materializer_hook) *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 . = ALIGN(16);
 __hook_end = .;
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) *(.reginfo*) *(.MIPS.abiflags*) *(.bss*) *(COMMON) }
}
ASSERT(__hook_end < 0x87100000, "Arcade materializer hook overlaps JPEG decoder")
