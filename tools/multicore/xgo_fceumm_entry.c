/*
 * XGO-native entry bridge for the first fully linked external FCEUmm core.
 *
 * The XGOC loader calls __start(original_stub_path, load_state). FCEUmm is
 * statically linked into this image, so no SF2000-style dynamic core API table
 * is needed: this bridge binds the core's ordinary libretro exports directly
 * into the already-mapped XGO stock run_emulator() indirection slots.
 */

typedef unsigned int u32;
typedef unsigned long size_t;
typedef int bool;

#define NULL ((void *)0)
#define NES_FAMILY 0x01u
#define FAMILY_MASK 0x00ffu
#define ROM_PREFIX "/mnt/sda1/ROMS/"
#define CORE_NAME "fceumm"
#define MAX_ROM_PATH 512u

struct retro_game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};

struct retro_system_av_info;

/* FCEUmm libretro exports, supplied by the pinned static archive. */
extern void retro_set_environment(bool (*cb)(unsigned, void *));
extern void retro_set_video_refresh(void (*cb)(const void *, unsigned, unsigned, size_t));
extern void retro_set_audio_sample_batch(size_t (*cb)(const short *, size_t));
extern void retro_set_input_poll(void (*cb)(void));
extern void retro_set_input_state(short (*cb)(unsigned, unsigned, unsigned, unsigned));
extern void retro_init(void);
extern void retro_deinit(void);
extern bool retro_load_game(const struct retro_game_info *);
extern void retro_unload_game(void);
extern void retro_run(void);
extern unsigned retro_get_region(void);
extern void retro_get_system_av_info(struct retro_system_av_info *);

/* XGO compatibility environment shim. */
extern bool xgo_minimal_environment(unsigned, void *);

/* Stock XGO callbacks/functions supplied by xgo_stockfw_symbols.ld. */
extern void retro_video_refresh_cb(const void *, unsigned, unsigned, size_t);
extern size_t retro_audio_sample_batch_cb(const short *, size_t);
extern void retro_input_poll_cb(void);
extern short retro_input_state_cb(unsigned, unsigned, unsigned, unsigned);
extern void run_emulator(int load_state);

/* Stock global indirection slots. */
extern struct retro_game_info g_retro_game_info;
extern int (*gfn_state_save)(const char *);
extern int (*gfn_state_load)(const char *);
extern unsigned (*gfn_retro_get_region)(void);
extern void (*gfn_get_system_av_info)(struct retro_system_av_info *);
extern bool (*gfn_retro_load_game)(const struct retro_game_info *);
extern void (*gfn_retro_unload_game)(void);
extern void (*gfn_retro_run)(void);
extern void (*gfn_frameskip)(int);
extern volatile u32 XGO_ACTIVE_SYSTEM_FAMILY;

/*
 * Session-scoped run-loop phase/counter. Every stock run_* wrapper zeros this
 * word immediately before installing/initializing its emulator core. The stock
 * run_emulator() loop subsequently reads, increments and resets it, so an
 * intercepted external-core path must not inherit the previous session value.
 */
#define XGO_RUN_PHASE_COUNTER (*(volatile u32 *)0x80c2e964u)

static char g_rom_path[MAX_ROM_PATH];

static int state_stub(const char *path)
{
    (void)path;
    return 1;
}

static int append_string(char *dst, size_t cap, size_t *used, const char *src)
{
    size_t p = *used;
    while (src && *src) {
        if (p + 1 >= cap)
            return 0;
        dst[p++] = *src++;
    }
    dst[p] = '\0';
    *used = p;
    return 1;
}

/*
 * Accept the same basic Multicore stub convention as the stock GBA hook:
 *
 *     .../fceumm;Actual Game.nes.gba
 *
 * and reconstruct:
 *
 *     /mnt/sda1/ROMS/fceumm/Actual Game.nes
 *
 * The final synthetic .gba suffix is removed. The string before ';' is
 * deliberately required to end in /fceumm so an arbitrary semicolon-tagged
 * GBA filename cannot accidentally launch this core.
 */
