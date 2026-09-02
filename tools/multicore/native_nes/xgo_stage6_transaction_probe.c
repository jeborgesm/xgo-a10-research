/*
 * Transactional Stage-6 bring-up probe.
 *
 * Hardware test 08 proved stages 1-5 of the normal frontend return cleanly,
 * but the original stage-6 checkpoint returned while stock GAME_INFO/GFN slots
 * were still overwritten.  That made a post-return stock freeze indistinguish-
 * able from a failure inside the stage-5 -> stage-6 setup window.
 *
 * This probe repeats the already-proven prefix, then subdivides only that window.
 * Before every deliberate return it restores all stock globals modified by the
 * new stage.  XGO_BRINGUP_SUBSTAGE values:
 *
 *   51  GAME_INFO write + restore
 *   52  GAME_INFO + GFN slot writes + restore
 *   53  above + controller port 0 setup + restore
 *   54  above + controller port 1 setup + restore
 */

#include <stddef.h>
#include <reent.h>

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

extern void xgo_stock_video_refresh(const void *, unsigned, unsigned, size_t);
extern size_t xgo_stock_audio_sample_batch(const short *, size_t);
extern void xgo_stock_input_poll(void);
extern short xgo_stock_input_state(unsigned, unsigned, unsigned, unsigned);

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

#ifndef XGO_BRINGUP_SUBSTAGE
#error XGO_BRINGUP_SUBSTAGE must be defined as 51, 52, 53, or 54
#endif
#if XGO_BRINGUP_SUBSTAGE < 51 || XGO_BRINGUP_SUBSTAGE > 54
#error XGO_BRINGUP_SUBSTAGE must be 51, 52, 53, or 54
#endif

extern void __libc_init_array(void);
extern void __sinit(struct _reent *);

static void init_core_runtime(void)
{
    _REENT_INIT_PTR(_REENT);
    __sinit(_REENT);
    __libc_init_array();
}

/* Reverse-GP veneer targets.  They are installed only as pointer values here;
 * the transactional probe returns before stock run_emulator can invoke them. */
unsigned xgo_diag_get_region(void)
{
    return retro_get_region();
}

void xgo_diag_get_av(struct retro_system_av_info *info)
{
    retro_get_system_av_info(info);
}

bool xgo_diag_load_game(const struct retro_game_info *info)
{
    return retro_load_game(info);
}

void xgo_diag_unload_game(void)
{
    retro_unload_game();
}

void xgo_diag_run(void)
{
    retro_run();
}

int xgo_disabled_state_io(const char *path)
{
    (void)path;
    return 0;
}

struct stock_snapshot {
    struct retro_game_info game_info;
    int (*state_save)(const char *);
    int (*state_load)(const char *);
    unsigned (*get_region)(void);
    void (*get_av)(struct retro_system_av_info *);
    bool (*load_game)(const struct retro_game_info *);
    void (*unload_game)(void);
    void (*run)(void);
    void *frameskip;
};

static void snapshot_stock(struct stock_snapshot *s)
{
    s->game_info.path = GAME_INFO.path;
    s->game_info.data = GAME_INFO.data;
    s->game_info.size = GAME_INFO.size;
    s->game_info.meta = GAME_INFO.meta;
    s->state_save = GFN_STATE_SAVE;
    s->state_load = GFN_STATE_LOAD;
    s->get_region = GFN_GET_REGION;
    s->get_av = GFN_GET_AV;
    s->load_game = GFN_LOAD_GAME;
    s->unload_game = GFN_UNLOAD_GAME;
    s->run = GFN_RUN;
    s->frameskip = GFN_FRAMESKIP;
}

static void restore_game_info(const struct stock_snapshot *s)
{
    GAME_INFO.path = s->game_info.path;
    GAME_INFO.data = s->game_info.data;
    GAME_INFO.size = s->game_info.size;
    GAME_INFO.meta = s->game_info.meta;
}

static void restore_gfn(const struct stock_snapshot *s)
{
    GFN_STATE_SAVE = s->state_save;
    GFN_STATE_LOAD = s->state_load;
    GFN_GET_REGION = s->get_region;
    GFN_GET_AV = s->get_av;
    GFN_LOAD_GAME = s->load_game;
    GFN_UNLOAD_GAME = s->unload_game;
    GFN_RUN = s->run;
    GFN_FRAMESKIP = s->frameskip;
}

int __core_entry_c(const char *filename, int load_state)
{
    struct stock_snapshot old;
    unsigned rom_size;

    (void)load_state;

    /* Prefix already demonstrated safe by hardware stages 1-5. */
    init_core_runtime();

    rom_size = RUN_FILE_SIZE;
    if (!ROM_BUFFER || rom_size == 0 || rom_size > MAX_ROM_SIZE)
        return -1;

    snapshot_stock(&old);

    SYSTEM_FAMILY = XGO_SYSTEM_NES;
    EMULATOR_LOOP_COUNTER = 0;

    retro_set_video_refresh(xgo_stock_video_refresh);
    retro_set_audio_sample_batch(xgo_stock_audio_sample_batch);
    retro_set_input_poll(xgo_stock_input_poll);
    retro_set_input_state(xgo_stock_input_state);
    retro_set_environment(xgo_minimal_environment);
    retro_init();

    GAME_INFO.path = filename;
    GAME_INFO.data = ROM_BUFFER;
    GAME_INFO.size = rom_size;
    GAME_INFO.meta = 0;

#if XGO_BRINGUP_SUBSTAGE == 51
    restore_game_info(&old);
    return 0;
#else
    GFN_STATE_LOAD = xgo_core_state_io;
    GFN_STATE_SAVE = xgo_core_state_io;
    GFN_GET_REGION = xgo_core_get_region;
    GFN_GET_AV = xgo_core_get_av;
    GFN_LOAD_GAME = xgo_core_load_game;
    GFN_UNLOAD_GAME = xgo_core_unload_game;
    GFN_RUN = xgo_core_run;
    GFN_FRAMESKIP = 0;
#endif

#if XGO_BRINGUP_SUBSTAGE == 52
    restore_gfn(&old);
    restore_game_info(&old);
    return 0;
#elif XGO_BRINGUP_SUBSTAGE >= 53
    retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD);
#endif

#if XGO_BRINGUP_SUBSTAGE == 53
    restore_gfn(&old);
    restore_game_info(&old);
    return 0;
#elif XGO_BRINGUP_SUBSTAGE == 54
    retro_set_controller_port_device(1, RETRO_DEVICE_JOYPAD);
    restore_gfn(&old);
    restore_game_info(&old);
    return 0;
#endif

    return 0;
}
