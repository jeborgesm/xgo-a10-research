/*
 * Native-main-list FCEUmm frontend for XGO.
 *
 * Entry comes from the patched NES call in run_game() at 0x80360e20. At that
 * point stock run_game() has already loaded the selected NES file into the
 * 64-MiB gp_buf_64m arena and stored an aligned length in g_run_file_size.
 *
 * Hardware bring-up uses a deliberately primitive SD trace written through
 * already-GP-safe stock VFS veneers. No printf, malloc, stdio or raw stock
 * callback pointers are used by the tracer.
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
#define FS_O_WRONLY 0x0001
#define FS_O_APPEND 0x0008
#define FS_O_CREAT  0x0100
#define FS_O_TRUNC  0x0200
#define DIAG_PATH "/mnt/sda1/xgo-native.log"

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
extern int xgo_stock_fs_open(const char *, int, int);
extern int xgo_stock_fs_write(int, const void *, unsigned);
extern int xgo_stock_fs_close(int);

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

static unsigned diag_len(const char *s)
{
    unsigned n = 0;
    while (s[n]) ++n;
    return n;
}

static void diag_write_flags(const char *s, int flags)
{
    int fd = xgo_stock_fs_open(DIAG_PATH, flags, 0666);
    if (fd < 0)
        return;
    (void)xgo_stock_fs_write(fd, s, diag_len(s));
    (void)xgo_stock_fs_close(fd);
}

static void diag_reset(const char *s)
{
    diag_write_flags(s, FS_O_WRONLY | FS_O_CREAT | FS_O_TRUNC);
}

static void diag(const char *s)
{
    diag_write_flags(s, FS_O_WRONLY | FS_O_CREAT | FS_O_APPEND);
}

/* These are the actual targets of the stock->core GP veneers during the
 * diagnostic build. They prove entry and return around each libretro callback. */
unsigned xgo_diag_get_region(void)
{
    unsigned r;
    diag("R1 get_region enter\n");
    r = retro_get_region();
    diag("R2 get_region return\n");
    return r;
}

void xgo_diag_get_av(struct retro_system_av_info *info)
{
    diag("A1 get_av enter\n");
    retro_get_system_av_info(info);
    diag("A2 get_av return\n");
}

bool xgo_diag_load_game(const struct retro_game_info *info)
{
    bool ok;
    diag("L1 retro_load_game enter\n");
    ok = retro_load_game(info);
    diag(ok ? "L2 retro_load_game TRUE\n" : "L2 retro_load_game FALSE\n");
    return ok;
}

void xgo_diag_unload_game(void)
{
    diag("U1 retro_unload_game enter\n");
    retro_unload_game();
    diag("U2 retro_unload_game return\n");
}

void xgo_diag_run(void)
{
    static unsigned first_run;
    if (first_run == 0) {
        first_run = 1;
        diag("F1 first retro_run enter\n");
    }
    retro_run();
    if (first_run == 1) {
        first_run = 2;
        diag("F2 first retro_run return\n");
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

    diag_reset("E0 core C entry\n");
    init_core_runtime();
    diag("E1 runtime initialized\n");

    rom_size = RUN_FILE_SIZE;
    if (!ROM_BUFFER || rom_size == 0 || rom_size > MAX_ROM_SIZE) {
        diag("E2 ROM validation FAILED\n");
        return -1;
    }
    diag("E2 ROM validation OK\n");

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
    diag("E3 before retro_init\n");
    retro_init();
    diag("E4 after retro_init\n");

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

    diag("E5 before stock run_emulator\n");
    xgo_stock_run_emulator(load_state);
    diag("E6 stock run_emulator returned\n");
    retro_deinit();
    diag("E7 retro_deinit returned\n");

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

    diag("E8 frontend return\n");
    return 0;
}
