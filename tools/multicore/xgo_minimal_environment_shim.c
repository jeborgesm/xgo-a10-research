/*
 * Minimal XGO libretro environment compatibility shim.
 *
 * Research-stage source. This deliberately implements only low-risk generic
 * queries that do not require direct XGO board-driver manipulation.
 * Unknown commands fall back to the stock environment handler through a
 * stock-GP veneer.
 *
 * The stock XGO handler at 0x8035eb64 is intentionally NOT trusted for pixel
 * format or rotation negotiation. It returns success for pixel formats it does
 * not actually convert, and SET_ROTATION only permutes D-pad masks without
 * rotating video. Until the external frontend implements those capabilities,
 * this shim advertises only what the underlying XGO transport really supports.
 */

typedef int bool;
#define true 1
#define false 0

typedef unsigned long size_t;
typedef bool (*environment_cb)(unsigned, void *);

struct retro_variable {
    const char *key;
    const char *value;
};

/* Pinned HC15xx libretro.h layout. Keep the byte-sized booleans explicit even
 * though this freestanding shim uses int for callback bool return values. */
struct retro_game_info_ext {
    const char *full_path;
    const char *archive_path;
    const char *archive_file;
    const char *dir;
    const char *name;
    const char *ext;
    const char *meta;
    const void *data;
    size_t size;
    unsigned char file_in_archive;
    unsigned char persistent_data;
};

struct retro_game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};

/* xgo_gp_bridges.s establishes XGO_STOCK_GP around this firmware call. */
extern bool xgo_stock_environment(unsigned, void *);

#define XGO_REGION_MODE (*(volatile unsigned *)0x80c2e878u)
#define XGO_GAME_INFO (*(volatile struct retro_game_info *)0x80c2e914u)

#define RETRO_ENVIRONMENT_SET_ROTATION               1u
#define RETRO_ENVIRONMENT_GET_CAN_DUPE               3u
#define RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY       9u
#define RETRO_ENVIRONMENT_SET_PIXEL_FORMAT          10u
#define RETRO_ENVIRONMENT_GET_VARIABLE              15u
#define RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE       17u
#define RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY        31u
#define RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE 65u
#define RETRO_ENVIRONMENT_GET_GAME_INFO_EXT         66u
#define RETRO_ENVIRONMENT_EXPERIMENTAL              0x10000u
#define RETRO_ENVIRONMENT_GET_INPUT_BITMASKS        (51u | RETRO_ENVIRONMENT_EXPERIMENTAL)
#define RETRO_ENVIRONMENT_GET_TARGET_SAMPLE_RATE    (81u | RETRO_ENVIRONMENT_EXPERIMENTAL)

/* libretro enum retro_pixel_format */
#define RETRO_PIXEL_FORMAT_0RGB1555 0u
#define RETRO_PIXEL_FORMAT_XRGB8888 1u
#define RETRO_PIXEL_FORMAT_RGB565   2u

static const char xgo_system_directory[] = "/mnt/sda1/bios";
static const char xgo_save_directory[]   = "/mnt/sda1/saves";
static const char region_ntsc[] = "NTSC";
static const char region_pal[]  = "PAL";
static const char region_auto[] = "Auto";

/* Variable updates are currently static in this minimal shim. */
static bool xgo_variable_update;
static struct retro_game_info_ext xgo_game_info_ext;

static bool str_equal(const char *a, const char *b)
{
    if (!a || !b)
        return false;
    while (*a && *b) {
        if (*a++ != *b++)
            return false;
    }
    return *a == *b;
}

bool xgo_minimal_environment(unsigned cmd, void *data)
{
    switch (cmd) {
    case RETRO_ENVIRONMENT_SET_ROTATION:
        (void)data;
        return false;

    case RETRO_ENVIRONMENT_GET_CAN_DUPE:
        if (!data)
            return false;
        *(bool *)data = true;
        return true;

    case RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY:
        if (!data)
            return false;
        *(const char **)data = xgo_system_directory;
        return true;

    case RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY:
        if (!data)
            return false;
        *(const char **)data = xgo_save_directory;
        return true;

    case RETRO_ENVIRONMENT_GET_INPUT_BITMASKS:
        /* Stock input is per-button only; never advertise id=256 masks. */
        (void)data;
        return false;

    case RETRO_ENVIRONMENT_SET_CONTENT_INFO_OVERRIDE:
        /* Pinned FCEUmm requests memory-backed fds|nes|unf|unif content. */
        (void)data;
        return true;

    case RETRO_ENVIRONMENT_GET_GAME_INFO_EXT:
        if (!data || !XGO_GAME_INFO.path || !XGO_GAME_INFO.data ||
            XGO_GAME_INFO.size == 0)
            return false;

        /* Expose the already-stock-preloaded ROM. The native sbrk reserves this
         * prefix and allocates external newlib only above it. */
        xgo_game_info_ext.full_path = XGO_GAME_INFO.path;
        xgo_game_info_ext.archive_path = 0;
        xgo_game_info_ext.archive_file = 0;
        xgo_game_info_ext.dir = 0;
        xgo_game_info_ext.name = 0;
        xgo_game_info_ext.ext = 0;
        xgo_game_info_ext.meta = XGO_GAME_INFO.meta;
        xgo_game_info_ext.data = XGO_GAME_INFO.data;
        xgo_game_info_ext.size = XGO_GAME_INFO.size;
        xgo_game_info_ext.file_in_archive = 0;
        xgo_game_info_ext.persistent_data = 1;
        *(const struct retro_game_info_ext **)data = &xgo_game_info_ext;
        return true;

    case RETRO_ENVIRONMENT_GET_VARIABLE:
        if (data) {
            struct retro_variable *var = (struct retro_variable *)data;
            if (str_equal(var->key, "fceumm_region")) {
                if (XGO_REGION_MODE == 0)
                    var->value = region_ntsc;
                else if (XGO_REGION_MODE == 1)
                    var->value = region_pal;
                else
                    var->value = region_auto;
                return true;
            }
        }
        return xgo_stock_environment(cmd, data);

    case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:
        if (!data)
            return false;
        *(bool *)data = xgo_variable_update;
        xgo_variable_update = false;
        return true;

    case RETRO_ENVIRONMENT_GET_TARGET_SAMPLE_RATE:
        if (!data)
            return false;
        /* Stock scheduler budgets imply stereo 16-bit 44.1-kHz PCM. */
        *(unsigned *)data = 44100u;
        return true;

    case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT:
        if (!data)
            return false;
        return *(const unsigned *)data == RETRO_PIXEL_FORMAT_RGB565;

    default:
        /* The wrapper temporarily installs stock $gp before entering firmware. */
        return xgo_stock_environment(cmd, data);
    }
}
