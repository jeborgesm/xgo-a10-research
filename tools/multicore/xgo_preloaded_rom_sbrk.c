/*
 * XGO external-core sbrk() for native main-list interception.
 *
 * At NES/SNES/Sega/GB family dispatch time, stock run_game() has already put
 * the selected ROM at gp_buf_64m and g_run_file_size describes the loaded
 * content. Upstream SF2000 Multicore normally starts its private newlib heap
 * at gp_buf_64m, which would overwrite that preloaded content.
 *
 * This variant preserves a 64-byte-aligned prefix containing the stock-loaded
 * ROM and exposes only the remainder of the 64-MiB arena to newlib.
 */

typedef int ptrdiff_t;
typedef unsigned int uintptr_t;

extern void *gp_buf_64m;
extern unsigned g_run_file_size;
extern int g_errno;

#define ARENA_SIZE 0x04000000u
#define ENOMEM_VALUE 12

static unsigned char *heap_floor;
static unsigned char *heap_ptr;
static unsigned char *heap_end;

static void heap_init(void)
{
    uintptr_t base = (uintptr_t)gp_buf_64m;
    unsigned reserve;

    if (g_run_file_size > ARENA_SIZE - 63u) {
        heap_floor = heap_ptr = heap_end = 0;
        g_errno = ENOMEM_VALUE;
        return;
    }

    reserve = (g_run_file_size + 63u) & ~63u;
    heap_floor = (unsigned char *)(base + reserve);
    heap_ptr = heap_floor;
    heap_end = (unsigned char *)(base + ARENA_SIZE);
}

void *sbrk(ptrdiff_t incr)
{
    unsigned char *old_ptr;
    unsigned char *new_ptr;

    if (!heap_ptr)
        heap_init();
    if (!heap_ptr)
        return (void *)-1;

    old_ptr = heap_ptr;
    new_ptr = heap_ptr + incr;

    if ((incr > 0 && new_ptr < old_ptr) ||
        new_ptr < heap_floor || new_ptr > heap_end) {
        g_errno = ENOMEM_VALUE;
        return (void *)-1;
    }

    heap_ptr = new_ptr;
    return old_ptr;
}
