/*
 * Minimal XGO libretro environment compatibility shim.
 *
 * Research-stage source. This deliberately implements only low-risk generic
 * queries that do not require direct XGO board-driver manipulation.
 * Unknown commands fall back to the stock environment handler.
 *
 * The stock XGO handler at 0x8035eb64 is intentionally NOT trusted for pixel
 * format negotiation because it returns success without validating the
 * requested format. Until an XRGB8888 converter is installed, this shim only
 * advertises RGB565.
 */

typedef int bool;
#define true 1
#define false 0

typedef bool (*environment_cb)(unsigned, void *);

struct retro_variable {
    const char *key;
    const char *value;
};

#define STOCK_XGO_ENV ((environment_cb)0x8035eb64u)
#define XGO_REGION_MODE (*(volatile unsigned *)0x80c2e878u)

#define RETRO_ENVIRONMENT_GET_CAN_DUPE          3u
#define RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY  9u
#define RETRO_ENVIRONMENT_SET_PIXEL_FORMAT      10u
#define RETRO_ENVIRONMENT_GET_VARIABLE          15u
#define RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE   17u
#define RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY    31u
#define RETRO_ENVIRONMENT_EXPERIMENTAL           0x10000u
#define RETRO_ENVIRONMENT_GET_TARGET_SAMPLE_RATE (81u | RETRO_ENVIRONMENT_EXPERIMENTAL)

/* libretro enum retro_pixel_format */
#define RETRO_PIXEL_FORMAT_0RGB1555 0u
#define RETRO_PIXEL_FORMAT_XRGB8888 1u
#define RETRO_PIXEL_FORMAT_RGB565   2u

static const char xgo_system_directory[] = "/mnt/sda1/bios";
static const char xgo_save_directory[]   = "/mnt/sda1/saves";
static const char region_ntsc[] = "NTSC";
static const char region_pal[]  = "PAL";
static const char region_auto[] = "Auto";

/*
 * Variable updates are currently static in this minimal shim. A future PC-side
 * configuration layer can back this with generated per-core option files.
 */
static bool xgo_variable_update;

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

    case RETRO_ENVIRONMENT_GET_VARIABLE:
        if (data) {
            struct retro_variable *var = (struct retro_variable *)data;
            if (str_equal(var->key, "fceumm_region")) {
                /*
                 * Stock XGO uses {"NTSC","PAL","AUTO"}; current FCEUmm's
                 * parser expects the automatic value as case-sensitive
                 * "Auto". Preserve XGO's region state while normalizing that
                 * one legacy spelling mismatch.
                 */
                if (XGO_REGION_MODE == 0)
                    var->value = region_ntsc;
                else if (XGO_REGION_MODE == 1)
                    var->value = region_pal;
                else
                    var->value = region_auto;
                return true;
            }
        }
        return STOCK_XGO_ENV(cmd, data);

    case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:
        if (!data)
            return false;
        *(bool *)data = xgo_variable_update;
        xgo_variable_update = false;
        return true;

    case RETRO_ENVIRONMENT_GET_TARGET_SAMPLE_RATE:
        if (!data)
            return false;
        /*
         * XGO run_emulator's per-frame audio byte budgets are derived from
         * stereo 16-bit 44.1-kHz PCM (3528 B @ 50 Hz, 2940 B @ 60 Hz).
         * Advertising 44100 makes modern cores with an Auto rate policy align
         * their generated audio with that stock scheduler.
         */
        *(unsigned *)data = 44100u;
        return true;

    case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT:
        if (!data)
            return false;
        /*
         * XGO's proven stock video path is RGB565. Do not repeat the stock
         * callback's false-positive success for XRGB8888/0RGB1555.
         */
        return *(const unsigned *)data == RETRO_PIXEL_FORMAT_RGB565;

    default:
        /* Keep stock logging and rotation behavior for commands it knows. */
        return STOCK_XGO_ENV(cmd, data);
    }
}
