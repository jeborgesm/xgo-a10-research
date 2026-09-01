/*
 * Synthetic libretro-style diagnostic core for XGO Multicore bring-up.
 *
 * This is not an emulator. It exists to prove that an external core loaded at
 * 0x87000000 can be driven by the stock XGO libretro frontend callbacks.
 *
 * Frame output:
 *   blue  = neither Player 1 nor Player 2 A is pressed
 *   red   = Player 1 A
 *   green = Player 2 A
 *   white = both Player 1 and Player 2 A
 *
 * The framebuffer is intentionally placed at fixed address 0x87100000 inside
 * the reserved external-core window so the core needs no stock allocator.
 */

typedef unsigned int size_t;
typedef int bool;
#define true 1
#define false 0

typedef bool (*retro_environment_t)(unsigned, void *);
typedef void (*retro_video_refresh_t)(const void *, unsigned, unsigned, size_t);
typedef void (*retro_audio_sample_t)(short, short);
typedef size_t (*retro_audio_sample_batch_t)(const short *, size_t);
typedef void (*retro_input_poll_t)(void);
typedef short (*retro_input_state_t)(unsigned, unsigned, unsigned, unsigned);

struct retro_system_info {
    const char *library_name;
    const char *library_version;
    const char *valid_extensions;
    bool need_fullpath;
    bool block_extract;
};

struct retro_game_geometry {
    unsigned base_width;
    unsigned base_height;
    unsigned max_width;
    unsigned max_height;
    float aspect_ratio;
};

struct retro_system_timing {
    double fps;
    double sample_rate;
};

struct retro_system_av_info {
    struct retro_game_geometry geometry;
    struct retro_system_timing timing;
};

struct retro_game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};

struct retro_core_t {
    void (*retro_init)(void);
    void (*retro_deinit)(void);
    unsigned (*retro_api_version)(void);
    void (*retro_get_system_info)(struct retro_system_info *);
    void (*retro_get_system_av_info)(struct retro_system_av_info *);
    void (*retro_set_environment)(retro_environment_t);
    void (*retro_set_video_refresh)(retro_video_refresh_t);
    void (*retro_set_audio_sample)(retro_audio_sample_t);
    void (*retro_set_audio_sample_batch)(retro_audio_sample_batch_t);
    void (*retro_set_input_poll)(retro_input_poll_t);
    void (*retro_set_input_state)(retro_input_state_t);
    void (*retro_set_controller_port_device)(unsigned, unsigned);
    void (*retro_reset)(void);
    void (*retro_run)(void);
    size_t (*retro_serialize_size)(void);
    bool (*retro_serialize)(void *, size_t);
    bool (*retro_unserialize)(const void *, size_t);
    void (*retro_cheat_reset)(void);
    void (*retro_cheat_set)(unsigned, bool, const char *);
    bool (*retro_load_game)(const struct retro_game_info *);
    bool (*retro_load_game_special)(unsigned, const struct retro_game_info *, size_t);
    void (*retro_unload_game)(void);
    unsigned (*retro_get_region)(void);
    void *(*retro_get_memory_data)(unsigned);
    size_t (*retro_get_memory_size)(unsigned);
};

static retro_video_refresh_t video_cb;
static retro_input_poll_t poll_cb;
static retro_input_state_t input_cb;

#define FB ((volatile unsigned short *)0x87100000u)

static void core_init(void)
{
    video_cb = 0;
    poll_cb = 0;
    input_cb = 0;
}

static void core_deinit(void) {}
static unsigned core_api_version(void) { return 1; }

static void core_get_system_info(struct retro_system_info *info)
{
    info->library_name = "XGO Probe";
    info->library_version = "0.1";
    info->valid_extensions = "gba";
    info->need_fullpath = false;
    info->block_extract = false;
}

static void core_get_system_av_info(struct retro_system_av_info *info)
{
    info->geometry.base_width = 320;
    info->geometry.base_height = 240;
    info->geometry.max_width = 320;
    info->geometry.max_height = 240;
    info->geometry.aspect_ratio = 1.333333333f;
    info->timing.fps = 60.0;
    info->timing.sample_rate = 22050.0;
}

static void core_set_environment(retro_environment_t cb) { (void)cb; }
static void core_set_video(retro_video_refresh_t cb) { video_cb = cb; }
static void core_set_audio_sample(retro_audio_sample_t cb) { (void)cb; }
static void core_set_audio_batch(retro_audio_sample_batch_t cb) { (void)cb; }
static void core_set_poll(retro_input_poll_t cb) { poll_cb = cb; }
static void core_set_input(retro_input_state_t cb) { input_cb = cb; }
static void core_set_port(unsigned port, unsigned device)
{
    (void)port;
    (void)device;
}

static void core_reset(void) {}

static void core_run(void)
{
    unsigned short color = 0x001f; /* blue */
    unsigned i;

    if (poll_cb)
        poll_cb();

    if (input_cb) {
        /* RETRO_DEVICE_JOYPAD=1, RETRO_DEVICE_ID_JOYPAD_A=8 */
        int p1 = input_cb(0, 1, 0, 8) != 0;
        int p2 = input_cb(1, 1, 0, 8) != 0;

        if (p1)
            color = p2 ? 0xffff : 0xf800; /* white : red */
        else if (p2)
            color = 0x07e0;              /* green */
    }

    for (i = 0; i < 320u * 240u; i++)
        FB[i] = color;

    if (video_cb)
        video_cb((const void *)FB, 320, 240, 640);
}

static size_t core_serialize_size(void) { return 0; }
static bool core_serialize(void *data, size_t size)
{
    (void)data;
    (void)size;
    return false;
}
static bool core_unserialize(const void *data, size_t size)
{
    (void)data;
    (void)size;
    return false;
}
static void core_cheat_reset(void) {}
static void core_cheat_set(unsigned i, bool enabled, const char *code)
{
    (void)i;
    (void)enabled;
    (void)code;
}
static bool core_load_game(const struct retro_game_info *info)
{
    (void)info;
    return true;
}
static bool core_load_special(unsigned type,
                              const struct retro_game_info *info,
                              size_t count)
{
    (void)type;
    (void)info;
    (void)count;
    return false;
}
static void core_unload(void) {}
static unsigned core_region(void) { return 0; }
static void *core_memory_data(unsigned id) { (void)id; return 0; }
static size_t core_memory_size(unsigned id) { (void)id; return 0; }

static struct retro_core_t api = {
    core_init,
    core_deinit,
    core_api_version,
    core_get_system_info,
    core_get_system_av_info,
    core_set_environment,
    core_set_video,
    core_set_audio_sample,
    core_set_audio_batch,
    core_set_poll,
    core_set_input,
    core_set_port,
    core_reset,
    core_run,
    core_serialize_size,
    core_serialize,
    core_unserialize,
    core_cheat_reset,
    core_cheat_set,
    core_load_game,
    core_load_special,
    core_unload,
    core_region,
    core_memory_data,
    core_memory_size
};

__attribute__((section(".entry"), used))
struct retro_core_t *xgo_probe_core_entry(void)
{
    core_init();
    return &api;
}
