/*
 * XGO Classic Arcade family-style stock-side loader.
 *
 * Golden Test08 additive path, list ID 11 only.
 * Transport remains XGOC for bounded/CRC-checked upper-RAM loading, but after
 * entry this follows the SF2000/GB300 ownership contract: consume retro_core_t,
 * install stock callbacks/globals, and let golden run_emulator own the loop.
 */
typedef unsigned int u32;
typedef unsigned long size_t;
typedef int bool;
typedef struct FILE_ FILE;

#define CORE_BASE  0x87000000u
#define CORE_LIMIT 0x87cdae00u
#define LIST_ID     11u
#define XGOC_MAGIC  0x434f4758u
#define FAMILY_ARCADE 0x0040u

struct xgoc {u32 magic,vh,load,entry,psz,msz,pcrc,hcrc;};
struct game_info {const char *path;const void *data;size_t size;const char *meta;};
struct av_info;

typedef bool (*env_t)(unsigned,void*);
typedef void (*video_t)(const void*,unsigned,unsigned,size_t);
typedef void (*audio_t)(short,short);
typedef size_t (*audio_batch_t)(const short*,size_t);
typedef void (*poll_t)(void);
typedef short (*input_t)(unsigned,unsigned,unsigned,unsigned);

struct retro_core_t {
    void (*init)(void); void (*deinit)(void); unsigned (*version)(void);
    void (*sysinfo)(void*); void (*av)(struct av_info*);
    void (*set_env)(env_t); void (*set_video)(video_t);
    void (*set_audio)(audio_t); void (*set_audio_batch)(audio_batch_t);
    void (*set_poll)(poll_t); void (*set_input)(input_t);
    void (*set_device)(unsigned,unsigned); void (*reset)(void); void (*run)(void);
    size_t (*serialize_size)(void); bool (*serialize)(void*,size_t);
    bool (*unserialize)(const void*,size_t); void (*cheat_reset)(void);
    void (*cheat_set)(unsigned,bool,const char*);
    bool (*load_game)(const struct game_info*);
    bool (*load_special)(unsigned,const struct game_info*,size_t);
    void (*unload_game)(void); unsigned (*region)(void);
    void *(*memory_data)(unsigned); size_t (*memory_size)(unsigned);
};

static FILE *(*const fw_fopen)(const char*,const char*)=(void*)0x802b3524;
static size_t (*const fw_fread)(void*,size_t,size_t,FILE*)=(void*)0x802b3698;
static int (*const fw_fclose)(FILE*)=(void*)0x802b2f40;
static int (*const dly_tsk)(unsigned)=(void*)0x8030f480;
static void (*const stock_run_fba)(const char*,int)=(void*)0x80360848;
static void (*const run_emulator)(int)=(void*)0x8035ed48;
static void (*const os_disable_interrupt)(void)=(void*)0x802e0750;
static void (*const os_enable_interrupt)(void)=(void*)0x802e0778;

static volatile u32 *const RAMSIZE=(void*)0x80c2ce6c;
static volatile u32 *const HEAP_BREAK=(void*)0x80c337b0;
static volatile u32 *const SND_FLAGS=(void*)0x80c2e80c;
static volatile unsigned char *const ACTIVE_LIST=(void*)0x80c33980;

#define GAME_INFO (*(volatile struct game_info*)0x80c2e914u)
#define RUN_FILE_SIZE (*(volatile u32*)0x80c33a7cu)
#define STATE_SAVE (*(int (**)(const char*))0x80c33a70u)
#define GET_REGION (*(unsigned (**)(void))0x80c33a9cu)
#define GET_AV (*(void (**)(struct av_info*))0x80c33aacu)
#define STATE_LOAD (*(int (**)(const char*))0x80c33ac0u)
#define LOAD_GAME (*(bool (**)(const struct game_info*))0x80c33accu)
#define UNLOAD_GAME (*(void (**)(void))0x80c33ad4u)
#define BUF64 (*(void**)0x80c33ad8u)
#define SYSTEM_FAMILY (*(volatile unsigned short*)0x80c33ad0u)
#define FRAMESKIP (*(void (**)(int))0x80c33ae0u)
#define RUN_GAME (*(void (**)(void))0x80c33ae4u)
#define RUN_PHASE (*(volatile u32*)0x80c2e964u)

static int state_stub(const char *p){(void)p;return 1;}

static u32 crc32_ieee(const unsigned char *p,u32 n)
{
    u32 c=0xffffffffu,i,j;
    for(i=0;i<n;i++){c^=p[i];for(j=0;j<8;j++)c=(c>>1)^(0xedb88320u&(0u-(c&1u)));}
    return ~c;
}

static void zero_range(unsigned char *p,u32 n){while(n--)*p++=0;}

static void full_cache_flush(void)
{
    u32 p;
    for(p=0x80000000u;p<=0x80004000u;p+=16u)
        __asm__ volatile("cache 1,0(%0);cache 1,0(%0)"::"r"(p));
    __asm__ volatile("sync;nop;nop");
    for(p=0x80000000u;p<=0x80004000u;p+=16u)
        __asm__ volatile("cache 0,0(%0);cache 0,0(%0)"::"r"(p));
}

