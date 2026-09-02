/*
 * Production XGO external-core linker layout.
 *
 * Derived from the maintained SF2000 Multicore core.ld, but adds explicit
 * XGOC file-backed/runtime extent symbols. External cores are normal static
 * MIPS images and may legitimately contain GOT/small-data sections; the
 * GP/GOT-free rule applies only to the 0x80001500 injected loader.
 */

ENTRY(__core_entry__)

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
    .eh_frame : { KEEP(*(.eh_frame)) *(.eh_frame.*) }
    .gcc_except_table : { *(.gcc_except_table .gcc_except_table.*) }

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

    /* Everything through small data must be present in core.xgc. */
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

    /DISCARD/ : {
        *(.reginfo)
        *(.MIPS.abiflags)
        *(.comment)
        *(.note*)
    }

    ASSERT(__core_entry__ == 0x87000000,
           "XGO core entry must remain exactly at 0x87000000")
    ASSERT(__image_end <= 0x87cdae00,
           "XGO external core exceeds reserved upper-RAM window")
}
