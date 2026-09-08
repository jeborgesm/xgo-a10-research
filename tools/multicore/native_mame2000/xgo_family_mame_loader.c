/*
 * XGO Classic Arcade family-style raw-core loader.
 * Additive list-ID-11 path over golden Test08.
 */
typedef unsigned int u32;
typedef unsigned long size_t;
typedef struct FILE_ FILE;
typedef int bool;
#define true 1
#define false 0

#ifndef XGO_MAME_CORE_SIZE
#error XGO_MAME_CORE_SIZE required
#endif

#define CORE_BASE 0x87000000u
#define CORE_LIMIT 0x87cdae00u
#define LIST_CLASSIC 11u

struct retro_game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};
struct retro_system_av_info;
struct xgo_family_core_api {
    void (*bind_callbacks)(void);
    void (*init)(void);
    void (*deinit)(void);
    unsigned (*get_region)(void);
    void (*get_av)(struct retro_system_av_info*);
    bool (*load_game)(const struct retro_game_info*);
    void (*unload_game)(void);
    void (*run)(void);
};

static FILE *(*const fw_fopen)(const char*,const char*)=(void*)0x802b3524;
static size_t (*const fw_fread)(void*,size_t,size_t,FILE*)=(void*)0x802b3698;
static int (*const fw_fclose)(FILE*)=(void*)0x802b2f40;
static int (*const dly_tsk)(unsigned)=(void*)0x8030f480;
static void (*const stock_run_fba)(const char*,int)=(void*)0x80360848;
static int (*const stock_run_emulator)(int)=(void*)0x8035ed48;
static void (*const os_disable_interrupt)(void)=(void*)0x802e0750;
static void (*const os_enable_interrupt)(void)=(void*)0x802e0778;

static volatile u32 *const RAMSIZE=(void*)0x80c2ce6c;
static volatile u32 *const HEAP_BREAK=(void*)0x80c337b0;
static volatile u32 *const SND_FLAGS=(void*)0x80c2e80c;
static volatile unsigned char *const ACTIVE_LIST=(void*)0x80c33980u;
static volatile unsigned *const RUN_FILE_SIZE=(void*)0x80c33a7cu;
static volatile void **const GP_BUF=(void*)0x80c33ad8u;
static volatile struct retro_game_info *const GAME_INFO=(void*)0x80c2e914u;

static volatile void **const GFN_STATE_SAVE=(void*)0x80c33a70u;
static volatile void **const GFN_GET_REGION=(void*)0x80c33a9cu;
static volatile void **const GFN_GET_AV=(void*)0x80c33aacu;
static volatile void **const GFN_STATE_LOAD=(void*)0x80c33ac0u;
static volatile void **const GFN_LOAD_GAME=(void*)0x80c33accu;
static volatile void **const GFN_UNLOAD_GAME=(void*)0x80c33ad4u;
static volatile void **const GFN_FRAMESKIP=(void*)0x80c33ae0u;
static volatile void **const GFN_RUN=(void*)0x80c33ae4u;

static const char *const SYS_DIR=(const char*)0x810a0eb0u;
static const char *const GAME_NAME=(const char*)0x8109fce8u;

static int state_stub(const char *p){(void)p;return 1;}
static void stop_sound(void){
    *SND_FLAGS &= 0xfffeu;
    while(*SND_FLAGS!=0) dly_tsk(1);
}
static void cache_flush(void){
    u32 p;
    for(p=0x80000000u;p<=0x80004000u;p+=16u)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)"::"r"(p));
    __asm__ volatile("sync; nop; nop");
    for(p=0x80000000u;p<=0x80004000u;p+=16u)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)"::"r"(p));
    __asm__ volatile("nop; nop; nop; nop; nop");
}
static void irq_patch(u32 *saved0,u32 *saved1){
    volatile u32 *dst=(volatile u32*)0x80049744u;
    volatile u32 *src=(volatile u32*)0x80001270u;
    u32 p;
    os_disable_interrupt();
    *saved0=dst[0]; *saved1=dst[1];
    dst[0]=src[0]; dst[1]=src[1];
    for(p=0x80049740u;p<0x80049750u;p+=16u)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)"::"r"(p));
    __asm__ volatile("sync; nop; nop");
    for(p=0x80049740u;p<0x80049750u;p+=16u)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)"::"r"(p));
    os_enable_interrupt();
}
static void irq_restore(u32 a,u32 b){
    volatile u32 *dst=(volatile u32*)0x80049744u;
    u32 p;
    os_disable_interrupt();
    dst[0]=a; dst[1]=b;
    for(p=0x80049740u;p<0x80049750u;p+=16u)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)"::"r"(p));
    __asm__ volatile("sync; nop; nop");
    for(p=0x80049740u;p<0x80049750u;p+=16u)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)"::"r"(p));
    os_enable_interrupt();
}

