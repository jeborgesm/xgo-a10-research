/*
 * Bidirectional $gp bridge between the external XGOC image and stock XGO.
 *
 * XGO stock code is not GP-independent: callbacks, stdio, scheduler and VFS
 * routines dereference firmware globals through the stock $gp (0x80c34774).
 * Conversely, FCEUmm/newlib code is linked with its own _gp and can be entered
 * indirectly by stock run_emulator().
 *
 * Ordinary veneers below are signature-transparent for calls whose argument
 * words fit in a0-a3. O32 stack arguments must be copied into the veneer's new
 * outgoing-argument area; fs_lseek has a dedicated five-word veneer for that
 * reason. Each veneer lives in its own function section so --gc-sections keeps
 * the reachable-runtime audits authoritative.
 */

    .set    noreorder
    .set    nomacro

.macro STOCK_BRIDGE name, target
    .pushsection .text.\name,"ax",@progbits
    .align  2
    .globl  \name
    .type   \name, @function
\name:
    addiu   $sp, $sp, -32
    sw      $ra, 28($sp)
    sw      $gp, 24($sp)
    lui     $gp, 0x80c3
    addiu   $gp, $gp, 0x4774
    jal     \target
    nop
    lw      $gp, 24($sp)
    lw      $ra, 28($sp)
    addiu   $sp, $sp, 32
    jr      $ra
    nop
    .size   \name, .-\name
    .popsection
.endm

/* O32 fs_lseek(fd, long long offset, whence): fd is a0, the 64-bit offset is
 * aligned into a2/a3, and whence is the fifth argument word at caller sp+16.
 * After allocating our 32-byte frame, old sp+16 is new sp+48; copy it to the
 * callee's required new sp+16 outgoing slot before the stock call. */
.macro STOCK_BRIDGE5 name, target
    .pushsection .text.\name,"ax",@progbits
    .align  2
    .globl  \name
    .type   \name, @function
\name:
    addiu   $sp, $sp, -32
    sw      $ra, 28($sp)
    sw      $gp, 24($sp)
    lw      $t0, 48($sp)
    sw      $t0, 16($sp)
    lui     $gp, 0x80c3
    addiu   $gp, $gp, 0x4774
    jal     \target
    nop
    lw      $gp, 24($sp)
    lw      $ra, 28($sp)
    addiu   $sp, $sp, 32
    jr      $ra
    nop
    .size   \name, .-\name
    .popsection
.endm

.macro CORE_BRIDGE name, target
    .pushsection .text.\name,"ax",@progbits
    .align  2
    .globl  \name
    .type   \name, @function
\name:
    addiu   $sp, $sp, -32
    sw      $ra, 28($sp)
    sw      $gp, 24($sp)
    lui     $gp, %hi(_gp)
    addiu   $gp, $gp, %lo(_gp)
    jal     \target
    nop
    lw      $gp, 24($sp)
    lw      $ra, 28($sp)
    addiu   $sp, $sp, 32
    jr      $ra
    nop
    .size   \name, .-\name
    .popsection
.endm

    .extern _gp

/* ---- external core -> stock XGO -------------------------------------- */
STOCK_BRIDGE xgo_stock_fopen,  0x802b3524
STOCK_BRIDGE xgo_stock_fseeko, 0x802b3804
STOCK_BRIDGE xgo_stock_ftell,  0x802b3f1c
STOCK_BRIDGE xgo_stock_fclose, 0x802b2f40

STOCK_BRIDGE  xgo_stock_fs_open,     0x802abd58
STOCK_BRIDGE  xgo_stock_fs_opendir,  0x802abe28
STOCK_BRIDGE  xgo_stock_fs_mkdir,    0x802abeb4
STOCK_BRIDGE  xgo_stock_fs_fstat,    0x802ac080
STOCK_BRIDGE  xgo_stock_fs_stat,     0x802ac0a4
STOCK_BRIDGE  xgo_stock_fs_read,     0x802ac150
STOCK_BRIDGE  xgo_stock_fs_write,    0x802ac274
STOCK_BRIDGE5 xgo_stock_fs_lseek,    0x802ac394
STOCK_BRIDGE  xgo_stock_fs_readdir,  0x802ac438
STOCK_BRIDGE  xgo_stock_fs_close,    0x802ac4d4
STOCK_BRIDGE  xgo_stock_fs_closedir, 0x802ac4f0

STOCK_BRIDGE xgo_stock_dly_tsk,           0x8030f480
STOCK_BRIDGE xgo_stock_os_get_tick_count, 0x8030fec8

STOCK_BRIDGE xgo_stock_video_refresh,      0x8035e70c
STOCK_BRIDGE xgo_stock_audio_sample_batch, 0x8035e7d8
STOCK_BRIDGE xgo_stock_input_poll,         0x8035ea30
STOCK_BRIDGE xgo_stock_input_state,        0x8035eb20
STOCK_BRIDGE xgo_stock_environment,        0x8035eb64
STOCK_BRIDGE xgo_stock_run_emulator,       0x8035ed48

/* ---- stock XGO -> external core -------------------------------------- */
    .extern retro_get_region
    .extern retro_get_system_av_info
    .extern retro_load_game
    .extern retro_unload_game
    .extern retro_run
    .extern xgo_disabled_state_io

CORE_BRIDGE xgo_core_get_region,  retro_get_region
CORE_BRIDGE xgo_core_get_av,      retro_get_system_av_info
CORE_BRIDGE xgo_core_load_game,   retro_load_game
CORE_BRIDGE xgo_core_unload_game, retro_unload_game
CORE_BRIDGE xgo_core_run,         retro_run
CORE_BRIDGE xgo_core_state_io,    xgo_disabled_state_io
