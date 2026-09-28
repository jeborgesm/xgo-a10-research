.set noreorder
.set nomacro
.text
.align 2
.globl _start
.type _start,@function
_start:
 j compat_validate
 nop
