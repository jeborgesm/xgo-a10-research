/*
 * XGO stock-firmware services intentionally exposed to an external core.
 *
 * This is deliberately narrower than ../xgo_stockfw_symbols.ld.
 * In particular, DO NOT bind malloc/free/realloc/calloc/sbrk or generic libc
 * here: the external FCEUmm image owns its own newlib heap inside gp_buf_64m.
 * Binding those names to the stock allocator would defeat memory isolation and,
 * on the native NES path, could overlap the preloaded ROM/newlib heap policy.
 */

/* Low-level filesystem primitives used by external newlib/VFS glue. */
fs_sync     = 0x802abc30;
fs_open     = 0x802abd58;
fs_opendir  = 0x802abe28;
fs_mkdir    = 0x802abeb4;
fs_access   = 0x802abfe8;
fs_fstat    = 0x802ac080;
fs_stat     = 0x802ac0a4;
fs_read     = 0x802ac150;
fs_write    = 0x802ac274;
fs_lseek    = 0x802ac394;
fs_readdir  = 0x802ac438;
fs_close    = 0x802ac4d4;
fs_closedir = 0x802ac4f0;

/* Scheduler/time services. */
dly_tsk           = 0x8030f480;
os_get_tick_count = 0x8030fec8;

/* Stock XGO libretro transport. */
retro_video_refresh_cb      = 0x8035e70c;
retro_audio_sample_batch_cb = 0x8035e7d8;
retro_input_poll_cb         = 0x8035ea30;
retro_input_state_cb        = 0x8035eb20;
retro_environment_cb        = 0x8035eb64;
run_emulator                = 0x8035ed48;

/* Stock globals intentionally shared with the external frontend/runtime. */
g_errno                 = 0x80c2d640;
g_retro_game_info       = 0x80c2e914;
gfn_state_save          = 0x80c33a70;
g_run_file_size         = 0x80c33a7c;
gfn_retro_get_region    = 0x80c33a9c;
gfn_get_system_av_info  = 0x80c33aac;
gfn_state_load          = 0x80c33ac0;
gfn_retro_load_game     = 0x80c33acc;
gfn_retro_unload_game   = 0x80c33ad4;
gp_buf_64m              = 0x80c33ad8;
gfn_frameskip           = 0x80c33ae0;
gfn_retro_run           = 0x80c33ae4;

XGO_ACTIVE_SYSTEM_FAMILY = 0x80c33ad0;

/*
 * Excluded by design:
 *   sbrk malloc free realloc calloc
 *   stdio/string/libc functions
 *
 * The native frontend currently invokes a few stock stdio routines through
 * explicit absolute function pointers, so they do not need linker symbols.
 */
