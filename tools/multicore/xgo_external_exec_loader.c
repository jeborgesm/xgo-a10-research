/*
 * XGO external-code execution probe loader.
 *
 * This is a controlled step beyond xgo_smoke_loader.c. It tests the exact
 * high-RAM execution mechanism used by SF2000 Multicore without loading a
 * libretro emulator core yet.
 *
 * For normal GBA filenames, behavior is unchanged: execution forwards to the
 * stock XGO run_gba().
 *
 * For /mnt/sda1/ROMS/XGO_EXEC_PROBE.gba, the loader:
 *   1. verifies the live stock heap break is below 0x87000000;
 *   2. opens /mnt/sda1/XGO_PROBE.BIN;
 *   3. temporarily lowers the stock heap ceiling to 0x87000000;
 *   4. reads up to 512 bytes into 0x87000000;
 *   5. flushes instruction/data caches;
 *   6. executes the loaded function at 0x87000000;
 *   7. restores the original heap ceiling;
 *   8. writes XGO_EXEC.OK only if the function returns 0x58474f21 ('XGO!').
 *
 * This code intentionally does not touch SPI NOR or Firmware.upk.
 */

typedef unsigned int size_t;
typedef struct FILE FILE;

typedef FILE *(*fopen_fn)(const char *, const char *);
typedef size_t (*fread_fn)(void *, size_t, size_t, FILE *);
typedef size_t (*fwrite_fn)(const void *, size_t, size_t, FILE *);
typedef int (*fclose_fn)(FILE *);
typedef void (*run_gba_fn)(const char *, int);
typedef unsigned (*probe_fn)(void);

#define FW_FOPEN   ((fopen_fn)0x802b3524u)
#define FW_FREAD   ((fread_fn)0x802b3698u)
#define FW_FWRITE  ((fwrite_fn)0x802b42acu)
#define FW_FCLOSE  ((fclose_fn)0x802b2f40u)
#define FW_RUN_GBA ((run_gba_fn)0x80360110u)

#define HEAP_BREAK (*(volatile unsigned *)0x80c337b0u)
#define RAMSIZE    (*(volatile unsigned *)0x80c2ce6cu)
#define CORE_ADDR  ((void *)0x87000000u)

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

static void write_marker(const char *path, const char *msg, unsigned len)
{
    FILE *f = FW_FOPEN(path, "wb");
    if (f) {
        FW_FWRITE(msg, 1, len, f);
        FW_FCLOSE(f);
    }
}

__attribute__((section(".entry"), used))
void xgo_loader_entry(const char *filename, int load_state)
{
    static const char probe[] = "/mnt/sda1/ROMS/XGO_EXEC_PROBE.gba";
    static const char ok[] = "External code executed at 0x87000000.\n";
    static const char heap_bad[] =
        "Heap already entered external-core window.\n";
    static const char load_bad[] =
        "Could not load external probe module.\n";

    FILE *f;
    unsigned old_limit;
    unsigned bytes_read;
    unsigned result;

    if (!string_equal(filename, probe)) {
        FW_RUN_GBA(filename, load_state);
        return;
    }

    if (HEAP_BREAK >= 0x87000000u) {
        write_marker("/mnt/sda1/XGO_EXEC_FAIL.TXT",
                     heap_bad, sizeof(heap_bad) - 1);
        return;
    }

    f = FW_FOPEN("/mnt/sda1/XGO_PROBE.BIN", "rb");
    if (!f) {
        write_marker("/mnt/sda1/XGO_EXEC_FAIL.TXT",
                     load_bad, sizeof(load_bad) - 1);
        return;
    }

    old_limit = RAMSIZE;
    RAMSIZE = 0x87000000u;

    bytes_read = FW_FREAD(CORE_ADDR, 1, 512, f);
    FW_FCLOSE(f);

    if (bytes_read == 0) {
        RAMSIZE = old_limit;
        write_marker("/mnt/sda1/XGO_EXEC_FAIL.TXT",
                     load_bad, sizeof(load_bad) - 1);
        return;
    }

    flush_all_caches();
    result = ((probe_fn)0x87000000u)();

    RAMSIZE = old_limit;

    if (result == 0x58474f21u)
        write_marker("/mnt/sda1/XGO_EXEC.OK", ok, sizeof(ok) - 1);
    else
        write_marker("/mnt/sda1/XGO_EXEC_FAIL.TXT",
                     load_bad, sizeof(load_bad) - 1);
}
