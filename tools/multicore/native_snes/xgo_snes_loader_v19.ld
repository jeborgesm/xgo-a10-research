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

    . = 0x80002230;
    __loader_start = .;
    .text   : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data   : { *(.data*) }
    .bss    : { *(.bss*) *(COMMON) }
    __loader_end = .;

    ASSERT(__loader_end <= 0x80003000,
           "XGO v19 SNES loader exceeds 0x80002230..0x80002fff verified cave")
}
