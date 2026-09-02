/*
 * Assembly-only XGO loader continuity probe.
 *
 * No C runtime, no GP setup, no stack frame, no stock firmware calls.
 * The loader calls this entry at 0x87000000. Returning 0x58474f31 ("XGO1")
 * proves the loader successfully transferred control into the external image
 * and received control back.
 */

    .set noreorder
    .set nomacro
    .section .text.entry,"ax",@progbits
    .globl __core_entry__
    .type __core_entry__, @function
__core_entry__:
    lui   $v0, 0x5847
    ori   $v0, $v0, 0x4f31
    jr    $ra
    nop
    .size __core_entry__, .-__core_entry__