static void repair_irq_gp(void)
{
    volatile u32 *src=(volatile u32*)0x80001270u;
    volatile u32 *dst=(volatile u32*)0x80049744u;
    os_disable_interrupt();
    dst[0]=src[0];dst[1]=src[1];
    __asm__ volatile("cache 1,0(%0);cache 1,0(%0);sync"::"r"(dst));
    __asm__ volatile("cache 0,0(%0);nop;nop"::"r"(dst));
    os_enable_interrupt();
}

static int build_path(char *out)
{
    const char *dir=(const char*)0x810a0eb0u;
    const char *game=(const char*)0x8109fce8u;
    u32 i=0,j=0;
    if(!dir || !*dir || !game || !*game) return 0;
    while(dir[i] && i<128u) out[j++]=dir[i++];
    if(i==0 || i>=128u) return 0;
    out[j++]='/';out[j++]='b';out[j++]='i';out[j++]='n';out[j++]='/';
    i=0;
    while(game[i] && i<64u){
        char ch=game[i++];
        if(ch=='/' || ch=='\\') return 0;
        out[j++]=ch;
    }
    if(i==0 || i>=64u) return 0;
    out[j]=0;
    return 1;
}

void load_and_run_classic_family(const char *filename,int load_state)
{
    FILE *f;
    struct xgoc h;
    u32 old_ram;
    struct retro_core_t *api;
    char path[200];
    struct game_info old_game;
    int (*old_save)(const char*),(*old_load)(const char*);
    unsigned (*old_region)(void);
    void (*old_av)(struct av_info*),(*old_unload)(void),(*old_run)(void),(*old_skip)(int);
    bool (*old_load_game)(const struct game_info*);
    unsigned short old_family;
    u32 old_phase;

    if(*ACTIVE_LIST!=LIST_ID || *HEAP_BREAK>=CORE_BASE){stock_run_fba(filename,load_state);return;}

    f=fw_fopen("/mnt/sda1/cores/mame2000/core.xgc","rb");
    if(!f){stock_run_fba(filename,load_state);return;}
    if(fw_fread(&h,1,sizeof(h),f)!=sizeof(h) ||
       h.magic!=XGOC_MAGIC || h.load!=CORE_BASE || !h.psz ||
       h.msz<h.psz || h.msz>(CORE_LIMIT-CORE_BASE)){
        fw_fclose(f);stock_run_fba(filename,load_state);return;
    }

    *SND_FLAGS&=0xfffeu;
    while(*SND_FLAGS) dly_tsk(1);
    old_ram=*RAMSIZE;
    *RAMSIZE=CORE_BASE;

    if(fw_fread((void*)CORE_BASE,1,h.psz,f)!=h.psz){
        fw_fclose(f);*RAMSIZE=old_ram;stock_run_fba(filename,load_state);return;
    }
    fw_fclose(f);
    if(crc32_ieee((const unsigned char*)CORE_BASE,h.psz)!=h.pcrc){
        *RAMSIZE=old_ram;stock_run_fba(filename,load_state);return;
    }
    zero_range((unsigned char*)(CORE_BASE+h.psz),h.msz-h.psz);
    repair_irq_gp();
    full_cache_flush();

    api=((struct retro_core_t *(*)(void))(CORE_BASE+h.entry))();
    if(!api || !build_path(path)){
        *RAMSIZE=old_ram;stock_run_fba(filename,load_state);return;
    }

    old_game.path=GAME_INFO.path;old_game.data=GAME_INFO.data;
    old_game.size=GAME_INFO.size;old_game.meta=GAME_INFO.meta;
    old_save=STATE_SAVE;old_load=STATE_LOAD;old_region=GET_REGION;old_av=GET_AV;
    old_load_game=LOAD_GAME;old_unload=UNLOAD_GAME;old_run=RUN_GAME;old_skip=FRAMESKIP;
    old_family=SYSTEM_FAMILY;old_phase=RUN_PHASE;

    STATE_SAVE=state_stub;STATE_LOAD=state_stub;
    SYSTEM_FAMILY=FAMILY_ARCADE;RUN_PHASE=0;

    api->set_video((video_t)0x8035e70c);
    api->set_audio_batch((audio_batch_t)0x8035e7d8);
    api->set_poll((poll_t)0x8035ea30);
    api->set_input((input_t)0x8035eb20);
    api->set_env((env_t)0x8035eb64);
    api->init();

    GAME_INFO.path=path;GAME_INFO.data=BUF64;GAME_INFO.size=RUN_FILE_SIZE;GAME_INFO.meta=0;
    GET_REGION=api->region;GET_AV=api->av;LOAD_GAME=api->load_game;
    UNLOAD_GAME=api->unload_game;RUN_GAME=api->run;FRAMESKIP=0;

    run_emulator(load_state);
    api->deinit();

    FRAMESKIP=old_skip;RUN_GAME=old_run;UNLOAD_GAME=old_unload;
    LOAD_GAME=old_load_game;GET_AV=old_av;GET_REGION=old_region;
    STATE_LOAD=old_load;STATE_SAVE=old_save;
    SYSTEM_FAMILY=old_family;RUN_PHASE=old_phase;
    GAME_INFO.path=old_game.path;GAME_INFO.data=old_game.data;
    GAME_INFO.size=old_game.size;GAME_INFO.meta=old_game.meta;
    *RAMSIZE=old_ram;
}
