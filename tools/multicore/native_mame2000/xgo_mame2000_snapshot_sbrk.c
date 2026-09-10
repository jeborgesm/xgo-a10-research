/*
 * XGO MAME2000 sbrk with LAZY save-state scratch reservation.
 *
 * Launch compatibility rule:
 *   behave exactly like the hardware-proven xgo_preloaded_rom_sbrk.c until
 *   Save/Load actually requests snapshot buffers.
 *
 * Only then reserve the unused top of gp_buf_64m. If the live MAME heap has
 * already grown into that space, state acquisition fails without changing the
 * heap limit or disturbing the running game.
 */
typedef int ptrdiff_t;
typedef unsigned int uintptr_t;
typedef unsigned long size_t;

extern void *gp_buf_64m;
extern unsigned g_run_file_size;
extern int g_errno;

#define ARENA_SIZE 0x04000000u
#define CORE_BASE  0x87000000u
#define ENOMEM_VALUE 12

#define STATE_RAW_CAP  0x00c00000u
#define STATE_COMP_CAP 0x00c20000u
#define STATE_SCRATCH_TOTAL (STATE_RAW_CAP + STATE_COMP_CAP)
#define STATE_ALIGNMENT 64u

static uintptr_t state_raw_base;
static uintptr_t state_comp_base;
static int state_reserved;

static uintptr_t heap_floor;
static uintptr_t heap_ptr;
static uintptr_t heap_end;
static uintptr_t arena_limit;

static int heap_init(void)
{
    uintptr_t base=(uintptr_t)gp_buf_64m;
    uintptr_t arena_end;
    unsigned reserve;

    if(!base || base>=CORE_BASE || g_run_file_size>ARENA_SIZE-63u){
        heap_floor=heap_ptr=heap_end=arena_limit=0;
        g_errno=ENOMEM_VALUE;
        return 0;
    }
    reserve=(g_run_file_size+63u)&~63u;
    if(base>0xffffffffu-ARENA_SIZE){
        heap_floor=heap_ptr=heap_end=arena_limit=0;
        g_errno=ENOMEM_VALUE;
        return 0;
    }

    heap_floor=base+reserve;
    arena_end=base+ARENA_SIZE;
    arena_limit=arena_end<CORE_BASE?arena_end:CORE_BASE;

    if(heap_floor>=arena_limit){
        heap_floor=heap_ptr=heap_end=arena_limit=0;
        g_errno=ENOMEM_VALUE;
        return 0;
    }

    /* Hardware-proven launch policy: full safe remainder belongs to MAME. */
    heap_end=arena_limit;
    heap_ptr=heap_floor;
    state_raw_base=state_comp_base=0;
    state_reserved=0;
    return 1;
}

static int reserve_state_scratch(void)
{
    uintptr_t end, raw;

    if(!heap_ptr && !heap_init()) return 0;
    if(state_reserved) return 1;

    end=arena_limit & ~(STATE_ALIGNMENT-1u);
    if(end<heap_floor || end-heap_floor<=STATE_SCRATCH_TOTAL)
        return 0;

    raw=end-STATE_SCRATCH_TOTAL;

    /*
     * Crucial safety gate: never move the heap ceiling below live allocations.
     * Failure leaves the original heap limit untouched.
     */
    if(heap_ptr>raw)
        return 0;

    state_raw_base=raw;
    state_comp_base=raw+STATE_RAW_CAP;
    heap_end=raw;
    state_reserved=1;
    return 1;
}

void *sbrk(ptrdiff_t incr)
{
    uintptr_t old_ptr,new_ptr;

    if(!heap_ptr && !heap_init()) return (void*)-1;
    old_ptr=heap_ptr;

    if(incr>=0){
        uintptr_t amount=(uintptr_t)incr;
        if(amount>heap_end-old_ptr){g_errno=ENOMEM_VALUE;return (void*)-1;}
        new_ptr=old_ptr+amount;
    }else{
        uintptr_t amount=(uintptr_t)(-(incr+1))+1u;
        if(amount>old_ptr-heap_floor){g_errno=ENOMEM_VALUE;return (void*)-1;}
        new_ptr=old_ptr-amount;
    }
    heap_ptr=new_ptr;
    return (void*)old_ptr;
}

uintptr_t xgo_mame_heap_floor(void){if(!heap_ptr&&!heap_init())return 0;return heap_floor;}
uintptr_t xgo_mame_heap_ptr(void){if(!heap_ptr&&!heap_init())return 0;return heap_ptr;}
uintptr_t xgo_mame_heap_limit(void){if(!heap_ptr&&!heap_init())return 0;return heap_end;}
int xgo_mame_heap_restore(uintptr_t p){
    if(!heap_ptr&&!heap_init())return 0;
    if(p<heap_floor||p>heap_end)return 0;
    heap_ptr=p;return 1;
}
void *xgo_mame_state_raw_buffer(void){
    if(!reserve_state_scratch())return 0;
    return (void*)state_raw_base;
}
void *xgo_mame_state_comp_buffer(void){
    if(!reserve_state_scratch())return 0;
    return (void*)state_comp_base;
}
size_t xgo_mame_state_raw_capacity(void){return STATE_RAW_CAP;}
size_t xgo_mame_state_comp_capacity(void){return STATE_COMP_CAP;}
