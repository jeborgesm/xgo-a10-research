ENTRY(xgo_volume_osd_hook)
SECTIONS {
  . = 0x80002780;
  .text : { *(.text*) }
  .data : { *(.data*) }
  /DISCARD/ : { *(.reginfo) *(.MIPS.abiflags) *(.pdr) *(.comment) *(.note*) *(.got*) }
}