static int build_real_rom_path(const char *stub)
{
    const char *semi = NULL;
    const char *p;
    const char *component;
    const char *name;
    const char *end;
    size_t used = 0;
    size_t name_len;
    static const char suffix[] = ".gba";
    unsigned i;

    if (!stub)
        return 0;

    component = stub;
    for (p = stub; *p; ++p) {
        if (*p == '/')
            component = p + 1;
        else if (*p == ';') {
            semi = p;
            break;
        }
    }

    if (!semi || semi == component)
        return 0;

    /* Component before ';' must be exactly "fceumm". */
    p = component;
    for (i = 0; CORE_NAME[i]; ++i) {
        if (p + i >= semi || p[i] != CORE_NAME[i])
            return 0;
    }
    if (p + i != semi)
        return 0;

    name = semi + 1;
    end = name;
    while (*end)
        ++end;
    name_len = (size_t)(end - name);
    if (name_len <= 4)
        return 0;

    /* Require and remove the final synthetic .gba suffix. */
    for (i = 0; i < 4; ++i) {
        if (name[name_len - 4 + i] != suffix[i])
            return 0;
    }
    name_len -= 4;

    g_rom_path[0] = '\0';
    if (!append_string(g_rom_path, sizeof(g_rom_path), &used, ROM_PREFIX) ||
        !append_string(g_rom_path, sizeof(g_rom_path), &used, CORE_NAME) ||
        !append_string(g_rom_path, sizeof(g_rom_path), &used, "/"))
        return 0;

    if (used + name_len + 1 > sizeof(g_rom_path))
        return 0;
    for (i = 0; i < name_len; ++i)
        g_rom_path[used + i] = name[i];
    used += name_len;
    g_rom_path[used] = '\0';
    return 1;
}

void __start(const char *stub_path, int load_state)
{
    u32 old_family;
    u32 old_run_phase;
    struct retro_game_info old_game_info;
    int (*old_state_save)(const char *);
    int (*old_state_load)(const char *);
    unsigned (*old_get_region)(void);
    void (*old_get_av)(struct retro_system_av_info *);
    bool (*old_load_game)(const struct retro_game_info *);
    void (*old_unload_game)(void);
    void (*old_run)(void);
    void (*old_frameskip)(int);

    if (!build_real_rom_path(stub_path))
        return;

    old_family = XGO_ACTIVE_SYSTEM_FAMILY;
    old_run_phase = XGO_RUN_PHASE_COUNTER;
    old_game_info = g_retro_game_info;
    old_state_save = gfn_state_save;
    old_state_load = gfn_state_load;
    old_get_region = gfn_retro_get_region;
    old_get_av = gfn_get_system_av_info;
    old_load_game = gfn_retro_load_game;
    old_unload_game = gfn_retro_unload_game;
    old_run = gfn_retro_run;
    old_frameskip = gfn_frameskip;

    /* Preserve unrelated high bits while selecting stock NES frontend policy. */
    XGO_ACTIVE_SYSTEM_FAMILY =
        (old_family & ~FAMILY_MASK) | NES_FAMILY;

    /* Exact per-session reset performed by every stock emulator wrapper. */
    XGO_RUN_PHASE_COUNTER = 0;

    retro_set_video_refresh(retro_video_refresh_cb);
    retro_set_audio_sample_batch(retro_audio_sample_batch_cb);
    retro_set_input_poll(retro_input_poll_cb);
    retro_set_input_state(retro_input_state_cb);
    retro_set_environment(xgo_minimal_environment);
    retro_init();

    /*
     * Pinned FCEUmm asks GET_GAME_INFO_EXT first. The minimal XGO environment
     * returns false, so FCEUmm consumes info->path and leaves content_data NULL.
     * Do not reuse the GBA preload buffer here.
     */
    g_retro_game_info.path = g_rom_path;
    g_retro_game_info.data = NULL;
    g_retro_game_info.size = 0;
    g_retro_game_info.meta = NULL;

    gfn_state_save = state_stub;
    gfn_state_load = state_stub;
    gfn_retro_get_region = retro_get_region;
    gfn_get_system_av_info = retro_get_system_av_info;
    gfn_retro_load_game = retro_load_game;
    gfn_retro_unload_game = retro_unload_game;
    gfn_retro_run = retro_run;

    /*
     * run_emulator() conditionally calls this stock core-specific hook. Since
     * the intercepted run_gba() never got a chance to install its own pointer,
     * leaving the slot untouched would make behavior depend on the previously
     * launched emulator. FCEUmm needs no OEM frameskip callback here.
     */
    gfn_frameskip = NULL;

    run_emulator(load_state);
    retro_deinit();

    /* Leave the stock frontend exactly as we found it. */
    gfn_frameskip = old_frameskip;
    gfn_retro_run = old_run;
    gfn_retro_unload_game = old_unload_game;
    gfn_retro_load_game = old_load_game;
    gfn_get_system_av_info = old_get_av;
    gfn_retro_get_region = old_get_region;
    gfn_state_load = old_state_load;
    gfn_state_save = old_state_save;
    g_retro_game_info = old_game_info;
    XGO_RUN_PHASE_COUNTER = old_run_phase;
    XGO_ACTIVE_SYSTEM_FAMILY = old_family;
}
