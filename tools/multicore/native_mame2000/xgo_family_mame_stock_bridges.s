    .set noreorder
    .set nomacro
.macro STOCK_BRIDGE name,target
    .pushsection .text.\name,"ax",@progbits
    .align 2
    .globl \name
    .type \name,@function
\name:
    addiu $sp,$sp,-32
    sw $ra,28($sp)
    sw $gp,24($sp)
    lui $gp,0x80c3
    addiu $gp,$gp,0x4774
    jal \target
    nop
    lw $gp,24($sp)
    lw $ra,28($sp)
    addiu $sp,$sp,32
    jr $ra
    nop
    .size \name,.-\name
    .popsection
.endm
STOCK_BRIDGE xgo_stock_video_refresh,0x8035e70c
STOCK_BRIDGE xgo_stock_audio_sample_batch,0x8035e7d8
STOCK_BRIDGE xgo_stock_input_poll,0x8035ea30
STOCK_BRIDGE xgo_stock_input_state,0x8035eb20
STOCK_BRIDGE xgo_stock_environment,0x8035eb64
STOCK_BRIDGE xgo_stock_dly_tsk,0x8030f480
STOCK_BRIDGE xgo_stock_os_get_tick_count,0x8030fec8
STOCK_BRIDGE xgo_stock_fopen,0x802b3524
STOCK_BRIDGE xgo_stock_fseeko,0x802b3804
STOCK_BRIDGE xgo_stock_ftell,0x802b3f1c
STOCK_BRIDGE xgo_stock_fclose,0x802b2f40
STOCK_BRIDGE xgo_stock_fs_open,0x802abd58
STOCK_BRIDGE xgo_stock_fs_opendir,0x802abe28
STOCK_BRIDGE xgo_stock_fs_mkdir,0x802abeb4
STOCK_BRIDGE xgo_stock_fs_fstat,0x802ac080
STOCK_BRIDGE xgo_stock_fs_stat,0x802ac0a4
STOCK_BRIDGE xgo_stock_fs_read,0x802ac150
STOCK_BRIDGE xgo_stock_fs_write,0x802ac274
STOCK_BRIDGE xgo_stock_fs_readdir,0x802ac438
STOCK_BRIDGE xgo_stock_fs_close,0x802ac4d4
STOCK_BRIDGE xgo_stock_fs_closedir,0x802ac4f0
