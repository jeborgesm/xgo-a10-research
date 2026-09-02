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
 * xgo_core_entry.s owns the true 0x87000000 external entry. It switches from
 * the stock firmware $gp to this image's linker-provided _gp before entering
 * this C frontend, then restores the stock $gp on return. xgo_gp_bridges.s
 * performs the same transition at every stock/core callback boundary.
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

/* Transparent core -> stock veneers. */
extern void xgo_stock_video_refresh(const void *, unsigned, unsigned, size_t);
extern size_t xgo_stock_audio_sample_batch(const short *, size_t);
extern void xgo_stock_input_poll(void);
extern short xgo_stock_input_state(unsigned, unsigned, unsigned, unsigned);
extern void xgo_stock_run_emulator(int);

typedef struct FILE_ FILE;
extern FILE *xgo_stock_fopen(const char *, const char *);
extern int xgo_stock_fseeko(FILE *, int, int);
extern int xgo_stock_ftell(FILE *);
extern int xgo_stock_fclose(FILE *);

/* Transparent stock run_emulator -> core veneers. */
extern unsigned xgo_core_get_region(void);
extern void xgo_core_get_av(struct retro_system_av_info *);
extern bool xgo_core_load_game(const struct retro_game_info *);
extern void xgo_core_unload_game(void);
extern void xgo_core_run(void);
extern int xgo_core_state_io(const char *);

#define GAME_INFO     (*(volatile struct retro_game_info *)0x80c2e914u)
#define ROM_BUFFER    (*(void **)0x80c33ad8u)
#define RUN_FILE_SIZE (*(volatile unsigned *)0x80c33a7cu)
#define SYSTEM_FAMILY (*(volatile unsigned short *)0x80c33ad0u)

/* Stock run_nes clears this immediately before installing libretro callbacks.
 * run_emulator then uses it in its timing/frameskip bookkeeping. */
#define EMULATOR_LOOP_COUNTER (*(volatile unsigned *)0x80c2e964u)

#define GFN_STATE_SAVE  (*(int (**)(const char *))0x80c33a70u)
#define GFN_GET_REGION  (*(unsigned (**)(void))0x80c33a9cu)
#define GFN_GET_AV      (*(void (**)(struct retro_system_av_info *))0x80c33aacu)
#define GFN_STATE_LOAD  (*(int (**)(const char *))0x80c33ac0u)
#define GFN_LOAD_GAME   (*(bool (**)(const struct retro_game_info *))0x80c33accu)
#define GFN_UNLOAD_GAME (*(void (**)(void))0x80c33ad4u)
#define GFN_FRAMESKIP   (*(void **)0x80c33ae0u)
#define GFN_RUN         (*(void (**)(void))0x80c33ae4u)

/* Called only through xgo_core_state_io, which establishes the external GP
 * before entering C from stock run_emulator(). */
int xgo_disabled_state_io(const char *path)
{
    (void)path;
    return 0;
}

/* run_game rounds g_run_file_size upward to four bytes before fread(). */
static int exact_rom_size(const char *filename, unsigned *size_out)
{
    FILE *f;
    int size;

    f = xgo_stock_fopen(filename, "rb");
    if (!f)
        return 0;
    if (xgo_stock_fseeko(f, 0, 2) != 0) {
        xgo_stock_fclose(f);
        return 0;
    }
    size = xgo_stock_ftell(f);
    xgo_stock_fclose(f);

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

int __core_entry_c(const char *filename, int load_state)
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

    /* g_run_file_size is already populated before entry and is used by the
     * preloaded-ROM sbrk implementation to reserve the ROM prefix. */
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

    /* Match stock run_nes shared timing state. */
    EMULATOR_LOOP_COUNTER = 0;

    /* FCEUmm executes with external _gp. Every callback it invokes into stock
     * therefore points at a veneer that installs XGO_STOCK_GP for the call. */
    retro_set_video_refresh(xgo_stock_video_refresh);
    retro_set_audio_sample_batch(xgo_stock_audio_sample_batch);
    retro_set_input_poll(xgo_stock_input_poll);
    retro_set_input_state(xgo_stock_input_state);
    retro_set_environment(xgo_minimal_environment);
    retro_init();

    /* Use the stock-preloaded ROM directly; no second ROM allocation/copy. */
    RUN_FILE_SIZE = rom_size;
    GAME_INFO.path = filename;
    GAME_INFO.data = ROM_BUFFER;
    GAME_INFO.size = rom_size;
    GAME_INFO.meta = 0;

    /* run_emulator executes under stock GP, so every function pointer that can
     * lead back into the external image must first restore the core _gp. */
    GFN_STATE_LOAD = xgo_core_state_io;
    GFN_STATE_SAVE = xgo_core_state_io;
    GFN_GET_REGION = xgo_core_get_region;
    GFN_GET_AV = xgo_core_get_av;
    GFN_LOAD_GAME = xgo_core_load_game;
    GFN_UNLOAD_GAME = xgo_core_unload_game;
    GFN_RUN = xgo_core_run;
    GFN_FRAMESKIP = 0;

    retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD);
    retro_set_controller_port_device(1, RETRO_DEVICE_JOYPAD);

    xgo_stock_run_emulator(load_state);
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
