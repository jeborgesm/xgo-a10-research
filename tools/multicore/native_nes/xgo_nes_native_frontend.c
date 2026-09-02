/*
 * Native-main-list FCEUmm frontend for XGO.
 *
 * Entry comes from the patched NES call in run_game() at 0x80360e20. At that
 * point stock run_game() has already loaded the selected NES file into the
 * 64-MiB gp_buf_64m arena and stored an aligned length in g_run_file_size.
 *
 * Link with xgo_preloaded_rom_sbrk.c so external newlib begins after the
 * preloaded ROM prefix instead of overwriting it.
 *
 * The injected native NES loader repairs the stock IRQ $gp path before this
 * entry point is called. Keep that transition logic in one place.
 */

#ifdef XGO_WITH_NEWLIB
#include <stddef.h>
#else
typedef unsigned int size_t;
#endif

typedef int bool;
#define true 1
#define false 0

#define RETRO_DEVICE_JOYPAD 1u
#define XGO_SYSTEM_NES 0x0001u
#define MAX_ROM_SIZE 0x04000000u

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
extern bool xgo_minimal_environment(unsigned, void *);

#define STOCK_VIDEO ((video_cb)0x8035e70cu)
#define STOCK_AUDIO ((audio_batch_cb)0x8035e7d8u)
#define STOCK_POLL  ((poll_cb)0x8035ea30u)
#define STOCK_INPUT ((input_cb)0x8035eb20u)

#define FW_RUN_EMULATOR ((void (*)(int))0x8035ed48u)

typedef struct FILE_ FILE;
#define FW_FOPEN  ((FILE *(*)(const char *, const char *))0x802b3524u)
#define FW_FSEEKO ((int (*)(FILE *, int, int))0x802b3804u)
#define FW_FTELL  ((int (*)(FILE *))0x802b3f1cu)
#define FW_FCLOSE ((int (*)(FILE *))0x802b2f40u)

#define GAME_INFO     (*(volatile struct retro_game_info *)0x80c2e914u)
#define ROM_BUFFER    (*(void **)0x80c33ad8u)
#define RUN_FILE_SIZE (*(volatile unsigned *)0x80c33a7cu)
#define SYSTEM_FAMILY (*(volatile unsigned short *)0x80c33ad0u)

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

/* run_game rounds g_run_file_size upward to four bytes before fread(). */
static int exact_rom_size(const char *filename, unsigned *size_out)
{
    FILE *f;
    int size;

    f = FW_FOPEN(filename, "rb");
    if (!f)
        return 0;
    if (FW_FSEEKO(f, 0, 2) != 0) {
        FW_FCLOSE(f);
        return 0;
    }
    size = FW_FTELL(f);
    FW_FCLOSE(f);

    if (size <= 0 || (unsigned)size > MAX_ROM_SIZE)
        return 0;
    *size_out = (unsigned)size;
    return 1;
}

#ifdef XGO_WITH_NEWLIB
#include <reent.h>
extern void __libc_init_array(void);
extern void __sinit(struct _reent *);
static void init_core_runtime(void)
{
    /* Loader has already zeroed the XGOC runtime-only region including BSS. */
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
    struct retro_game_info old_game_info;
    unsigned old_run_file_size;
    unsigned rom_size;
    unsigned short old_system_family;
    int (*old_state_save)(const char *);
    int (*old_state_load)(const char *);
    unsigned (*old_get_region)(void);
    void (*old_get_av)(struct retro_system_av_info *);
    bool (*old_load_game)(const struct retro_game_info *);
    void (*old_unload_game)(void);
    void (*old_run)(void);
    void *old_frameskip;

    /*
     * g_run_file_size is already populated before entry and is used by the
     * preloaded-ROM sbrk implementation to reserve the ROM prefix. Initialize
     * newlib only after that stock preload has happened.
     */
    init_core_runtime();

    if (!ROM_BUFFER || !exact_rom_size(filename, &rom_size))
        return -1;

    old_game_info.path = GAME_INFO.path;
    old_game_info.data = GAME_INFO.data;
    old_game_info.size = GAME_INFO.size;
    old_game_info.meta = GAME_INFO.meta;
    old_run_file_size = RUN_FILE_SIZE;
    old_system_family = SYSTEM_FAMILY;
    old_state_save = GFN_STATE_SAVE;
    old_state_load = GFN_STATE_LOAD;
    old_get_region = GFN_GET_REGION;
    old_get_av = GFN_GET_AV;
    old_load_game = GFN_LOAD_GAME;
    old_unload_game = GFN_UNLOAD_GAME;
    old_run = GFN_RUN;
    old_frameskip = GFN_FRAMESKIP;

    SYSTEM_FAMILY = XGO_SYSTEM_NES;

    retro_set_video_refresh(STOCK_VIDEO);
    retro_set_audio_sample_batch(STOCK_AUDIO);
    retro_set_input_poll(STOCK_POLL);
    retro_set_input_state(STOCK_INPUT);
    retro_set_environment(xgo_minimal_environment);
    retro_init();

    /* Use the stock-preloaded ROM directly; no second ROM allocation/copy. */
    RUN_FILE_SIZE = rom_size;
    GAME_INFO.path = filename;
    GAME_INFO.data = ROM_BUFFER;
    GAME_INFO.size = rom_size;
    GAME_INFO.meta = 0;

    GFN_STATE_LOAD = disabled_state_io;
    GFN_STATE_SAVE = disabled_state_io;
    GFN_GET_REGION = retro_get_region;
    GFN_GET_AV = retro_get_system_av_info;
    GFN_LOAD_GAME = retro_load_game;
    GFN_UNLOAD_GAME = retro_unload_game;
    GFN_RUN = retro_run;
    GFN_FRAMESKIP = 0;

    retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD);
    retro_set_controller_port_device(1, RETRO_DEVICE_JOYPAD);

    FW_RUN_EMULATOR(load_state);
    retro_deinit();

    GFN_STATE_SAVE = old_state_save;
    GFN_STATE_LOAD = old_state_load;
    GFN_GET_REGION = old_get_region;
    GFN_GET_AV = old_get_av;
    GFN_LOAD_GAME = old_load_game;
    GFN_UNLOAD_GAME = old_unload_game;
    GFN_RUN = old_run;
    GFN_FRAMESKIP = old_frameskip;
    SYSTEM_FAMILY = old_system_family;
    RUN_FILE_SIZE = old_run_file_size;
    GAME_INFO.path = old_game_info.path;
    GAME_INFO.data = old_game_info.data;
    GAME_INFO.size = old_game_info.size;
    GAME_INFO.meta = old_game_info.meta;

    return 0;
}
