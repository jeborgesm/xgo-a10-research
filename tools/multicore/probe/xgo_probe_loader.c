/*
 * Validated XGO external-core loader research prototype.
 *
 * External payloads use the small XGOC container documented alongside this
 * prototype. The loader validates metadata and payload integrity, reserves the
 * core RAM window before file I/O, zeros BSS/runtime-only memory, synchronizes
 * caches over the loaded executable range, and only then transfers control.
 *
 * No Firmware.upk / SPI-NOR operation is involved.
 */

typedef unsigned int u32;
typedef unsigned long size_t;
typedef struct FILE_ FILE;

#define CORE_BASE        0x87000000u
#define CORE_LIMIT       0x87cdae00u
#define XGOC_MAGIC       0x434f4758u /* bytes: "XGOC" */
#define XGOC_VERSION     1u
#define XGOC_HEADER_SIZE 32u

typedef struct {
    u32 magic;
    u32 version_header; /* low 16: version, high 16: header size */
    u32 load_addr;
    u32 entry_offset;
    u32 payload_size;
    u32 memory_size;
    u32 payload_crc32;  /* standard reflected CRC-32 / IEEE */
    u32 header_crc32;   /* CRC over the first 28 header bytes */
} xgoc_header;

static FILE *(*const fw_fopen)(const char *, const char *) = (void *)0x802b3524;
static size_t (*const fw_fread)(void *, size_t, size_t, FILE *) = (void *)0x802b3698;
static int (*const fw_fclose)(FILE *) = (void *)0x802b2f40;
static void (*const stock_run_gba)(const char *, int) = (void *)0x80360110;
static volatile u32 *const RAMSIZE = (void *)0x80c2ce6c;
static volatile u32 *const HEAP_BREAK = (void *)0x80c337b0;

static int has_semicolon(const char *s)
{
    while (*s) {
        if (*s++ == ';')
            return 1;
    }
    return 0;
}

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

static void cache_sync_range(u32 start, u32 end)
{
    u32 p;

    start &= ~15u;
    end = (end + 15u) & ~15u;

    for (p = start; p < end; p += 16)
        __asm__ volatile("cache 1,0(%0)" : : "r"(p));

    __asm__ volatile("sync; nop; nop");

    for (p = start; p < end; p += 16)
        __asm__ volatile("cache 0,0(%0)" : : "r"(p));

    __asm__ volatile("sync; nop; nop");
}

void load_and_run_core(const char *path, int load_state)
{
    FILE *f;
    xgoc_header h;
    u32 old_limit;
    u32 end_addr;
    u32 entry_addr;
    void (*entry)(const char *, int);

    if (!has_semicolon(path)) {
        stock_run_gba(path, load_state);
        return;
    }

    /* Never lower the heap ceiling beneath an allocation already in use. */
    if (*HEAP_BREAK >= CORE_BASE)
        return;

    /* Reserve external-core RAM before stock stdio can allocate anything. */
    old_limit = *RAMSIZE;
    *RAMSIZE = CORE_BASE;

    /* First production target: the pinned HC15xx-compatible FCEUmm core. */
    f = fw_fopen("/mnt/sda1/cores/fceumm/core.xgc", "rb");
    if (!f)
        goto restore_heap;

    if (fw_fread(&h, 1, sizeof(h), f) != sizeof(h))
        goto close_file;

    if (h.magic != XGOC_MAGIC ||
        (h.version_header & 0xffffu) != XGOC_VERSION ||
        (h.version_header >> 16) != XGOC_HEADER_SIZE ||
        crc32_ieee((const unsigned char *)&h, 28) != h.header_crc32 ||
        h.load_addr != CORE_BASE ||
        h.payload_size == 0 ||
        h.memory_size < h.payload_size ||
        h.entry_offset >= h.payload_size ||
        h.memory_size > (CORE_LIMIT - CORE_BASE))
        goto close_file;

    end_addr = CORE_BASE + h.memory_size;
    entry_addr = CORE_BASE + h.entry_offset;

    if (end_addr < CORE_BASE ||
        entry_addr < CORE_BASE ||
        entry_addr >= end_addr)
        goto close_file;

    if (fw_fread((void *)CORE_BASE, 1, h.payload_size, f) != h.payload_size)
        goto close_file;

    fw_fclose(f);
    f = 0;

    if (crc32_ieee((const unsigned char *)CORE_BASE, h.payload_size) !=
        h.payload_crc32)
        goto restore_heap;

    zero_range((unsigned char *)(CORE_BASE + h.payload_size),
               h.memory_size - h.payload_size);

    cache_sync_range(CORE_BASE, end_addr);

    /* Pass the original stub and stock load-state request into the core bridge. */
    entry = (void *)entry_addr;
    entry(path, load_state);

restore_heap:
    *RAMSIZE = old_limit;
    return;

close_file:
    fw_fclose(f);
    goto restore_heap;
}
