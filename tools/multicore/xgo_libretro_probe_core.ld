ENTRY(xgo_probe_core_entry)

SECTIONS
{
    . = 0x87000000;

    .image :
    {
        KEEP(*(.entry))
        *(.text*)
        *(.rodata*)
        *(.data*)
    }

    .bss (NOLOAD) :
    {
        *(.bss*)
        *(COMMON)
    }

    /DISCARD/ :
    {
        *(.comment*)
        *(.note*)
        *(.MIPS.abiflags*)
        *(.reginfo*)
    }
}
