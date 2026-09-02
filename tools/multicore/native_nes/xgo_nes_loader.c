/*
 * Native NES external-core loader for XGO.
 *
 * Intended patch site:
 *   run_game + NES dispatch JAL at 0x80360e20
 *
 * run_game() has already preloaded the selected NES ROM into gp_buf_64m before
 * this function is called. This loader validates and installs only the external
 * core image. If anything is wrong, it restores the heap ceiling and calls the
 * untouched stock run_nes() implementation.
 */

typedef unsigned int u32;
typedef unsigned long size_t;
typedef struct FILE_ FILE;

#define CORE_BASE        0x87000000u
#define CORE_LIMIT       0x87cdae00u
#define XGOC_MAGIC       0x434f4758u /* "XGOC" */
#define XGOC_VERSION     1u
#define XGOC_HEADER_SIZE 32u

typedef struct {
    u32 magic;
    u32 version_header;
    u32 load_addr;
    u32 entry_offset;
    u32 payload_size;
    u32 memory_size;
    u32 payload_crc32;
    u32 header_crc32;
} xgoc_header;

static FILE *(*const fw_fopen)(const char *, const char *) = (void *)0x802b3524;
static size_t (*const fw_fread)(void *, size_t, size_t, FILE *) = (void *)0x802b3698;
static int (*const fw_fclose)(FILE *) = (void *)0x802b2f40;
static int (*const dly_tsk)(unsigned) = (void *)0x8030f480;
static void (*const stock_run_nes)(const char *, int) = (void *)0x8035f63c;

static volatile u32 *const RAMSIZE = (void *)0x80c2ce6c;
static volatile u32 *const HEAP_BREAK = (void *)0x80c337b0;
static volatile u32 *const SND_TASK_FLAGS = (void *)0x80c2e80c;

static u32 crc32_ieee(const unsigned char *p, u32 n)
{
    u32 crc = 0xffffffffu;
    u32 i, j;
    for (i = 0; i < n; ++i) {
        crc ^= p[i];
        for (j = 0; j < 8; ++j)
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1u)));
    }
    return ~crc;
}

static void zero_range(unsigned char *p, u32 n)
{
    while (n--)
        *p++ = 0;
}

static void stop_stock_sound_task(void)
{
    *SND_TASK_FLAGS &= 0xfffeu;
    while (*SND_TASK_FLAGS != 0)
        dly_tsk(1);
}

static void full_cache_flush(void)
{
    u32 p;
    for (p = 0x80000000u; p <= 0x80004000u; p += 16u)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)" : : "r"(p));
    __asm__ volatile("sync; nop; nop");
    for (p = 0x80000000u; p <= 0x80004000u; p += 16u)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)" : : "r"(p));
    __asm__ volatile("nop; nop; nop; nop; nop");
}

void load_and_run_core(const char *filename, int load_state)
{
    FILE *f = 0;
    xgoc_header h;
    u32 old_limit;
    u32 end_addr;
    u32 entry_addr;
    int (*entry)(const char *, int);

    /* If upper RAM is already in active stock use, do not disturb NES at all. */
    if (*HEAP_BREAK >= CORE_BASE) {
        stock_run_nes(filename, load_state);
        return;
    }

    old_limit = *RAMSIZE;
    *RAMSIZE = CORE_BASE;

    f = fw_fopen("/mnt/sda1/cores/fceumm/core.xgc", "rb");
    if (!f)
        goto stock_fallback;

    if (fw_fread(&h, 1, sizeof(h), f) != sizeof(h))
        goto close_fallback;

    if (h.magic != XGOC_MAGIC ||
        (h.version_header & 0xffffu) != XGOC_VERSION ||
        (h.version_header >> 16) != XGOC_HEADER_SIZE ||
        crc32_ieee((const unsigned char *)&h, 28) != h.header_crc32 ||
        h.load_addr != CORE_BASE ||
        h.payload_size == 0 ||
        h.memory_size < h.payload_size ||
        h.entry_offset >= h.payload_size ||
        h.memory_size > (CORE_LIMIT - CORE_BASE))
        goto close_fallback;

    end_addr = CORE_BASE + h.memory_size;
    entry_addr = CORE_BASE + h.entry_offset;
    if (end_addr < CORE_BASE || entry_addr < CORE_BASE || entry_addr >= end_addr)
        goto close_fallback;

    if (fw_fread((void *)CORE_BASE, 1, h.payload_size, f) != h.payload_size)
        goto close_fallback;

    fw_fclose(f);
    f = 0;

    if (crc32_ieee((const unsigned char *)CORE_BASE, h.payload_size) !=
        h.payload_crc32)
        goto stock_fallback;

    zero_range((unsigned char *)(CORE_BASE + h.payload_size),
               h.memory_size - h.payload_size);

    /* Match the first operation of stock run_nes(), but only after validation. */
    stop_stock_sound_task();
    full_cache_flush();

    entry = (void *)entry_addr;
    entry(filename, load_state);

    *RAMSIZE = old_limit;
    return;

close_fallback:
    fw_fclose(f);

stock_fallback:
    *RAMSIZE = old_limit;
    stock_run_nes(filename, load_state);
}
