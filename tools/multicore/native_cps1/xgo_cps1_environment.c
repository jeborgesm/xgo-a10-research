/* CPS1-local environment wrapper.
 * Keeps the proven generic XGO shim unchanged while satisfying FB Alpha 2012
 * CPS-1's assumption that a logger exists whenever directories are available.
 */
typedef int bool;
#define true 1
#define false 0

struct retro_log_callback {
    void (*log)(int level, const char *fmt, ...);
};

extern bool xgo_minimal_environment(unsigned, void *);

#define RETRO_ENVIRONMENT_GET_LOG_INTERFACE 27u

static void xgo_cps1_noop_log(int level, const char *fmt, ...)
{
    (void)level;
    (void)fmt;
}

bool xgo_cps1_environment(unsigned cmd, void *data)
{
    if (cmd == RETRO_ENVIRONMENT_GET_LOG_INTERFACE) {
        struct retro_log_callback *cb = (struct retro_log_callback *)data;
        if (!cb)
            return false;
        cb->log = xgo_cps1_noop_log;
        return true;
    }
    return xgo_minimal_environment(cmd, data);
}