void load_and_run_family_mame(const char *filename,int load_state)
{
    FILE *f;
    u32 old_limit,irq0,irq1;
    struct xgo_family_core_api *api;
    struct retro_game_info old_info;
    void *old[8];
    char path[192];
    unsigned i,j;

    if(*ACTIVE_LIST!=LIST_CLASSIC){ stock_run_fba(filename,load_state); return; }
    if(*HEAP_BREAK>=CORE_BASE || XGO_MAME_CORE_SIZE>(CORE_LIMIT-CORE_BASE)){
        stock_run_fba(filename,load_state); return;
    }

    f=fw_fopen("/mnt/sda1/cores/m2k/core_87000000","rb");
    if(!f){ stock_run_fba(filename,load_state); return; }

    stop_sound();
    old_limit=*RAMSIZE;
    *RAMSIZE=CORE_BASE;

    if(fw_fread((void*)CORE_BASE,1,XGO_MAME_CORE_SIZE,f)!=XGO_MAME_CORE_SIZE){
        fw_fclose(f); *RAMSIZE=old_limit; stock_run_fba(filename,load_state); return;
    }
    fw_fclose(f);
    irq_patch(&irq0,&irq1);
    cache_flush();

    api=((struct xgo_family_core_api *(*)(const char*,int))CORE_BASE)(filename,load_state);
    if(!api){ irq_restore(irq0,irq1); *RAMSIZE=old_limit; stock_run_fba(filename,load_state); return; }

    /* Resolve the real stock-selected arcade ZIP path. */
    j=0;
    for(i=0;SYS_DIR[i]&&i<128&&j+1<sizeof(path);++i) path[j++]=SYS_DIR[i];
    if(!j||i>=128||j+6>=sizeof(path)) goto fallback;
    path[j++]='/'; path[j++]='b'; path[j++]='i'; path[j++]='n'; path[j++]='/';
    for(i=0;GAME_NAME[i]&&i<64&&j+1<sizeof(path);++i){
        char ch=GAME_NAME[i]; if(ch=='/'||ch=='\\') goto fallback; path[j++]=ch;
    }
    if(!i||i>=64) goto fallback;
    path[j]=0;

    old_info=*(struct retro_game_info*)GAME_INFO;
    old[0]=(void*)*GFN_STATE_SAVE; old[1]=(void*)*GFN_GET_REGION;
    old[2]=(void*)*GFN_GET_AV; old[3]=(void*)*GFN_STATE_LOAD;
    old[4]=(void*)*GFN_LOAD_GAME; old[5]=(void*)*GFN_UNLOAD_GAME;
    old[6]=(void*)*GFN_FRAMESKIP; old[7]=(void*)*GFN_RUN;

    api->bind_callbacks();
    api->init();

    ((struct retro_game_info*)GAME_INFO)->path=path;
    ((struct retro_game_info*)GAME_INFO)->data=(const void*)*GP_BUF;
    ((struct retro_game_info*)GAME_INFO)->size=*RUN_FILE_SIZE;
    ((struct retro_game_info*)GAME_INFO)->meta=0;

    *GFN_STATE_SAVE=(void*)state_stub;
    *GFN_STATE_LOAD=(void*)state_stub;
    *GFN_GET_REGION=(void*)api->get_region;
    *GFN_GET_AV=(void*)api->get_av;
    *GFN_LOAD_GAME=(void*)api->load_game;
    *GFN_UNLOAD_GAME=(void*)api->unload_game;
    *GFN_FRAMESKIP=0;
    *GFN_RUN=(void*)api->run;

    stock_run_emulator(load_state);
    api->deinit();

    *(struct retro_game_info*)GAME_INFO=old_info;
    *GFN_STATE_SAVE=old[0]; *GFN_GET_REGION=old[1]; *GFN_GET_AV=old[2];
    *GFN_STATE_LOAD=old[3]; *GFN_LOAD_GAME=old[4]; *GFN_UNLOAD_GAME=old[5];
    *GFN_FRAMESKIP=old[6]; *GFN_RUN=old[7];

    irq_restore(irq0,irq1);
    *RAMSIZE=old_limit;
    return;

fallback:
    irq_restore(irq0,irq1);
    *RAMSIZE=old_limit;
    stock_run_fba(filename,load_state);
}
