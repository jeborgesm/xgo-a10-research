ENTRY(xgo_external_probe)

SECTIONS
{
    . = 0x87000000;

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
