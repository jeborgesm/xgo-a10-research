.set noreorder
.set noat
.text

.section .main_sched,"ax",@progbits
.globl main_sched
main_sched:
    jal   0x8030fec8              # os_get_tick_count
    nop
    lw    $t1,-3328($gp)          # scheduler_start_tick
    subu  $t2,$v0,$t1             # elapsed_ms
    lw    $t3,-30284($gp)         # target_fps
    multu $t2,$t3
    mflo  $t4
    addiu $t5,$zero,1000
    .word 0x018d001b              # divu $zero,$t4,$t5; divisor is literal 1000
    mflo  $t6                     # ideal_frame
    lw    $t7,-30280($gp)         # completed_frame_count
    addiu $t8,$t7,1               # next_frame
    sltu  $t9,$t6,$t8             # ideal_frame < next_frame
    bnez  $t9,early_wait
    nop

    sw    $t8,-30280($gp)         # completed = next
    lw    $t0,-30304($gp)         # catchup_count
    sltu  $t1,$t8,$t6             # next < ideal
    sltiu $t2,$t0,3               # catchup < 3
    and   $t1,$t1,$t2
    bnez  $t1,catchup
    addiu $t0,$t0,1               # increment only matters on taken path

reset_catchup:
    sw    $zero,-30304($gp)
    sw    $t6,-30280($gp)         # snap logical frame to wall-time ideal
    sw    $zero,-3300($gp)        # frameskip = 0
    j     0x8035ef70              # untouched stock dispatch path
    nop

catchup:
    sw    $t0,-30304($gp)
    addiu $t1,$zero,1
    sw    $t1,-3300($gp)          # frameskip = 1
    j     0x8035ef70
    nop

.section .early_sched,"ax",@progbits
.globl early_wait
early_wait:
    jal   0x8030f480              # dly_tsk
    addiu $a0,$zero,1             # 1 ms polling sleep
    j     main_sched
    nop
