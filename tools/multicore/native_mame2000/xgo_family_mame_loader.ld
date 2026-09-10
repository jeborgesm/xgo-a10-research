ENTRY(__start)
SECTIONS {
 /DISCARD/ : { *(.reginfo) *(.MIPS.abiflags) *(.pdr) *(.comment) *(.note*) *(.got*) *(.sdata*) *(.sbss*) }
 . = 0x80001900;
 .text : { *(.text*) }
 .rodata : { *(.rodata*) }
 .data : { *(.data*) }
 .bss : { *(.bss*) *(COMMON) }
 __end = .;
 ASSERT(__end <= 0x80002180, "family MAME loader exceeds verified cave")
}
