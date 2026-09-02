/*
 * Stripped XGO native-FCEUmm frontend prototype.
 *
 * This is the external image entry intended to be linked together with the
 * known HC15xx-compatible FCEUmm static archive, libretro-common, newlib, the
 * XGO environment shim, and xgo_preloaded_rom_sbrk.c.
 *
 * Entry contract:
 *   - loader has placed this image at 0x87000000
 *   - run_game() has already loaded/decompressed the selected NES ROM into
 *     gp_buf_64m and populated g_run_file_size
 *   - active XGO family remains NES (0x01)
 *
 * First-bring-up policy:
 *   - preserve stock XGO video/audio/input transport
 *   - repair IRQ $gp exactly as maintained Multicore does
 *   - disable stock save-state I/O to avoid feeding 2017 FCEUmm state files to
 *     the newer core
 *   - configure both libretro ports as ordinary joypads
 *   - leave the enhanced Multicore pause-menu patch out until basic execution
 *     is proven
 *
 * This source does not touch SPI NOR or Firmware.upk.
 */

typedef unsigned int size_t;
typedef int bool;
#define true 1
#define false 0

struct retro_game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};
struct retro_system_av_info;

typedef bool (*environment_cb)(unsigned, void *);
typedef void (*video_cb)(const void *, unsigned, unsigned, size_t);
typedef size_t (*audio_batch_cb)(const short *, size_t);
typedef void (*poll_cb)(void);
typedef short (*input_cb)(unsigned, unsigned, unsigned, unsigned);

/* Supplied by the statically linked FCEUmm archive. */
extern void retro_init(void);
extern void retro_deinit(void);
extern void retro_set_environment(environment_cb);
extern void retro_set_video_refresh(video_cb);
extern void retro_set_audio_sample_batch(audio_batch_cb);
extern void retro_set_input_poll(poll_cb);
extern void retro_set_input_state(input_cb);
extern void retro_set_controller_port_device(unsigned, unsigned);
extern void retro_get_system_av_info(struct retro_system_av_info *);
extern bool retro_load_game(const struct retro_game_info *);
extern void retro_unload_game(void);
extern void retro_run(void);
extern unsigned retro_get_region(void);

/* Supplied by xgo_minimal_environment_shim.c. */
extern bool xgo_minimal_environment(unsigned, void *);

#define STOCK_VIDEO ((video_cb)0x8035e70cu)
#define STOCK_AUDIO ((audio_batch_cb)0x8035e7d8u)
#define STOCK_POLL  ((poll_cb)0x8035ea30u)
#define STOCK_INPUT ((input_cb)0x8035eb20u)

#define FW_DLY_TSK      ((int (*)(unsigned))0x8030f480u)
#define FW_RUN_EMULATOR ((void (*)(int))0x8035ed48u)
#define FW_OS_DISABLE   ((void (*)(void))0x802e0750u)
#define FW_OS_ENABLE    ((void (*)(void))0x802e0778u)

#define SOUND_FLAGS   (*(volatile unsigned *)0x80c2e80cu)
#define GAME_INFO     (*(volatile struct retro_game_info *)0x80c2e914u)
#define ROM_BUFFER    (*(void **)0x80c33ad8u)
#define RUN_FILE_SIZE (*(volatile unsigned *)0x80c33a7cu)

#define GFN_STATE_SAVE  (*(int (**)(const char *))0x80c33a70u)
#define GFN_GET_REGION  (*(unsigned (**)(void))0x80c33a9cu)
#define GFN_GET_AV      (*(void (**)(struct retro_system_av_info *))0x80c33aacu)
#define GFN_STATE_LOAD  (*(int (**)(const char *))0x80c33ac0u)
#define GFN_LOAD_GAME   (*(bool (**)(const struct retro_game_info *))0x80c33accu)
#define GFN_UNLOAD_GAME (*(void (**)(void))0x80c33ad4u)
#define GFN_FRAMESKIP   (*(void **)0x80c33ae0u)
#define GFN_RUN         (*(void (**)(void))0x80c33ae4u)

