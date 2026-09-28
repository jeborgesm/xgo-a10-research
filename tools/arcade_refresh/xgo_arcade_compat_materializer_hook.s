.set noreorder
.set nomacro
.text
.align 2
.globl xgo_compat_materializer_hook
.type xgo_compat_materializer_hook,@function
xgo_compat_materializer_hook:
 addiu $sp,$sp,-32
 sw $ra,28($sp)
 jal xgo_compat_ensure_loaded
 nop
 bltz $v0,validator_error
 nop
 move $a0,$zero
 lui $a1,0x8760
 ori $a1,$a1,0x0100
 lui $a2,0x8760
 ori $a2,$a2,0x0500
 lui $t9,0x8718
 jalr $t9
 nop
 beq $v0,$zero,compatible
 nop
 addiu $t0,$zero,1
 beq $v0,$t0,skip_item
 nop
 addiu $t0,$zero,2
 beq $v0,$t0,skip_item
 nop
 b validator_error
 nop
compatible:
 lw $ra,28($sp)
 addiu $sp,$sp,32
 lw $s2,0xa0($fp)
 lw $a1,0x7c($fp)
 lui $t9,0x8700
 ori $t9,$t9,0x0534
 jr $t9
 nop
skip_item:
 lw $ra,28($sp)
 addiu $sp,$sp,32
 lui $t9,0x8700
 ori $t9,$t9,0x01f4
 jr $t9
 nop
validator_error:
 lw $ra,28($sp)
 addiu $sp,$sp,32
 lui $t9,0x8700
 ori $t9,$t9,0x0d84
 jr $t9
 nop
