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

#define STOCK_XGO_ENV ((environment_cb)0x8035eb64u)

#define RETRO_ENVIRONMENT_GET_CAN_DUPE          3u
#define RETRO_ENVIRONMENT_GET_SYSTEM_DIRECTORY  9u
#define RETRO_ENVIRONMENT_SET_PIXEL_FORMAT      10u
#define RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE   17u
#define RETRO_ENVIRONMENT_GET_SAVE_DIRECTORY    31u

/* libretro enum retro_pixel_format */
#define RETRO_PIXEL_FORMAT_0RGB1555 0u
#define RETRO_PIXEL_FORMAT_XRGB8888 1u
#define RETRO_PIXEL_FORMAT_RGB565   2u

static const char xgo_system_directory[] = "/mnt/sda1/bios";
static const char xgo_save_directory[]   = "/mnt/sda1/saves";

/*
 * Variable updates are currently static in this minimal shim. A future PC-side
 * configuration layer can back this with generated per-core option files.
 */
static bool xgo_variable_update;

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

    case RETRO_ENVIRONMENT_GET_VARIABLE_UPDATE:
        if (!data)
            return false;
        *(bool *)data = xgo_variable_update;
        xgo_variable_update = false;
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
        /* Keep stock region-variable, logging and rotation behavior. */
        return STOCK_XGO_ENV(cmd, data);
    }
}
