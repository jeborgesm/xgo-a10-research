/*
 * Synthetic XGO libretro bring-up loader.
 *
 * This loader is a controlled bridge between the raw 0x87000000 execution
 * probe and a real Multicore emulator core. It loads a tiny synthetic core,
 * wires it to the stock XGO libretro callbacks, populates the same global
 * function-pointer slots used by XGO run_emulator(), and then hands control to
 * the stock run loop.
 *
 * Normal GBA filenames pass through unchanged to stock run_gba().
 *
 * No SPI NOR updater path is used.
 */

typedef unsigned int size_t;
typedef int bool;
typedef struct FILE FILE;

typedef FILE *(*fopen_fn)(const char *, const char *);
typedef size_t (*fread_fn)(void *, size_t, size_t, FILE *);
typedef int (*fclose_fn)(FILE *);
typedef void (*run_gba_fn)(const char *, int);
typedef int (*dly_fn)(unsigned);
typedef bool (*environment_cb)(unsigned, void *);
typedef void (*video_cb)(const void *, unsigned, unsigned, size_t);
typedef size_t (*audio_batch_cb)(const short *, size_t);
typedef void (*poll_cb)(void);
typedef short (*input_cb)(unsigned, unsigned, unsigned, unsigned);

struct game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};

struct core_api {
    void (*init)(void);
    void (*deinit)(void);
    unsigned (*api_version)(void);
    void (*get_system_info)(void *);
    void (*get_system_av_info)(void *);
    void (*set_environment)(environment_cb);
    void (*set_video)(video_cb);
    void (*set_audio_sample)(void *);
    void (*set_audio_batch)(audio_batch_cb);
    void (*set_poll)(poll_cb);
    void (*set_input)(input_cb);
    void (*set_port)(unsigned, unsigned);
    void (*reset)(void);
    void (*run)(void);
    size_t (*serialize_size)(void);
    bool (*serialize)(void *, size_t);
    bool (*unserialize)(const void *, size_t);
    void (*cheat_reset)(void);
    void (*cheat_set)(unsigned, bool, const char *);
    bool (*load_game)(const struct game_info *);
    bool (*load_special)(unsigned, const struct game_info *, size_t);
    void (*unload)(void);
    unsigned (*region)(void);
    void *(*memory_data)(unsigned);
    size_t (*memory_size)(unsigned);
};

typedef struct core_api *(*core_entry_fn)(void);

#define FW_FOPEN       ((fopen_fn)0x802b3524u)
#define FW_FREAD       ((fread_fn)0x802b3698u)
#define FW_FCLOSE      ((fclose_fn)0x802b2f40u)
#define FW_RUN_GBA     ((run_gba_fn)0x80360110u)
#define FW_DLY_TSK     ((dly_fn)0x8030f480u)
#define FW_RUN_EMULATOR ((void (*)(int))0x8035ed48u)

#define STOCK_VIDEO ((video_cb)0x8035e70cu)
#define STOCK_AUDIO ((audio_batch_cb)0x8035e7d8u)
#define STOCK_POLL  ((poll_cb)0x8035ea30u)
#define STOCK_INPUT ((input_cb)0x8035eb20u)
#define STOCK_ENV   ((environment_cb)0x8035eb64u)

#define HEAP_BREAK  (*(volatile unsigned *)0x80c337b0u)
#define RAMSIZE     (*(volatile unsigned *)0x80c2ce6cu)
#define SOUND_FLAGS (*(volatile unsigned *)0x80c2e80cu)
#define GAME_INFO   (*(volatile struct game_info *)0x80c2e914u)

#define GFN_STATE_SAVE  (*(int (**)(const char *))0x80c33a70u)
#define GFN_GET_REGION  (*(unsigned (**)(void))0x80c33a9cu)
#define GFN_GET_AV      (*(void (**)(void *))0x80c33aacu)
#define GFN_STATE_LOAD  (*(int (**)(const char *))0x80c33ac0u)
#define GFN_LOAD_GAME   (*(bool (**)(const struct game_info *))0x80c33accu)
#define GFN_UNLOAD_GAME (*(void (**)(void))0x80c33ad4u)
#define ROM_BUFFER      (*(void **)0x80c33ad8u)
#define GFN_FRAMESKIP   (*(void **)0x80c33ae0u)
#define GFN_RUN         (*(void (**)(void))0x80c33ae4u)
#define RUN_FILE_SIZE   (*(volatile unsigned *)0x80c33a7cu)

static int string_equal(const char *a, const char *b)
{
    unsigned i = 0;

    if (!a)
        return 0;

    while (b[i]) {
        if (a[i] != b[i])
            return 0;
        i++;
    }

    return a[i] == 0;
}

static int state_stub(const char *path)
{
    (void)path;
    return 1;
}

static void flush_all_caches(void)
{
    unsigned p;

    for (p = 0x80000000u; p <= 0x80004000u; p += 16)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)" : : "r"(p));

    __asm__ volatile("sync; nop; nop");

    for (p = 0x80000000u; p <= 0x80004000u; p += 16)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)" : : "r"(p));

    __asm__ volatile("nop; nop; nop; nop; nop");
}

__attribute__((section(".entry"), used))
void xgo_loader_entry(const char *filename, int load_state)
{
    static const char probe[] = "/mnt/sda1/ROMS/XGO_LIBRETRO_PROBE.gba";
    FILE *f;
    unsigned old_limit;
    unsigned bytes_read;
    struct core_api *api;

    if (!string_equal(filename, probe)) {
        FW_RUN_GBA(filename, load_state);
        return;
    }

    if (HEAP_BREAK >= 0x87000000u)
        return;

    f = FW_FOPEN("/mnt/sda1/XGO_LIBRETRO_PROBE.BIN", "rb");
    if (!f)
        return;

    old_limit = RAMSIZE;
    RAMSIZE = 0x87000000u;

    bytes_read = FW_FREAD((void *)0x87000000u, 1, 0x10000u, f);
    FW_FCLOSE(f);

    if (!bytes_read) {
        RAMSIZE = old_limit;
        return;
    }

    flush_all_caches();
    api = ((core_entry_fn)0x87000000u)();
    if (!api) {
        RAMSIZE = old_limit;
        return;
    }

    /* Same sound-task shutdown convention used by the stock wrappers. */
    SOUND_FLAGS &= 0xfffeu;
    while (SOUND_FLAGS != 0)
        FW_DLY_TSK(1);

    /* Wire the external core into XGO's already-working frontend transport. */
    api->set_video(STOCK_VIDEO);
    api->set_audio_batch(STOCK_AUDIO);
    api->set_poll(STOCK_POLL);
    api->set_input(STOCK_INPUT);
    api->set_environment(STOCK_ENV);
    api->init();

    GAME_INFO.path = filename;
    GAME_INFO.data = (const void *)ROM_BUFFER;
    GAME_INFO.size = RUN_FILE_SIZE;
    GAME_INFO.meta = 0;

    GFN_STATE_LOAD = state_stub;
    GFN_STATE_SAVE = state_stub;
    GFN_GET_REGION = api->region;
    GFN_GET_AV = api->get_system_av_info;
    GFN_LOAD_GAME = api->load_game;
    GFN_UNLOAD_GAME = api->unload;
    GFN_RUN = api->run;
    GFN_FRAMESKIP = 0;

    FW_RUN_EMULATOR(load_state);

    api->deinit();
    RAMSIZE = old_limit;
}
