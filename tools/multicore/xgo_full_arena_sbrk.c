/*
 * XGO external-core newlib heap for GBA-stub / self-loading launch paths.
 *
 * In the GBA branch, stock run_game() does not preload content into gp_buf_64m
 * before calling run_gba(). A Multicore-style fake-GBA hook therefore owns the
 * complete 64 MiB scratch arena for its private newlib heap and loads the real
 * ROM later through the external core's load-game wrapper.
 *
 * Do NOT use this allocator for native NES/Sega/SNES/GB interception: those
 * branches preload the selected ROM into gp_buf_64m before their runner call.
 */

typedef int ptrdiff_t;
typedef unsigned int uintptr_t;

extern void *gp_buf_64m;
extern int g_errno;

#define ARENA_SIZE 0x04000000u
#define ENOMEM_VALUE 12

static unsigned char *heap_floor;
static unsigned char *heap_ptr;
static unsigned char *heap_end;

static int heap_init(void)
{
    uintptr_t base = (uintptr_t)gp_buf_64m;

    if (!base) {
        g_errno = ENOMEM_VALUE;
        return 0;
    }

    heap_floor = (unsigned char *)base;
    heap_ptr = heap_floor;
    heap_end = heap_floor + ARENA_SIZE;
    return 1;
}

void *sbrk(ptrdiff_t incr)
{
    unsigned char *old_ptr;
    unsigned char *new_ptr;

    if (!heap_ptr && !heap_init())
        return (void *)-1;

    old_ptr = heap_ptr;

    if (incr >= 0) {
        unsigned inc = (unsigned)incr;
        if (inc > (unsigned)(heap_end - heap_ptr)) {
            g_errno = ENOMEM_VALUE;
            return (void *)-1;
        }
        new_ptr = heap_ptr + inc;
    } else {
        unsigned dec = (unsigned)(-(incr + 1)) + 1u;
        if (dec > (unsigned)(heap_ptr - heap_floor)) {
            g_errno = ENOMEM_VALUE;
            return (void *)-1;
        }
        new_ptr = heap_ptr - dec;
    }

    heap_ptr = new_ptr;
    return old_ptr;
}
