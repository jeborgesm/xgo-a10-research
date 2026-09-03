/*
 * Bidirectional $gp bridge between the external XGOC image and stock XGO.
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

/*
 * State compression helpers identified from the stock NES state path.
 *
 * 0x80365e64:
 *   int compress(dst, &dst_len, src, src_len)
 *
 * 0x8021dcc0:
 *   int uncompress(dst, &dst_len, src, src_len)
 *
 * Both return zlib-style status (0 == success). Keep them behind a GP veneer
 * even though the entry bodies are not GP-relative; callees remain stock code.
 */
STOCK_BRIDGE xgo_stock_state_compress,   0x80365e64
STOCK_BRIDGE xgo_stock_state_uncompress, 0x8021dcc0

/* Direct current-region writer used only for bring-up diagnostics. */
STOCK_BRIDGE xgo_stock_osd_region_write,   0x8035c31c

STOCK_BRIDGE xgo_stock_video_refresh,      0x8035e70c
STOCK_BRIDGE xgo_stock_audio_sample_batch, 0x8035e7d8
STOCK_BRIDGE xgo_stock_input_poll,         0x8035ea30
STOCK_BRIDGE xgo_stock_input_state,        0x8035eb20
STOCK_BRIDGE xgo_stock_environment,        0x8035eb64
STOCK_BRIDGE xgo_stock_run_emulator,       0x8035ed48

/* ---- stock XGO -> external core -------------------------------------- */
    .extern xgo_diag_get_region
    .extern xgo_diag_get_av
    .extern xgo_diag_load_game
    .extern xgo_diag_unload_game
    .extern xgo_diag_run
    .extern xgo_state_io_dispatch

CORE_BRIDGE xgo_core_get_region,  xgo_diag_get_region
CORE_BRIDGE xgo_core_get_av,      xgo_diag_get_av
CORE_BRIDGE xgo_core_load_game,   xgo_diag_load_game
CORE_BRIDGE xgo_core_unload_game, xgo_diag_unload_game
CORE_BRIDGE xgo_core_run,         xgo_diag_run

/*
 * The hardware-proven frontend still installs one pointer into both stock
 * state slots. The stock frontend gives that pointer distinguishable paths:
 *   save -> temporary .kmp
 *   load -> final .sa0..sa3
 * so the first generic-state candidate can dispatch without perturbing the
 * already-proven frontend wiring. A later cleanup should split load/save
 * veneers after hardware validation.
 */
CORE_BRIDGE xgo_core_state_io,    xgo_state_io_dispatch
