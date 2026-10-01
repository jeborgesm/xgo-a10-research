.set noreorder
.set noat
.text
.align 2
.globl xgo_compat_dynamic_preflight
.type xgo_compat_dynamic_preflight,@function
xgo_compat_dynamic_preflight:
 addiu $sp,$sp,-32
 sw $ra,28($sp)
 jal xgo_compat_ensure_loaded
 nop
 bltz $v0,error
 nop
 move $a0,$zero
 lui $a1,0x8730
 lui $a2,0x8700
 ori $a2,$a2,0x0020
 jal xgo_arcade_preflight_family
 nop
 b done
 nop
error:
 addiu $v0,$zero,-1
done:
 lw $ra,28($sp)
 addiu $sp,$sp,32
 jr $ra
 nop
