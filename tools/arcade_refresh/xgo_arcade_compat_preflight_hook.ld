OUTPUT_ARCH(mips)
ENTRY(xgo_compat_preflight_hook)
SECTIONS { . = 0x87002600; .text : { *(.text*) *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) *(COMMON) } __hook_end = .; }
