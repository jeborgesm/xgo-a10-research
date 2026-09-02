ENTRY(__start)

SECTIONS
{
    /DISCARD/ : { *(.reginfo) *(.MIPS.abiflags) *(.pdr) *(.comment) *(.note*) }

    . = 0x87000000;
    __image_start = .;

    .text   : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data   : { *(.data*) }

    /* End of bytes that must exist in the on-card XGOC payload. */
    __file_end = .;

    /* BSS is runtime memory only; the loader zeros this range after loading. */
    .bss (NOLOAD) : {
        __bss_start = .;
        *(.bss*)
        *(COMMON)
        __bss_end = .;
    }

    __image_end = .;
}
