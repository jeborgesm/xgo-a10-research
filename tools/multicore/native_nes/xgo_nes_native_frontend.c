/*
 * Native-main-list FCEUmm frontend for XGO.
 *
 * Hardware bring-up visual probe: every important execution boundary submits
 * a synthetic 256x240 RGB565 frame through the already-GP-safe stock XGO video
 * callback. The probe deliberately uses no filesystem, printf, malloc or libc.
 * Loader-side XGOC BSS clearing makes the static framebuffer usable even before
 * external newlib initialization.
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
#define DIAG_W 256u
#define DIAG_H 240u
#define DIAG_PITCH (DIAG_W * 2u)

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

/*
 * Visual stage encoding.
 *
 * The full background changes with every stage. The top 40 rows additionally
 * encode the stage number as eight 32-pixel-wide binary bars: white means 1,
 * black means 0, least-significant bit at the left. This keeps identification
 * robust even if RGB565 channel ordering differs from expectation.
 */
static unsigned short diag_frame[DIAG_W * DIAG_H];

static unsigned short diag_color(unsigned stage)
{
    static const unsigned short colors[] = {
        0x0000, /* unused */
        0xf800, /* 1 red */
        0x07e0, /* 2 green */
        0x001f, /* 3 blue */
        0xffe0, /* 4 yellow */
        0xf81f, /* 5 magenta */
        0x07ff, /* 6 cyan */
        0xffff, /* 7 white */
        0x7bef, /* 8 gray */
        0x780f, /* 9 purple-ish */
        0x03ef, /* 10 teal-ish */
        0xfbe0, /* 11 orange-ish */
        0x8410, /* 12 dark gray */
        0xfc10, /* 13 warm */
        0x87f0, /* 14 lime-ish */
        0x801f  /* 15 violet-ish */
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
            unsigned short c = bg;
            if (y < 40u) {
                unsigned bit = x >> 5; /* 8 bars, 32 pixels each */
                c = (stage & (1u << bit)) ? 0xffffu : 0x0000u;
            }
            diag_frame[y * DIAG_W + x] = c;
        }
    }

    xgo_stock_video_refresh(diag_frame, DIAG_W, DIAG_H, DIAG_PITCH);
}

/* These are the true targets of the stock->core GP veneers. */
unsigned xgo_diag_get_region(void)
{
    unsigned r;
    diag_screen(10); /* region enter */
    r = retro_get_region();
    diag_screen(11); /* region returned */
    return r;
}

void xgo_diag_get_av(struct retro_system_av_info *info)
{
    diag_screen(8); /* AV enter */
    retro_get_system_av_info(info);
    diag_screen(9); /* AV returned */
}

bool xgo_diag_load_game(const struct retro_game_info *info)
{
    bool ok;
    diag_screen(6); /* retro_load_game enter */
    ok = retro_load_game(info);
    diag_screen(7); /* retro_load_game returned */
    return ok;
}

void xgo_diag_unload_game(void)
{
    diag_screen(14);
    retro_unload_game();
    diag_screen(15);
}

void xgo_diag_run(void)
{
    static unsigned first_run;
    if (first_run == 0) {
        first_run = 1;
        diag_screen(12); /* first retro_run enter */
    }
    retro_run();
    if (first_run == 1) {
        first_run = 2;
        diag_screen(13); /* first retro_run returned */
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

    /* Stage 1 is intentionally before ANY newlib/runtime initialization. */
    diag_screen(1);
    init_core_runtime();
    diag_screen(2);

    rom_size = RUN_FILE_SIZE;
    if (!ROM_BUFFER || rom_size == 0 || rom_size > MAX_ROM_SIZE) {
        diag_screen(15);
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

    SYSTEM_FAMILY = XGO_SYSTEM_NES;
    EMULATOR_LOOP_COUNTER = 0;

    retro_set_video_refresh(xgo_stock_video_refresh);
    retro_set_audio_sample_batch(xgo_stock_audio_sample_batch);
    retro_set_input_poll(xgo_stock_input_poll);
    retro_set_input_state(xgo_stock_input_state);
    retro_set_environment(xgo_minimal_environment);

    diag_screen(3); /* before retro_init */
    retro_init();
    diag_screen(4); /* after retro_init */

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

    diag_screen(5); /* immediately before stock run_emulator */
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