static int disabled_state_io(const char *path)
{
    (void)path;
    return 0;
}

/*
 * Maintained SF2000 Multicore repairs $gp in the IRQ path by copying the two
 * firmware startup instructions rather than embedding a firmware-specific GP
 * constant. XGO has independently confirmed the same source/destination sites.
 */
static void repair_irq_gp(void)
{
    volatile unsigned *src = (volatile unsigned *)0x80001270u;
    volatile unsigned *dst = (volatile unsigned *)0x80049744u;
    unsigned p;

    FW_OS_DISABLE();
    dst[0] = src[0];
    dst[1] = src[1];

    /* 16-byte cache lines: write back and invalidate only the patched area. */
    for (p = 0x80049740u; p < 0x80049750u; p += 16)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)" : : "r"(p));
    __asm__ volatile("sync; nop; nop");
    for (p = 0x80049740u; p < 0x80049750u; p += 16)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)" : : "r"(p));
    __asm__ volatile("nop; nop; nop; nop; nop");

    FW_OS_ENABLE();
}

/*
 * A raw core_87000000 image does not contain the NOLOAD BSS bytes. The final
 * newlib build must clear BSS and initialize newlib before using FCEUmm.
 *
 * Define XGO_WITH_NEWLIB when compiling with the SF2000/HC15xx newlib
 * toolchain. Keeping this conditional allows the control-flow shell to be
 * compile/disassembly-checked with a freestanding LLVM MIPS target too.
 */
#ifdef XGO_WITH_NEWLIB
#include <reent.h>
extern unsigned char __bss_start;
extern unsigned char _end;
extern void __libc_init_array(void);
extern void __sinit(struct _reent *);

static void init_core_runtime(void)
{
    unsigned char *p;
    for (p = &__bss_start; p < &_end; ++p)
        *p = 0;

    _REENT_INIT_PTR(_REENT);
    __sinit(_REENT);
    __libc_init_array();
}
#else
static void init_core_runtime(void) {}
#endif

__attribute__((section(".init.core_entry"), used))
int __core_entry__(const char *filename, int load_state)
{
    repair_irq_gp();
    init_core_runtime();

    /* Same sound-task transition performed by the embedded stock NES wrapper. */
    SOUND_FLAGS &= 0xfffeu;
    while (SOUND_FLAGS != 0)
        FW_DLY_TSK(1);

    /* Keep the proven XGO hardware transport, replace only the emulator core. */
    retro_set_video_refresh(STOCK_VIDEO);
    retro_set_audio_sample_batch(STOCK_AUDIO);
    retro_set_input_poll(STOCK_POLL);
    retro_set_input_state(STOCK_INPUT);
    retro_set_environment(xgo_minimal_environment);
    retro_init();

    /* Native NES run_game() has already populated this arena. */
    GAME_INFO.path = filename;
    GAME_INFO.data = ROM_BUFFER;
    GAME_INFO.size = RUN_FILE_SIZE;
    GAME_INFO.meta = 0;

    /*
     * Stock save-state files belong to the embedded 2017 FCEUmm build. Do not
     * let the first newer-core experiment consume or overwrite them.
     */
    GFN_STATE_LOAD = disabled_state_io;
    GFN_STATE_SAVE = disabled_state_io;
    GFN_GET_REGION = retro_get_region;
    GFN_GET_AV = retro_get_system_av_info;
    GFN_LOAD_GAME = retro_load_game;
    GFN_UNLOAD_GAME = retro_unload_game;
    GFN_RUN = retro_run;
    GFN_FRAMESKIP = 0;

    retro_set_controller_port_device(0, 1); /* RETRO_DEVICE_JOYPAD */
    retro_set_controller_port_device(1, 1);

    FW_RUN_EMULATOR(load_state);

    retro_deinit();
    return 0;
}
