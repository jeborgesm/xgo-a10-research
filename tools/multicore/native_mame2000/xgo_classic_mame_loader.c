/*
 * XGO Classic Arcade external MAME2000 loader.
 *
 * Patch site: stock arcade runtime JAL at 0x80360df8.
 * Only active list ID 11 is redirected. Lists 7..10 remain stock FBA.
 */
typedef unsigned int u32;
typedef unsigned long size_t;
typedef struct FILE_ FILE;

#define CORE_BASE        0x87000000u
#define CORE_LIMIT       0x87cdae00u
#define XGOC_MAGIC       0x434f4758u
#define XGOC_VERSION     1u
#define XGOC_HEADER_SIZE 32u
#define XGO_LIST_CLASSIC 11u

typedef struct {
    u32 magic, version_header, load_addr, entry_offset;
    u32 payload_size, memory_size, payload_crc32, header_crc32;
} xgoc_header;

static FILE *(*const fw_fopen)(const char *, const char *) = (void *)0x802b3524;
static size_t (*const fw_fread)(void *, size_t, size_t, FILE *) = (void *)0x802b3698;
static int (*const fw_fclose)(FILE *) = (void *)0x802b2f40;
static size_t (*const fw_fwrite)(const void *, size_t, size_t, FILE *) = (void *)0x802b42ac;
static int (*const dly_tsk)(unsigned) = (void *)0x8030f480;
static void (*const stock_run_fba)(const char *, int) = (void *)0x80360848;
static void (*const os_disable_interrupt)(void) = (void *)0x802e0750;
static void (*const os_enable_interrupt)(void) = (void *)0x802e0778;

static volatile u32 *const RAMSIZE = (void *)0x80c2ce6c;
static volatile u32 *const HEAP_BREAK = (void *)0x80c337b0;
static volatile u32 *const SND_TASK_FLAGS = (void *)0x80c2e80c;
static volatile unsigned char *const ACTIVE_LIST_ID = (void *)0x80c33980u;

static const char trace_path[]="/mnt/sda1/MAME17-L.txt";

static void trace_stage(unsigned stage)
{
    FILE *f;
    char code;
    if(stage==3u) code='C';
    else if(stage==4u) code='D';
    else if(stage==10u) code='J';
    else return;
    f=fw_fopen(trace_path,"wb");
    if(!f) return;
    fw_fwrite(&code,1,1,f);
    fw_fclose(f);
}

static u32 crc32_ieee(const unsigned char *p, u32 n)
{
    u32 crc=0xffffffffu,i,j;
    for(i=0;i<n;++i){
        crc^=p[i];
        for(j=0;j<8;++j)
            crc=(crc>>1)^(0xedb88320u&(0u-(crc&1u)));
    }
    return ~crc;
}
static void zero_range(unsigned char *p,u32 n){while(n--)*p++=0;}
static void stop_stock_sound_task(void)
{
    *SND_TASK_FLAGS &= 0xfffeu;
    while(*SND_TASK_FLAGS!=0) dly_tsk(1);
}
static void full_cache_flush(void)
{
    u32 p;
    for(p=0x80000000u;p<=0x80004000u;p+=16u)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)"::"r"(p));
    __asm__ volatile("sync; nop; nop");
    for(p=0x80000000u;p<=0x80004000u;p+=16u)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)"::"r"(p));
    __asm__ volatile("nop; nop; nop; nop; nop");
}
static void repair_irq_gp(void)
{
    volatile u32 *src=(volatile u32 *)0x80001270u;
    volatile u32 *dst=(volatile u32 *)0x80049744u;
    u32 p;
    os_disable_interrupt();
    dst[0]=src[0]; dst[1]=src[1];
    for(p=0x80049740u;p<0x80049750u;p+=16u)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)"::"r"(p));
    __asm__ volatile("sync; nop; nop");
    for(p=0x80049740u;p<0x80049750u;p+=16u)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)"::"r"(p));
    __asm__ volatile("nop; nop; nop; nop; nop");
    os_enable_interrupt();
}

void load_and_run_classic_mame(const char *filename,int load_state)
{
    FILE *f=0;
    xgoc_header h;
    u32 old_limit,end_addr,entry_addr;
    int (*entry)(const char *,int);

    if(*ACTIVE_LIST_ID!=XGO_LIST_CLASSIC){
        stock_run_fba(filename,load_state);
        return;
    }
    if(*HEAP_BREAK>=CORE_BASE){
        stock_run_fba(filename,load_state);
        return;
    }

    f=fw_fopen("/mnt/sda1/cores/mame2000/core.xgc","rb");
    if(!f) goto stock_undisturbed;
    if(fw_fread(&h,1,sizeof(h),f)!=sizeof(h)) goto close_undisturbed;
    if(h.magic!=XGOC_MAGIC ||
       (h.version_header&0xffffu)!=XGOC_VERSION ||
       (h.version_header>>16)!=XGOC_HEADER_SIZE ||
       crc32_ieee((const unsigned char *)&h,28)!=h.header_crc32 ||
       h.load_addr!=CORE_BASE || h.payload_size==0 ||
       h.memory_size<h.payload_size || h.entry_offset>=h.payload_size ||
       h.memory_size>(CORE_LIMIT-CORE_BASE))
        goto close_undisturbed;

    end_addr=CORE_BASE+h.memory_size;
    entry_addr=CORE_BASE+h.entry_offset;
    if(end_addr<CORE_BASE || entry_addr<CORE_BASE || entry_addr>=end_addr)
        goto close_undisturbed;

    trace_stage(3);
    stop_stock_sound_task();
    trace_stage(4);
    if(*HEAP_BREAK>=CORE_BASE) goto close_sound_stopped;
    old_limit=*RAMSIZE;
    *RAMSIZE=CORE_BASE;

    if(fw_fread((void *)CORE_BASE,1,h.payload_size,f)!=h.payload_size)
        goto close_restore;
    fw_fclose(f); f=0;

    if(crc32_ieee((const unsigned char *)CORE_BASE,h.payload_size)!=h.payload_crc32)
        goto restore;
    zero_range((unsigned char *)(CORE_BASE+h.payload_size),h.memory_size-h.payload_size);
    repair_irq_gp();
    full_cache_flush();

    entry=(void *)entry_addr;

    /*
     * The fifth Arcade page is a newly activated frontend section.  Its
     * presentation/resource tables are intentionally incomplete.  The old
     * hardware-proven MAME2000 frontend ultimately calls the lower-level stock
     * run_emulator() path, where the active list ID can still select per-list
     * runtime policy.  Give that lower-level runtime a known-good Arcade
     * identity (CPS1/list 7) while the external core owns emulation, then
     * restore list 11 before returning to the frontend.
     */
    *ACTIVE_LIST_ID=7u;
    trace_stage(10);
    entry(filename,load_state);
    *ACTIVE_LIST_ID=XGO_LIST_CLASSIC;

    *RAMSIZE=old_limit;
    return;

close_restore:
    fw_fclose(f);
restore:
    *RAMSIZE=old_limit;
    stock_run_fba(filename,load_state);
    return;
close_sound_stopped:
    fw_fclose(f);
    stock_run_fba(filename,load_state);
    return;
close_undisturbed:
    fw_fclose(f);
stock_undisturbed:
    stock_run_fba(filename,load_state);
}
