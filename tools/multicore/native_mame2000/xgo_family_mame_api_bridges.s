    .set noreorder
    .set nomacro
    .extern _gp
.macro CORE_BRIDGE name,target
    .pushsection .text.\name,"ax",@progbits
    .align 2
    .globl \name
    .type \name,@function
\name:
    addiu $sp,$sp,-32
    sw $ra,28($sp)
    sw $gp,24($sp)
    lui $gp,%hi(_gp)
    addiu $gp,$gp,%lo(_gp)
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

    .extern xgo_family_bind_impl
    .extern xgo_family_init_impl
    .extern xgo_family_deinit_impl
    .extern xgo_family_get_region_impl
    .extern xgo_family_get_av_impl
    .extern xgo_family_load_game_impl
    .extern xgo_family_unload_game_impl
    .extern xgo_family_run_impl

CORE_BRIDGE xgo_family_api_bind,xgo_family_bind_impl
CORE_BRIDGE xgo_family_api_init,xgo_family_init_impl
CORE_BRIDGE xgo_family_api_deinit,xgo_family_deinit_impl
CORE_BRIDGE xgo_family_api_get_region,xgo_family_get_region_impl
CORE_BRIDGE xgo_family_api_get_av,xgo_family_get_av_impl
CORE_BRIDGE xgo_family_api_load_game,xgo_family_load_game_impl
CORE_BRIDGE xgo_family_api_unload_game,xgo_family_unload_game_impl
CORE_BRIDGE xgo_family_api_run,xgo_family_run_impl
