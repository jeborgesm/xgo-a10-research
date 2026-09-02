/*
 * Minimal XGO external-payload loader research prototype.
 *
 * This is intentionally smaller than SF2000 Multicore. It exists to validate
 * the already-mapped XGO loader window and stock callback addresses before a
 * full Multicore port is attempted.
 *
 * No Firmware.upk / SPI-NOR operation is involved.
 */

typedef unsigned int u32;
typedef unsigned long size_t;
typedef struct FILE_ FILE;

static FILE *(*const fw_fopen)(const char *, const char *) = (void *)0x802b3524;
static size_t (*const fw_fread)(void *, size_t, size_t, FILE *) = (void *)0x802b3698;
static int (*const fw_fclose)(FILE *) = (void *)0x802b2f40;
static void (*const stock_run_gba)(const char *, int) = (void *)0x80360110;
static volatile u32 *const RAMSIZE = (void *)0x80c2ce6c;

#define CORE_BASE   0x87000000u
#define PROBE_LIMIT 0x00100000u

static int has_semicolon(const char *s)
{
    while (*s) {
        if (*s++ == ';')
            return 1;
    }
    return 0;
}

/*
 * Make bytes written by fread visible to instruction fetch before jumping to
 * CORE_BASE.  The original prototype accidentally operated on 0x80000000..
 * 0x80004000, which does not cover the external payload at 0x87000000.
 *
 * Keep this deliberately bounded to the same 1 MiB research window used by
 * the probe fread.  A production Multicore loader should use the actual image
 * span (and explicitly account for BSS) rather than inheriting this limit.
 */
static void cache_sync_core_window(void)
{
    u32 p;

    for (p = CORE_BASE; p < CORE_BASE + PROBE_LIMIT; p += 16)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)" : : "r"(p));

    __asm__ volatile("sync; nop; nop");

    for (p = CORE_BASE; p < CORE_BASE + PROBE_LIMIT; p += 16)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)" : : "r"(p));

    __asm__ volatile("sync; nop; nop");
}

void load_and_run_core(const char *path, int load_state)
{
    FILE *f;
    u32 old_limit;
    void (*entry)(void) = (void *)CORE_BASE;

    /* Preserve normal stock GBA behavior unless this is an explicit probe stub. */
    if (!has_semicolon(path)) {
        stock_run_gba(path, load_state);
        return;
    }

    /*
     * Reserve the external-core window BEFORE opening/reading the payload.
     * Otherwise an allocation made by the stock stdio path could theoretically
     * enter 0x87000000+ while that same range is being used as executable RAM.
     */
    old_limit = *RAMSIZE;
    *RAMSIZE = CORE_BASE;

    f = fw_fopen("/mnt/sda1/cores/xgoprobe/core_87000000", "rb");
    if (!f) {
        *RAMSIZE = old_limit;
        return;
    }

    /* Probe payload is deliberately bounded to 1 MiB. */
    fw_fread((void *)CORE_BASE, 1, PROBE_LIMIT, f);
    fw_fclose(f);

    cache_sync_core_window();
    entry();

    *RAMSIZE = old_limit;
}
