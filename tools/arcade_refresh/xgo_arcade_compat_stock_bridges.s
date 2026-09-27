/* GP-safe stock stdio veneers for external Arcade compatibility helper. */
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
STOCK_BRIDGE xgo_stock_fopen,0x802b3524
STOCK_BRIDGE xgo_stock_fread,0x802b3698
STOCK_BRIDGE xgo_stock_fseeko,0x802b3804
STOCK_BRIDGE xgo_stock_ftell,0x802b3f1c
STOCK_BRIDGE xgo_stock_fclose,0x802b2f40
