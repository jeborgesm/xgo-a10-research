/*
 * XGO native-NES external-core loader prototype.
 *
 * Intended hook site: run_game() NES dispatch at 0x80360e20.
 * At that point XGO has already loaded/decompressed the selected NES content
 * into gp_buf_64m and populated g_run_file_size.
 *
 * Safety/fallback behavior:
 *   - If the external core cannot be opened or validated, call the stock NES
 *     runner at 0x8035f63c with the original arguments.
 *   - Lower the stock allocator ceiling to 0x87000000 only while the external
 *     core is resident.
 *   - Load no more than 12 MiB at 0x87000000.
 *   - Verify the complete core file was read before executing it.
 *   - Restore RAMSIZE after the external core returns.
 *
 * This loader does not touch SPI NOR or Firmware.upk.
 */

typedef unsigned int size_t;
typedef struct FILE FILE;

typedef FILE *(*fopen_fn)(const char *, const char *);
typedef size_t (*fread_fn)(void *, size_t, size_t, FILE *);
typedef int (*fclose_fn)(FILE *);
typedef int (*fseeko_fn)(FILE *, int, int);
typedef int (*ftell_fn)(FILE *);
typedef void (*stock_nes_fn)(const char *, int);
typedef int (*core_entry_fn)(const char *, int);

#define FW_FOPEN      ((fopen_fn)0x802b3524u)
#define FW_FREAD      ((fread_fn)0x802b3698u)
#define FW_FCLOSE     ((fclose_fn)0x802b2f40u)
#define FW_FSEEKO     ((fseeko_fn)0x802b3804u)
#define FW_FTELL      ((ftell_fn)0x802b3f1cu)
#define FW_STOCK_NES  ((stock_nes_fn)0x8035f63cu)

#define HEAP_BREAK (*(volatile unsigned *)0x80c337b0u)
#define RAMSIZE    (*(volatile unsigned *)0x80c2ce6cu)
#define CORE_ADDR  ((void *)0x87000000u)
#define CORE_MAX_FILE_SIZE 0x00c00000u

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

static void stock_fallback(const char *filename, int load_state)
{
    FW_STOCK_NES(filename, load_state);
}

__attribute__((section(".entry"), used))
void xgo_loader_entry(const char *filename, int load_state)
{
    static const char core_path[] = "/mnt/sda1/cores/FCEUmm.xgo";
    FILE *f;
    int core_size;
    size_t bytes_read;
    unsigned old_limit;

    if (HEAP_BREAK >= 0x87000000u) {
        stock_fallback(filename, load_state);
        return;
    }

    f = FW_FOPEN(core_path, "rb");
    if (!f) {
        stock_fallback(filename, load_state);
        return;
    }

    if (FW_FSEEKO(f, 0, 2) != 0) {
        FW_FCLOSE(f);
        stock_fallback(filename, load_state);
        return;
    }

    core_size = FW_FTELL(f);
    if (core_size <= 0 || (unsigned)core_size > CORE_MAX_FILE_SIZE ||
        FW_FSEEKO(f, 0, 0) != 0) {
        FW_FCLOSE(f);
        stock_fallback(filename, load_state);
        return;
    }

    old_limit = RAMSIZE;
    RAMSIZE = 0x87000000u;

    bytes_read = FW_FREAD(CORE_ADDR, 1, (size_t)core_size, f);
    FW_FCLOSE(f);

    if (bytes_read != (size_t)core_size) {
        RAMSIZE = old_limit;
        stock_fallback(filename, load_state);
        return;
    }

    flush_all_caches();
    ((core_entry_fn)0x87000000u)(filename, load_state);

    RAMSIZE = old_limit;
}
