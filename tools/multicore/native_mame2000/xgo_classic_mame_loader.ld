ENTRY(__start)
SECTIONS
{
    /DISCARD/ : {
        *(.reginfo)
        *(.MIPS.abiflags)
        *(.pdr)
        *(.comment)
        *(.note*)
        *(.got*)
        *(.sdata*)
        *(.sbss*)
    }

    . = 0x80001900;
    __loader_start = .;
    .text   : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data   : { *(.data*) }
    .bss    : { *(.bss*) *(COMMON) }
    __loader_end = .;

    ASSERT(__loader_end <= 0x80002180,
           "Classic Arcade loader exceeds verified 0x80001900..0x8000217f cave")
}
