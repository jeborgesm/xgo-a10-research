/*
 * Minimal XGO loader-injection smoke test.
 *
 * Purpose:
 *   - prove that a resealed SD-loaded bisrv.asd executes code injected at
 *     0x80001500;
 *   - prove the injected code can call resolved stock XGO stdio functions;
 *   - preserve normal GBA behavior for every filename except the explicit
 *     probe path below.
 *
 * The probe path is intentionally harmless: selecting
 *   /mnt/sda1/ROMS/XGO_PROBE.gba
 * creates /mnt/sda1/XGO_PROBE.OK on the SD card and returns to the caller.
 * It does not touch SPI NOR or Firmware.upk.
 *
 * Stock firmware fingerprint used while deriving these addresses:
 * SHA-256 869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf
 */

typedef unsigned int size_t;
typedef struct FILE FILE;

typedef FILE *(*fopen_fn)(const char *, const char *);
typedef size_t (*fwrite_fn)(const void *, size_t, size_t, FILE *);
typedef int (*fclose_fn)(FILE *);
typedef void (*run_gba_fn)(const char *, int);

#define FW_FOPEN   ((fopen_fn)0x802b3524u)
#define FW_FWRITE  ((fwrite_fn)0x802b42acu)
#define FW_FCLOSE  ((fclose_fn)0x802b2f40u)
#define FW_RUN_GBA ((run_gba_fn)0x80360110u)

static int is_probe(const char *s)
{
    static const char probe[] = "/mnt/sda1/ROMS/XGO_PROBE.gba";
    unsigned i = 0;

    if (!s)
        return 0;

    while (probe[i]) {
        if (s[i] != probe[i])
            return 0;
        i++;
    }

    return s[i] == 0;
}

__attribute__((section(".entry"), used))
void xgo_loader_entry(const char *filename, int load_state)
{
    if (!is_probe(filename)) {
        FW_RUN_GBA(filename, load_state);
        return;
    }

    FILE *f = FW_FOPEN("/mnt/sda1/XGO_PROBE.OK", "wb");
    if (f) {
        static const char msg[] =
            "XGO injected loader executed successfully.\n";
        FW_FWRITE(msg, 1, sizeof(msg) - 1, f);
        FW_FCLOSE(f);
    }
}
