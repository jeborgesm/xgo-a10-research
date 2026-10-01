/* GP-safe low-level VFS veneers for Arcade compatibility helper.
 * fs_lseek is the proven O32 five-word exception: whence lives at caller sp+16.
 */
.set noreorder
.set nomacro
.macro STOCK_BRIDGE name,target
 .text
 .align 2
 .globl \name
 .type \name,@function
\name:
 addiu $sp,$sp,-32
 sw $ra,28($sp)
 sw $gp,24($sp)
 lui $gp,0x80c3
 addiu $gp,$gp,0x4774
 jal \target
 nop
 lw $gp,24($sp)
 lw $ra,28($sp)
 addiu $sp,$sp,32
 jr $ra
 nop
.endm
.macro STOCK_BRIDGE5 name,target
 .text
 .align 2
 .globl \name
 .type \name,@function
\name:
 addiu $sp,$sp,-32
 sw $ra,28($sp)
 sw $gp,24($sp)
 lw $t0,48($sp)
 sw $t0,16($sp)
 lui $gp,0x80c3
 addiu $gp,$gp,0x4774
 jal \target
 nop
 lw $gp,24($sp)
 lw $ra,28($sp)
 addiu $sp,$sp,32
 jr $ra
 nop
.endm
STOCK_BRIDGE  xgo_stock_fs_open,0x802abd58
STOCK_BRIDGE  xgo_stock_fs_fstat,0x802ac080
STOCK_BRIDGE  xgo_stock_fs_read,0x802ac150
STOCK_BRIDGE5 xgo_stock_fs_lseek,0x802ac394
STOCK_BRIDGE  xgo_stock_fs_close,0x802ac4d4
