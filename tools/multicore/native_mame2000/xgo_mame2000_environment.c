/* MAME2000-local environment policy for XGO Core #3.
 *
 * Keep the proven generic shim unchanged. MAME2000 needs only a few frontend
 * options to match the HC15xx/XGO runtime cleanly.
 */
typedef int bool;
#define true 1
#define false 0

struct retro_variable {
    const char *key;
    const char *value;
};
struct retro_log_callback {
    void (*log)(int level, const char *fmt, ...);
};

extern bool xgo_minimal_environment(unsigned, void *);

#define RETRO_ENVIRONMENT_SET_VARIABLES               16u
#define RETRO_ENVIRONMENT_GET_VARIABLE                15u
#define RETRO_ENVIRONMENT_GET_LOG_INTERFACE           27u
#define RETRO_ENVIRONMENT_SET_GEOMETRY                37u

static const char v_frameskip[] = "disabled";
static const char v_threshold[] = "30";
static const char v_interval[] = "1";
static const char v_skip_disclaimer[] = "enabled";
static const char v_show_gameinfo[] = "disabled";
static const char v_sample_rate[] = "11025";
static const char v_stereo[] = "enabled";
static const char v_audio[] = "enabled";

static int eq(const char *a, const char *b)
{
    if (!a || !b) return 0;
    while (*a && *b) {
        if (*a++ != *b++) return 0;
    }
    return *a == *b;
}

static void xgo_mame2000_noop_log(int level, const char *fmt, ...)
{
    (void)level; (void)fmt;
}

bool xgo_mame2000_environment(unsigned cmd, void *data)
{
    if (cmd == RETRO_ENVIRONMENT_SET_VARIABLES) {
        (void)data;
        return true;
    }

    if (cmd == RETRO_ENVIRONMENT_GET_LOG_INTERFACE) {
        struct retro_log_callback *cb = (struct retro_log_callback *)data;
        if (!cb) return false;
        cb->log = xgo_mame2000_noop_log;
        return true;
    }

    if (cmd == RETRO_ENVIRONMENT_SET_GEOMETRY) {
        /* Stock XGO video callback/scaler already accepts changing RGB565
         * dimensions. Geometry notification requires no board-side mutation. */
        (void)data;
        return true;
    }

    if (cmd == RETRO_ENVIRONMENT_GET_VARIABLE && data) {
        struct retro_variable *v = (struct retro_variable *)data;
        if (eq(v->key, "mame2000-frameskip")) {
            v->value = v_frameskip; return true;
        }
        if (eq(v->key, "mame2000-frameskip_threshold")) {
            v->value = v_threshold; return true;
        }
        if (eq(v->key, "mame2000-frameskip_interval")) {
            v->value = v_interval; return true;
        }
        if (eq(v->key, "mame2000-skip_disclaimer")) {
            v->value = v_skip_disclaimer; return true;
        }
        if (eq(v->key, "mame2000-show_gameinfo")) {
            v->value = v_show_gameinfo; return true;
        }
        if (eq(v->key, "mame2000-sample_rate")) {
            v->value = v_sample_rate; return true;
        }
        if (eq(v->key, "mame2000-stereo")) {
            v->value = v_stereo; return true;
        }
        if (eq(v->key, "mame2000-audio")) {
            v->value = v_audio; return true;
        }
    }

    return xgo_minimal_environment(cmd, data);
}
