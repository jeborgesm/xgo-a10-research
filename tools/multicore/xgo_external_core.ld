/*
 * Link a self-contained XGO external core at the reserved 0x87000000 window.
 *
 * File-backed sections are contiguous from __image_start through __file_end.
 * Runtime-only zero-initialized storage follows through __image_end. The XGOC
 * packer uses these three anchors plus __start to describe the executable.
 */

ENTRY(__start)

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
        *(.text .stub .text.* .gnu.linkonce.t.*)
    }

    .fini : { KEEP(*(SORT_NONE(.fini))) }

    .rodata :
    {
        *(.rodata .rodata.* .gnu.linkonce.r.*)
        *(.srodata .srodata.*)
        *(.lit4 .lit8)
    }

    .eh_frame_hdr : { *(.eh_frame_hdr) *(.eh_frame_entry .eh_frame_entry.*) }
    .eh_frame : { KEEP(*(.eh_frame)) *(.eh_frame.*) }
    .gcc_except_table : { *(.gcc_except_table .gcc_except_table.*) }

    .init_array :
    {
        PROVIDE_HIDDEN(__init_array_start = .);
        KEEP(*(SORT_BY_INIT_PRIORITY(.init_array.*) SORT_BY_INIT_PRIORITY(.ctors.*)))
        KEEP(*(.init_array))
        PROVIDE_HIDDEN(__init_array_end = .);
    }

    .fini_array :
    {
        PROVIDE_HIDDEN(__fini_array_start = .);
        KEEP(*(SORT_BY_INIT_PRIORITY(.fini_array.*) SORT_BY_INIT_PRIORITY(.dtors.*)))
        KEEP(*(.fini_array))
        PROVIDE_HIDDEN(__fini_array_end = .);
    }

    .ctors :
    {
        KEEP(*(.ctors))
        KEEP(*(SORT(.ctors.*)))
    }

    .dtors :
    {
        KEEP(*(.dtors))
        KEEP(*(SORT(.dtors.*)))
    }

    .data :
    {
        _fdata = .;
        *(.data .data.* .gnu.linkonce.d.*)
        SORT(CONSTRUCTORS)
    }

    .got.plt : { *(.got.plt) }
    . = .;
    HIDDEN(_gp = ALIGN(16) + 0x7ff0);
    .got : { *(.got) }

    .sdata :
    {
        *(.sdata .sdata.* .gnu.linkonce.s.*)
        *(.sdata2 .sdata2.*)
    }

    /* End of bytes that must exist in core.xgc payload. */
    . = ALIGN(16);
    __file_end = .;

    __bss_start = .;
    _fbss = .;

    .sbss (NOLOAD) :
    {
        *(.sbss .sbss.* .gnu.linkonce.sb.*)
        *(.scommon)
    }

    .bss (NOLOAD) :
    {
        *(.bss .bss.* .gnu.linkonce.b.*)
        *(COMMON)
    }

    . = ALIGN(16);
    _end = .;
    __image_end = .;

    /DISCARD/ :
    {
        *(.reginfo)
        *(.MIPS.abiflags)
        *(.pdr)
        *(.comment)
        *(.note*)
    }

    ASSERT(__image_end <= 0x87cdae00,
           "XGO external core exceeds stock heap ceiling / reserved window")
}
