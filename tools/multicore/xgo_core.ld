/* XGO external-core image layout, based on the proven SF2000 Multicore core.ld. */
SECTIONS
{
    . = 0x87000000;
    __image_start = .;

    .init :
    {
        KEEP(*(.init.core_entry))
        KEEP(*(SORT_NONE(.init)))
    }

    .text :
    {
        *(.text.unlikely .text.*_unlikely .text.unlikely.*)
        *(.text.exit .text.exit.*)
        *(.text.startup .text.startup.*)
        *(.text.hot .text.hot.*)
        *(SORT(.text.sorted.*))
        *(.text .stub .text.*)
    }

    .fini : { KEEP(*(SORT_NONE(.fini))) }
    .rodata : { *(.rodata .rodata.*) }

    .eh_frame_hdr : { *(.eh_frame_hdr) *(.eh_frame_entry .eh_frame_entry.*) }
    .eh_frame : ONLY_IF_RO { KEEP(*(.eh_frame)) *(.eh_frame.*) }
    .gcc_except_table : ONLY_IF_RO { *(.gcc_except_table .gcc_except_table.*) }

    .init_array :
    {
        PROVIDE_HIDDEN(__init_array_start = .);
        KEEP(*(SORT_BY_INIT_PRIORITY(.init_array.*) SORT_BY_INIT_PRIORITY(.ctors.*)))
        KEEP(*(.init_array EXCLUDE_FILE(*crtbegin.o *crtbegin?.o *crtend.o *crtend?.o) .ctors))
        PROVIDE_HIDDEN(__init_array_end = .);
    }

    .fini_array :
    {
        PROVIDE_HIDDEN(__fini_array_start = .);
        KEEP(*(SORT_BY_INIT_PRIORITY(.fini_array.*) SORT_BY_INIT_PRIORITY(.dtors.*)))
        KEEP(*(.fini_array EXCLUDE_FILE(*crtbegin.o *crtbegin?.o *crtend.o *crtend?.o) .dtors))
        PROVIDE_HIDDEN(__fini_array_end = .);
    }

    .ctors :
    {
        KEEP(*crtbegin.o(.ctors))
        KEEP(*crtbegin?.o(.ctors))
        KEEP(*(EXCLUDE_FILE(*crtend.o *crtend?.o) .ctors))
        KEEP(*(SORT(.ctors.*)))
        KEEP(*(.ctors))
    }

    .dtors :
    {
        KEEP(*crtbegin.o(.dtors))
        KEEP(*crtbegin?.o(.dtors))
        KEEP(*(EXCLUDE_FILE(*crtend.o *crtend?.o) .dtors))
        KEEP(*(SORT(.dtors.*)))
        KEEP(*(.dtors))
    }

    .data :
    {
        _fdata = .;
        *(.data .data.*)
        SORT(CONSTRUCTORS)
    }

    .got.plt : { *(.got.plt) }
    . = .;
    HIDDEN(_gp = ALIGN(16) + 0x7ff0);
    .got : { *(.got) }
    .sdata : { *(.sdata .sdata.*) }

    /* Everything through this marker has bytes in core_87000000. */
    __file_end = .;

    __bss_start = .;
    _fbss = .;
    .sbss (NOLOAD) :
    {
        *(.sbss .sbss.*)
        *(.scommon)
    }
    .bss (NOLOAD) :
    {
        *(.bss .bss.*)
        *(COMMON)
        . = ALIGN(. != 0 ? 4 : 1);
    }
    . = ALIGN(4);
    _end = .;
    __image_end = .;

    /DISCARD/ : { *(.reginfo) *(.MIPS.abiflags) *(.comment) *(.note*) }

    ASSERT(__image_end <= 0x87cdae00,
           "XGO external core exceeds reserved 0x87000000..0x87cdae00 window")
}
ENTRY(__core_entry__)
