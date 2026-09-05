    .set noreorder
    .set noat
    .section .text
    .globl xgo_volume_osd_hook
xgo_volume_osd_hook:
    # run_screen_write tail-calls us with:
    # a0=RGB565 frame, a1=width, a2=height, a3=pixel pitch
    # ra already belongs to run_screen_write's caller.

    lui     $t0, %hi(osd_initialized)
    lw      $t1, %lo(osd_initialized)($t0)

    lui     $t2, 0x80c3
    lw      $t3, 0x3a54($t2)          # g_volume @ 0x80c33a54
    andi    $t3, $t3, 0x00ff

    bnez    $t1, 1f
    nop
    addiu   $t1, $zero, 1
    sw      $t1, %lo(osd_initialized)($t0)
    sw      $t3, %lo(osd_last_volume)($t0)
    j       tail_original
    nop

1:
    lw      $t4, %lo(osd_last_volume)($t0)
    beq     $t3, $t4, 2f
    nop
    sw      $t3, %lo(osd_last_volume)($t0)
    addiu   $t5, $zero, 120
    sw      $t5, %lo(osd_visible_frames)($t0)

2:
    lw      $t5, %lo(osd_visible_frames)($t0)
    beqz    $t5, tail_original
    nop
    sltiu   $t6, $a1, 72
    bnez    $t6, tail_original
    nop
    sltiu   $t6, $a2, 16
    bnez    $t6, tail_original
    nop
    beqz    $a0, tail_original
    nop

    addiu   $t5, $t5, -1
    sw      $t5, %lo(osd_visible_frames)($t0)

    # Stock policy remains 0/33/66/99; map to 0/21/42/64 pixels.
    beqz    $t3, fill_zero
    nop
    sltiu   $t7, $t3, 34
    bnez    $t7, fill_low
    nop
    sltiu   $t7, $t3, 67
    bnez    $t7, fill_mid
    nop
    addiu   $t6, $zero, 64
    b       fill_done
    nop
fill_zero:
    move    $t6, $zero
    b       fill_done
    nop
fill_low:
    addiu   $t6, $zero, 21
    b       fill_done
    nop
fill_mid:
    addiu   $t6, $zero, 42
fill_done:
    addiu   $sp, $sp, -32
    sw      $ra, 28($sp)
    sw      $a0, 16($sp)
    sw      $a1, 20($sp)
    sw      $a2, 24($sp)
    sw      $a3, 12($sp)
    sw      $t6, 8($sp)

    # Bottom-left: x=8, y=height-16.
    addiu   $t9, $a2, -16
    multu   $t9, $a3
    mflo    $t7
    addiu   $t7, $t7, 8
    sll     $t7, $t7, 1
    addu    $t7, $a0, $t7

    lui     $t8, %hi(osd_backup)
    addiu   $t8, $t8, %lo(osd_backup)
    addiu   $t9, $zero, 8
backup_row:
    addiu   $v0, $zero, 0
backup_col:
    lhu     $v1, 0($t7)
    sh      $v1, 0($t8)
    lw      $t6, 8($sp)
    sltu    $v1, $v0, $t6
    beqz    $v1, draw_empty
    nop
    addiu   $v1, $zero, -1
draw_store:
    sh      $v1, 0($t7)
    addiu   $t7, $t7, 2
    addiu   $t8, $t8, 2
    addiu   $v0, $v0, 1
    sltiu   $v1, $v0, 64
    bnez    $v1, backup_col
    nop
    sll     $v1, $a3, 1
    addiu   $v1, $v1, -128
    addu    $t7, $t7, $v1
    addiu   $t9, $t9, -1
    bnez    $t9, backup_row
    nop
    b       present
    nop
draw_empty:
    addiu   $v1, $zero, 0
    b       draw_store
    nop

present:
    jal     0x8035c31c
    nop

    # Restore the core-owned source frame after the synchronous display copy.
    lw      $a0, 16($sp)
    lw      $a3, 12($sp)
    lw      $a2, 24($sp)
    addiu   $t9, $a2, -16
    multu   $t9, $a3
    mflo    $t7
    addiu   $t7, $t7, 8
    sll     $t7, $t7, 1
    addu    $t7, $a0, $t7
    lui     $t8, %hi(osd_backup)
    addiu   $t8, $t8, %lo(osd_backup)
    addiu   $t9, $zero, 8
restore_row:
    addiu   $v0, $zero, 64
restore_col:
    lhu     $v1, 0($t8)
    sh      $v1, 0($t7)
    addiu   $t7, $t7, 2
    addiu   $t8, $t8, 2
    addiu   $v0, $v0, -1
    bnez    $v0, restore_col
    nop
    sll     $v1, $a3, 1
    addiu   $v1, $v1, -128
    addu    $t7, $t7, $v1
    addiu   $t9, $t9, -1
    bnez    $t9, restore_row
    nop

    lw      $ra, 28($sp)
    addiu   $sp, $sp, 32
    jr      $ra
    nop

tail_original:
    j       0x8035c31c
    nop

    .section .data
    .align 2
osd_initialized:     .word 0
osd_last_volume:     .word 0
osd_visible_frames:  .word 0
    .align 2
osd_backup:          .space 1024
