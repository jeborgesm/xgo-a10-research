/*
 * XGO external-core ABI veneer.
 *
 * Stock run_game()/the injected loader enter the external image with the stock
 * firmware global pointer still live in $gp. The linked FCEUmm/newlib image has
 * its own _gp and emits GP-relative accesses immediately, so C must never run
 * under the stock value.
 *
 * Preserve the firmware $gp and return address, establish the linker-provided
 * external-core _gp, execute the C frontend, then restore the firmware $gp
 * before returning to the injected loader / stock run_game() call chain.
 *
 * Keep this veneer freestanding and GP-independent. It is the first code at
 * 0x87000000 and executes before any external-core runtime initialization.
 */

    .set    noreorder
    .set    nomacro
    .section .init.core_entry,"ax",@progbits
    .align  2
    .globl  __core_entry__
    .type   __core_entry__, @function
    .extern __core_entry_c
    .extern _gp

__core_entry__:
    /* O32 caller frame: 16-byte outgoing argument area plus saved state. */
    addiu   $sp, $sp, -32
    sw      $ra, 28($sp)
    sw      $gp, 24($sp)

    /* No crt0 runs for an XGOC image. Establish the linked image's own GP. */
    lui     $gp, %hi(_gp)
    addiu   $gp, $gp, %lo(_gp)

    jal     __core_entry_c
    nop

    /* C may have used the core GP; firmware must never see that value. */
    lw      $gp, 24($sp)
    lw      $ra, 28($sp)
    addiu   $sp, $sp, 32
    jr      $ra
    nop

    .size   __core_entry__, .-__core_entry__
