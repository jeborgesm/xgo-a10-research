.set noreorder
.set noat
.text
.align 2
.globl xgo_compat_preflight_hook
.type xgo_compat_preflight_hook,@function
xgo_compat_preflight_hook:
 addiu $sp,$sp,-32
 sw $ra,28($sp)
 jal xgo_compat_ensure_loaded
 nop
 bltz $v0,error
 nop
 move $a0,$zero
 lui $a1,%hi(source_path)
 addiu $a1,$a1,%lo(source_path)
 lui $a2,%hi(driver_stem)
 addiu $a2,$a2,%lo(driver_stem)
 lui $t9,0x8730
 jalr $t9
 nop
 beq $v0,$zero,compatible
 nop
 addiu $t0,$zero,1
 beq $v0,$t0,nochange
 nop
 addiu $t0,$zero,2
 beq $v0,$t0,nochange
 nop
 b error
 nop
compatible:
 lui $t9,0x8700
 ori $t9,$t9,0x0020
 jalr $t9
 nop
 b done
 nop
nochange:
 move $v0,$zero
 b done
 nop
error:
 addiu $v0,$zero,-1
done:
 lw $ra,28($sp)
 addiu $sp,$sp,32
 jr $ra
 nop
.section .rodata
.align 2
source_path: .asciz "/mnt/sda1/ARCADE/CPS1/import/1941.zip"
driver_stem: .asciz "1941"
