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

sbrk        = 0x80291944;
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

/* ---- filesystem / VFS ------------------------------------------------- */
/*
 * These wrappers preserve the same ABI and the same +0x634c relocation from
 * the SF2000 08/03 firmware. fs_access is also independently observed in XGO
 * frontend path checks, strengthening the block identification.
 */

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

osal_tds2_cache_flush = 0x80049214;
os_disable_interrupt  = 0x802e0750;
os_enable_interrupt   = 0x802e0778;
dly_tsk               = 0x8030f480;
os_get_tick_count     = 0x8030fec8;

/* ---- optional direct display-driver imports --------------------------- */
/*
 * These are not required by the minimal XGO external-core path, which can
 * remain behind the stock libretro callbacks. They are mapped for carrying
 * over SF2000 Multicore's advanced scaling/TV/tearing features.
 *
 * This region is intentionally NOT derived from one global address delta.
 * Each block was verified semantically in XGO executable code.
 */

get_vp_init_low_lcd_para = 0x801b9c84;
switch_lcd_or_tv         = 0x801b9de4;

/* ALi vpo_device->ioctl wrapper: vtable slot +0x3c. */
vpo_ioctl = 0x802777bc;

/* Generic HLD device-list lookup by type/id. */
dev_get_by_id = 0x802779a8;

/* XGO OSD driver wrapper block. */
osddrv_open             = 0x80278028;
osddrv_close            = 0x80278108;
osddrv_3x_create_region = 0x8027881c;
osddrv_3x_region_write  = 0x80279114;
osddrv_scale            = 0x80279438;

/* Active ST7789V MCU-8080 panel driver helpers. */
st7789v_caset_raset = 0x802a09e8;
st7789v_ramwr       = 0x802a0a8c;

/* ---- XGO stock frontend transport ------------------------------------- */
/*
 * These are the stock XGO display/audio transport helpers used below the
 * libretro callbacks. Keeping external cores behind these routines avoids
 * teaching a first Multicore port about XGO-specific LCD/audio drivers.
 */

run_osd_region_write = 0x8035c31c;
run_screen_write     = 0x8035c398;
run_sound_advance    = 0x8035cba0;

/* ---- XGO libretro frontend --------------------------------------------- */

retro_video_refresh_cb       = 0x8035e70c;
retro_audio_sample_batch_cb  = 0x8035e7d8;
retro_input_poll_cb          = 0x8035ea30;
retro_input_state_cb         = 0x8035eb20;
retro_environment_cb         = 0x8035eb64;

/* Applies the compiled six-button mapping table. */
set_keymap = 0x8035e83c;

run_emulator = 0x8035ed48;
run_gba      = 0x80360110;

/*
 * Main content dispatcher. The function emits "run_game %s,%s,%x", parses
 * the file extension/system mask, opens packaged content, and dispatches to
 * the appropriate stock emulator wrapper.
 */
run_game = 0x80360b88;

/* WQW package helpers used directly by run_game's packaged-content path. */
unwqw_init       = 0x80365c4c;
unwqw_decompress = 0x80365d70;
unwqw_free       = 0x80365de4;

/* ---- XGO startup / IRQ compatibility ---------------------------------- */

/* Startup establishes the firmware GP using these two instructions. */
XGO_GP_INIT_LUI   = 0x80001270;
XGO_GP_INIT_ADDIU = 0x80001274;
XGO_STOCK_GP      = 0x80c34774;

/*
 * Same IRQ-path patch slot used by SF2000/GB300 Multicore.
 * Preferred patch strategy: copy the two instructions at 0x80001270/74 into
 * 0x80049744/48 and flush the I-cache, rather than hard-coding the GP opcode.
 */
XGO_IRQ_GP_PATCH_LUI   = 0x80049744;
XGO_IRQ_GP_PATCH_ADDIU = 0x80049748;

/* Semantically verified Multicore diagnostic hook targets. */
XGO_WATCHDOG_HOOK_SITE = 0x800030d4;
XGO_EXCEPTION_HOOK_SITE = 0x800495a0;

/* ---- XGO globals ------------------------------------------------------- */

/*
 * XGO sbrk at 0x80291944 implements:
 *
 *   old = *XGO_HEAP_BREAK;
 *   new = old + increment;
 *   if ((unsigned)new < (unsigned)*RAMSIZE) {
 *       *XGO_HEAP_BREAK = new;
 *       return old;
 *   }
 *   g_errno = 12; // ENOMEM
 *   return (void *)-1;
 *
 * Allocator initialization writes:
 *   initial current break = 0x813b4bb4
 *   heap ceiling          = 0x87cdae00
 */
XGO_HEAP_START = 0x813b4bb4;
XGO_HEAP_BREAK = 0x80c337b0;
RAMSIZE        = 0x80c2ce6c;
g_errno        = 0x80c2d640;

/* Battery classifier output (-1,0..4). */
g_battery_level = 0x80c2d0d8;

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

/* Low family bits select NES/Sega/SNES/GBA/GB/Arcade frontend policy. */
XGO_ACTIVE_SYSTEM_FAMILY = 0x80c33ad0;

/*
 * Controller task and final mapped state arrays. Their 0x68-byte separation
 * matches the same two-stage state model documented by SF2000 Multicore.
 */
g_joy_task_state = 0x80c33a5c;
g_joy_state      = 0x80c33ac4;

/* Final mapped controller words consumed by retro_input_state_cb. */
g_input_port0 = 0x80c33ac4;  /* GPIO B15 -> Player 1 */
g_input_port1 = 0x80c33ac8;  /* GPIO L0  -> Player 2 */

/*
 * For the stripped/basic XGO Multicore path that uses stock callbacks, the
 * essential stock-firmware surface is now substantially mapped. Remaining
 * work is primarily production-core/newlib compatibility and hardware test
 * validation, rather than missing fundamental XGO board APIs.
 *
 * Already resolved:
 *   - loader injection window 0x1500..0x217f
 *   - debug-font window 0x2260..0x24ff
 *   - GBA redirect call site 0x80360cf4 / file offset 0x360cf4
 *   - IRQ GP repair slot 0x80049744/48
 *   - watchdog and general-exception hook sites
 *   - live heap break and heap ceiling
 *   - main run_game dispatcher and WQW package helpers
 *   - global keymap application routine
 *   - minimal and advanced video import sets
 */
