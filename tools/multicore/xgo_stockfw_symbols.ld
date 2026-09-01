/*
 * XGO A10 stock-firmware symbol map for an SF2000-Multicore style port.
 *
 * Source: static disassembly of the preserved XGO bios/bisrv.asd.
 * Runtime image base: 0x80000000.
 * Firmware SHA-256:
 *   869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
 *
 * Status:
 *   CONFIRMED entries below are supported by executable behavior and/or
 *   multiple address-delta anchors. Do not apply this map to other firmware
 *   revisions without fingerprinting them first.
 */

/* ---- libc / stdio ------------------------------------------------------ */
/* XGO reproduces the SF2000 08/03/1.6 library block at +0x634c. */

malloc      = 0x80291c04;
free        = 0x80292814;
realloc     = 0x802928d8;
calloc      = 0x80292b90;

vsnprintf   = 0x80294624;
sprintf     = 0x802946d8;
vprintf     = 0x80294780;
printf      = 0x802947c0;
snprintf    = 0x802947e8;
vsprintf    = 0x80294808;
rand        = 0x802948b8;
memcpy      = 0x8029496c;
memset      = 0x80294b9c;
memcmp      = 0x80294c7c;
memmove     = 0x80294ce0;
strcpy      = 0x80294dac;
strcmp      = 0x80294dec;
strlen      = 0x80294e30;
atoi        = 0x80294e58;

fclose      = 0x802b2f40;
fflush      = 0x802b30b0;
fgets       = 0x802b320c;
fopen       = 0x802b3524;
fw_fread    = 0x802b3698;
fseeko      = 0x802b3804;
ftell       = 0x802b3f1c;
ftello      = 0x802b3f38;
fwrite      = 0x802b42ac;

/* ---- TDS / scheduler --------------------------------------------------- */

os_disable_interrupt = 0x802e0750;
os_enable_interrupt  = 0x802e0778;
dly_tsk              = 0x8030f480;
os_get_tick_count    = 0x8030fec8;

/* ---- XGO libretro frontend --------------------------------------------- */

retro_video_refresh_cb       = 0x8035e70c;
retro_audio_sample_batch_cb  = 0x8035e7d8;
retro_input_poll_cb          = 0x8035ea30;
retro_input_state_cb         = 0x8035eb20;
retro_environment_cb         = 0x8035eb64;

run_emulator = 0x8035ed48;
run_gba      = 0x80360110;

/* ---- XGO globals ------------------------------------------------------- */
/* XGO startup establishes $gp = 0x80c34774. */

/* Heap ceiling used by sbrk/allocator. Allocator init writes 0x87cdae00. */
RAMSIZE = 0x80c2ce6c;

/* Sound-task control word. Emulator wrappers clear bit 0 and wait for 0. */
g_snd_task_flags = 0x80c2e80c;

/* struct retro_game_info { path, data, size, ... } */
g_retro_game_info = 0x80c2e914;

/* Stock state indirection used by in-game Load/Save. */
gfn_state_save = 0x80c33a70;
gfn_state_load = 0x80c33ac0;

/* Active core API indirection. */
gfn_retro_get_region      = 0x80c33a9c;
gfn_get_system_av_info    = 0x80c33aac;
gfn_retro_load_game       = 0x80c33acc;
gfn_retro_unload_game     = 0x80c33ad4;
gp_buf_64m                 = 0x80c33ad8;
gfn_frameskip              = 0x80c33ae0;
gfn_retro_run              = 0x80c33ae4;

g_run_file_size            = 0x80c33a7c;

/*
 * Still to resolve before attempting an XGO Multicore build:
 *   - exact cache-flush/IRQ-hook patch site used by Multicore init_once()
 *   - any additional libc symbols required by selected cores
 *   - debug/LCD helper symbols if UART-less on-screen diagnostics are retained
 *   - confirmation that 0x87000000..core-end is safe against XGO-specific RAM use
 *
 * Important: the upstream SF2000 Multicore hard-codes stock $gp=0x80c114f4.
 * XGO MUST restore $gp=0x80c34774 before entering stock interrupt handlers.
 */
