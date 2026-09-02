/*
 * Bidirectional $gp bridge between the external XGOC image and stock XGO.
 *
 * XGO stock code is not GP-independent: callbacks, stdio, scheduler and VFS
 * routines dereference firmware globals through the stock $gp (0x80c34774).
 * Conversely, FCEUmm/newlib code is linked with its own _gp and can be entered
 * indirectly by stock run_emulator().
 *
 * Every veneer below is signature-transparent. a0-a3 and any caller stack
 * arguments are left untouched; only a private O32 frame, ra and gp are used.
 * Return values in v0/v1 (including 64-bit O32 returns) pass through unchanged.
 */

    .set    noreorder
    .set    nomacro
    .text
    .align  2

/* Stock firmware GP recovered from startup at 0x80001270/74. */
#define XGO_STOCK_GP_HI 0x80c3
#define XGO_STOCK_GP_LO 0x4774

/*
 * A transparent call veneer needs the mandatory 16-byte O32 outgoing argument
 * area plus saved gp/ra. 32 bytes preserves 8-byte stack alignment.
 */
.macro STOCK_BRIDGE name, target
    .globl  \name
    .type   \name, @function
\name:
    addiu   $sp, $sp, -32
    sw      $ra, 28($sp)
    sw      $gp, 24($sp)
    lui     $gp, XGO_STOCK_GP_HI
    addiu   $gp, $gp, XGO_STOCK_GP_LO
    jal     \target
    nop
    lw      $gp, 24($sp)
    lw      $ra, 28($sp)
    addiu   $sp, $sp, 32
    jr      $ra
    nop
    .size   \name, .-\name
.endm

.macro CORE_BRIDGE name, target
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
.endm

    .extern _gp

/* ---- external core -> stock XGO -------------------------------------- */

/* Stock stdio used by exact_rom_size(). */
STOCK_BRIDGE xgo_stock_fopen,  0x802b3524
STOCK_BRIDGE xgo_stock_fseeko, 0x802b3804
STOCK_BRIDGE xgo_stock_ftell,  0x802b3f1c
STOCK_BRIDGE xgo_stock_fclose, 0x802b2f40

/* ALi VFS primitives used by external newlib/libretro-common. */
STOCK_BRIDGE xgo_stock_fs_open,     0x802abd58
STOCK_BRIDGE xgo_stock_fs_opendir,  0x802abe28
STOCK_BRIDGE xgo_stock_fs_mkdir,    0x802abeb4
STOCK_BRIDGE xgo_stock_fs_fstat,    0x802ac080
STOCK_BRIDGE xgo_stock_fs_stat,     0x802ac0a4
STOCK_BRIDGE xgo_stock_fs_read,     0x802ac150
STOCK_BRIDGE xgo_stock_fs_write,    0x802ac274
STOCK_BRIDGE xgo_stock_fs_lseek,    0x802ac394
STOCK_BRIDGE xgo_stock_fs_readdir,  0x802ac438
STOCK_BRIDGE xgo_stock_fs_close,    0x802ac4d4
STOCK_BRIDGE xgo_stock_fs_closedir, 0x802ac4f0

/* Scheduler/time services. */
STOCK_BRIDGE xgo_stock_dly_tsk,           0x8030f480
STOCK_BRIDGE xgo_stock_os_get_tick_count, 0x8030fec8

/* Stock libretro transport and main frontend loop. */
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
