.set noreorder
.set noat
.text
.align 2
.globl xgo_compat_materializer_hook
.type xgo_compat_materializer_hook,@function

/* Inline hook, not an ABI call site: preserve the materializer's complete
   live integer context across compatibility validation. */
xgo_compat_materializer_hook:
 addiu $sp,$sp,-128
 sw $at,0($sp)
 sw $v0,4($sp)
 sw $v1,8($sp)
 sw $a0,12($sp)
 sw $a1,16($sp)
 sw $a2,20($sp)
 sw $a3,24($sp)
 sw $t0,28($sp)
 sw $t1,32($sp)
 sw $t2,36($sp)
 sw $t3,40($sp)
 sw $t4,44($sp)
 sw $t5,48($sp)
 sw $t6,52($sp)
 sw $t7,56($sp)
 sw $s0,60($sp)
 sw $s1,64($sp)
 sw $s2,68($sp)
 sw $s3,72($sp)
 sw $s4,76($sp)
 sw $s5,80($sp)
 sw $s6,84($sp)
 sw $s7,88($sp)
 sw $t8,92($sp)
 sw $t9,96($sp)
 sw $gp,100($sp)
 sw $fp,104($sp)
 sw $ra,108($sp)
 mfhi $t0
 sw $t0,112($sp)
 mflo $t0
 sw $t0,116($sp)

 jal xgo_compat_ensure_loaded
 nop
 bltz $v0,validator_error
 nop
 move $a0,$zero
 lui $a1,0x8760
 ori $a1,$a1,0x0100
 lui $a2,0x8760
 ori $a2,$a2,0x0500
 lui $t9,0x8730
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

restore_context:
 lw $t0,112($sp)
 mthi $t0
 lw $t0,116($sp)
 mtlo $t0
 lw $at,0($sp)
 lw $v0,4($sp)
 lw $v1,8($sp)
 lw $a0,12($sp)
 lw $a1,16($sp)
 lw $a2,20($sp)
 lw $a3,24($sp)
 lw $t0,28($sp)
 lw $t1,32($sp)
 lw $t2,36($sp)
 lw $t3,40($sp)
 lw $t4,44($sp)
 lw $t5,48($sp)
 lw $t6,52($sp)
 lw $t7,56($sp)
 lw $s0,60($sp)
 lw $s1,64($sp)
 lw $s2,68($sp)
 lw $s3,72($sp)
 lw $s4,76($sp)
 lw $s5,80($sp)
 lw $s6,84($sp)
 lw $s7,88($sp)
 lw $t8,92($sp)
 lw $t9,96($sp)
 lw $gp,100($sp)
 lw $fp,104($sp)
 lw $ra,108($sp)
 addiu $sp,$sp,128
 jr $k0
 nop

compatible:
 lui $k0,0x8700
 ori $k0,$k0,0x0534
 b restore_context
 nop
skip_item:
 lui $k0,0x8700
 ori $k0,$k0,0x01f4
 b restore_context
 nop
validator_error:
 lui $k0,0x8700
 ori $k0,$k0,0x0d84
 b restore_context
 nop
