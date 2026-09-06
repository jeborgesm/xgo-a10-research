    .set noreorder
    .set noat
    .text
    .globl menu_osd_tick_wrapper
menu_osd_tick_wrapper:
    addiu $sp,$sp,-24
    sw    $ra,20($sp)

    jal   0x8030f480
    nop

    jal   0x8030fec8
    nop
    move  $t9,$v0

    lui   $t0,%hi(menu_init)
    lw    $t1,%lo(menu_init)($t0)

    lui   $t2,0x80c3
    lw    $t3,0x3a54($t2)
    andi  $t3,$t3,0x00ff

    bnez  $t1,initialized
    nop
    addiu $t1,$zero,1
    sw    $t1,%lo(menu_init)($t0)
    sw    $t3,%lo(menu_last_volume)($t0)
    b     done
    nop

initialized:
    lw    $t4,%lo(menu_last_volume)($t0)
    beq   $t3,$t4,no_change
    nop
    sw    $t3,%lo(menu_last_volume)($t0)

    lw    $t5,0x395c($t2)
    addiu $t6,$zero,640
    bne   $t5,$t6,done
    nop
    lw    $t7,0x3958($t2)
    addiu $t6,$zero,480
    bne   $t7,$t6,done
    nop

    lui   $t8,0x8000
    addiu $t6,$zero,120
    sw    $t6,0x2988($t8)
    addiu $t6,$t9,1000
    sw    $t6,%lo(menu_deadline)($t0)
    addiu $t6,$zero,1
    sw    $t6,%lo(menu_active)($t0)
    b     repaint
    nop

no_change:
    lw    $t4,%lo(menu_active)($t0)
    beqz  $t4,done
    nop
    lw    $t5,%lo(menu_deadline)($t0)
    sltu  $t6,$t9,$t5
    bnez  $t6,done
    nop

    sw    $zero,%lo(menu_active)($t0)
    lui   $t8,0x8000
    sw    $zero,0x2988($t8)

    lw    $t5,0x395c($t2)
    addiu $t6,$zero,640
    bne   $t5,$t6,done
    nop
    lw    $t7,0x3958($t2)
    addiu $t6,$zero,480
    bne   $t7,$t6,done
    nop

repaint:
    lw    $a0,0x3364($t2)
    beqz  $a0,done
    nop
    lw    $a1,0x395c($t2)
    lw    $a2,0x3958($t2)
    sll   $a3,$a1,1
    jal   0x8035c398
    nop

done:
    lw    $ra,20($sp)
    addiu $sp,$sp,24
    jr    $ra
    nop

    .data
    .align 2
menu_init:        .word 0
menu_last_volume: .word 0
menu_deadline:    .word 0
menu_active:      .word 0
