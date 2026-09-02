ENTRY(__start)

SECTIONS
{
    /DISCARD/ : { *(.reginfo) *(.MIPS.abiflags) *(.pdr) *(.comment) *(.note*) }

    . = 0x80001500;
    __loader_start = .;
    .text   : { *(.text*) }
    .rodata : { *(.rodata*) }
    .data   : { *(.data*) }
    .bss    : { *(.bss*) *(COMMON) }
    __loader_end = .;

    /*
     * The preserved XGO firmware has exactly 0xC80 (3200) zero bytes at
     * 0x80001500..0x8000217f. This assertion checks the in-memory extent,
     * including any future .bss growth, rather than only the objcopied file
     * size. A loader that reaches 0x80002180 or below is valid; anything past
     * it would overwrite stock firmware and must fail at link time.
     */
    ASSERT(__loader_end <= 0x80002180,
           "XGO injected loader exceeds 0x80001500..0x8000217f firmware cave")
}
