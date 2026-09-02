ENTRY(xgo_loader_entry)

SECTIONS
{
    . = 0x80001500;

    .text :
    {
        KEEP(*(.entry))
        *(.text*)
        *(.rodata*)
    }

    /DISCARD/ :
    {
        *(.comment*)
        *(.note*)
        *(.MIPS.abiflags*)
        *(.reginfo*)
    }
}
