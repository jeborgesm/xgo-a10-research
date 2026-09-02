/*
 * Native-main-list FCEUmm frontend for XGO.
 *
 * Normal builds retain the current-region visual diagnostics. Bring-up ladder
 * builds define XGO_BRINGUP_RETURN_STAGE; in those builds all visual diagnostics
 * are compiled out and the real frontend deliberately returns at one selected
 * checkpoint. This gives hardware a dependency-free observable:
 *
 *   return to menu = checkpoint was reached safely
 *   freeze          = failure occurred before the selected checkpoint returned
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
#define DIAG_W 128u
#define DIAG_H 64u
#define DIAG_PIXEL_PITCH DIAG_W

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
extern int xgo_stock_osd_region_write(const void *, unsigned, unsigned, unsigned);
extern void xgo_stock_video_refresh(const void *, unsigned, unsigned, size_t);
extern size_t xgo_stock_audio_sample_batch(const short *, size_t);
extern void xgo_stock_input_poll(void);
extern short xgo_stock_input_state(unsigned, unsigned, unsigned, unsigned);
extern void xgo_stock_run_emulator(int);

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
#define EMULATOR_LOOP_COUNTER (*(volatile unsigned *)0x80c2e964u)

#define GFN_STATE_SAVE  (*(int (**)(const char *))0x80c33a70u)
#define GFN_GET_REGION  (*(unsigned (**)(void))0x80c33a9cu)
#define GFN_GET_AV      (*(void (**)(struct retro_system_av_info *))0x80c33aacu)
#define GFN_STATE_LOAD  (*(int (**)(const char *))0x80c33ac0u)
#define GFN_LOAD_GAME   (*(bool (**)(const struct retro_game_info *))0x80c33accu)
#define GFN_UNLOAD_GAME (*(void (**)(void))0x80c33ad4u)
#define GFN_FRAMESKIP   (*(void **)0x80c33ae0u)
#define GFN_RUN         (*(void (**)(void))0x80c33ae4u)

#ifndef XGO_BRINGUP_RETURN_STAGE
static unsigned short diag_frame[DIAG_W * DIAG_H];

static unsigned short diag_color(unsigned stage)
{
    static const unsigned short colors[] = {
        0x0000, 0xf800, 0x07e0, 0x001f,
        0xffe0, 0xf81f, 0x07ff, 0xffff,
        0x7bef, 0x780f, 0x03ef, 0xfbe0,
        0x8410, 0xfc10, 0x87f0, 0x801f
    };
    if (stage >= (sizeof(colors) / sizeof(colors[0])))
        stage = (sizeof(colors) / sizeof(colors[0])) - 1u;
    return colors[stage];
}

static void diag_screen(unsigned stage)
{
    unsigned x, y;
    unsigned short bg = diag_color(stage);

    for (y = 0; y < DIAG_H; ++y) {
        for (x = 0; x < DIAG_W; ++x) {
            unsigned short c;
            if (y < (DIAG_H / 2u)) {
                unsigned bit = x >> 4;
                c = (stage & (1u << bit)) ? 0xffffu : 0x0000u;
            } else {
                c = bg;
            }
            diag_frame[y * DIAG_W + x] = c;
        }
    }

    (void)xgo_stock_osd_region_write(diag_frame, DIAG_W, DIAG_H,
                                     DIAG_PIXEL_PITCH);
}
#define XGO_DIAG(n) diag_screen(n)
#else
#define XGO_DIAG(n) ((void)0)
#endif

#ifdef XGO_BRINGUP_RETURN_STAGE
#define XGO_RETURN_STAGE(n) do { if (XGO_BRINGUP_RETURN_STAGE == (n)) return 0; } while (0)
#else
#define XGO_RETURN_STAGE(n) ((void)0)
#endif

unsigned xgo_diag_get_region(void)
{
    unsigned r;
    XGO_DIAG(10);
    r = retro_get_region();
    XGO_DIAG(11);
    return r;
}

void xgo_diag_get_av(struct retro_system_av_info *info)
{
    XGO_DIAG(8);
    retro_get_system_av_info(info);
    XGO_DIAG(9);
}

bool xgo_diag_load_game(const struct retro_game_info *info)
{
    bool ok;
    XGO_DIAG(6);
    ok = retro_load_game(info);
    XGO_DIAG(7);
    return ok;
}

void xgo_diag_unload_game(void)
{
    XGO_DIAG(14);
    retro_unload_game();
    XGO_DIAG(15);
}

void xgo_diag_run(void)
{
    static unsigned first_run;
    if (first_run == 0) {
        first_run = 1;
        XGO_DIAG(12);
    }
    retro_run();
    if (first_run == 1) {
        first_run = 2;
        XGO_DIAG(13);
    }
}

int xgo_disabled_state_io(const char *path)
{
    (void)path;
    return 0;
}

#ifdef XGO_WITH_NEWLIB
#include <reent.h>
extern void __libc_init_array(void);
extern void __sinit(struct _reent *);
static void init_core_runtime(void)
{
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

    /* Stage 1: GP entry veneer reached C and a normal C return is possible. */
    XGO_RETURN_STAGE(1);

    XGO_DIAG(1);
    init_core_runtime();

    /* Stage 2: external newlib/reentrancy/constructor initialization returned. */
    XGO_RETURN_STAGE(2);
    XGO_DIAG(2);

    rom_size = RUN_FILE_SIZE;
    if (!ROM_BUFFER || rom_size == 0 || rom_size > MAX_ROM_SIZE) {
        XGO_DIAG(15);
        return -1;
    }

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

    /* Stage 3: stock ROM/global state can be read safely under external GP. */
    XGO_RETURN_STAGE(3);

    SYSTEM_FAMILY = XGO_SYSTEM_NES;
    EMULATOR_LOOP_COUNTER = 0;

    retro_set_video_refresh(xgo_stock_video_refresh);
    retro_set_audio_sample_batch(xgo_stock_audio_sample_batch);
    retro_set_input_poll(xgo_stock_input_poll);
    retro_set_input_state(xgo_stock_input_state);
    retro_set_environment(xgo_minimal_environment);

    /* Stage 4: libretro callback setter calls completed. */
    XGO_RETURN_STAGE(4);
    XGO_DIAG(3);

    retro_init();

    /* Stage 5: FCEUmm retro_init() completed and returned. */
    XGO_RETURN_STAGE(5);
    XGO_DIAG(4);

    GAME_INFO.path = filename;
    GAME_INFO.data = ROM_BUFFER;
    GAME_INFO.size = rom_size;
    GAME_INFO.meta = 0;

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

    /* Stage 6: stock frontend slots/content-info/controller setup completed. */
    XGO_RETURN_STAGE(6);
    XGO_DIAG(5);

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
