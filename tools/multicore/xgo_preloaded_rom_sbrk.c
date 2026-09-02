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

static uintptr_t heap_floor;
static uintptr_t heap_ptr;
static uintptr_t heap_end;

static int heap_init(void)
{
    uintptr_t base = (uintptr_t)gp_buf_64m;
    unsigned reserve;

    if (!base || g_run_file_size > ARENA_SIZE - 63u) {
        heap_floor = heap_ptr = heap_end = 0;
        g_errno = ENOMEM_VALUE;
        return 0;
    }

    reserve = (g_run_file_size + 63u) & ~63u;

    /* Integer arithmetic keeps overflow checks defined even on hostile input. */
    if (base > 0xffffffffu - ARENA_SIZE) {
        heap_floor = heap_ptr = heap_end = 0;
        g_errno = ENOMEM_VALUE;
        return 0;
    }

    heap_floor = base + reserve;
    heap_ptr = heap_floor;
    heap_end = base + ARENA_SIZE;
    return 1;
}

void *sbrk(ptrdiff_t incr)
{
    uintptr_t old_ptr;
    uintptr_t new_ptr;

    if (!heap_ptr && !heap_init())
        return (void *)-1;

    old_ptr = heap_ptr;

    if (incr >= 0) {
        uintptr_t amount = (uintptr_t)incr;
        if (amount > heap_end - old_ptr) {
            g_errno = ENOMEM_VALUE;
            return (void *)-1;
        }
        new_ptr = old_ptr + amount;
    } else {
        /* Avoid negating INT_MIN in signed arithmetic. */
        uintptr_t amount = (uintptr_t)(-(incr + 1)) + 1u;
        if (amount > old_ptr - heap_floor) {
            g_errno = ENOMEM_VALUE;
            return (void *)-1;
        }
        new_ptr = old_ptr - amount;
    }

    heap_ptr = new_ptr;
    return (void *)old_ptr;
}
