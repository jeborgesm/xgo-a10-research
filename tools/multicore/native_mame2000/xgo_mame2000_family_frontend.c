/*
 * XGO list-11 family-style MAME2000 frontend transaction.
 *
 * Runs inside the external image but follows the family ownership contract:
 * obtain the core API table, install stock callbacks/slots, then let golden
 * run_emulator() own the loop. Golden firmware is not replaced.
 */
typedef unsigned int u32;
typedef unsigned long size_t;
typedef int bool;
#define NULL ((void*)0)
#define ARCADE_FAMILY 0x40u
#define FAMILY_MASK 0xffu
#define MAXPATH 256

struct retro_game_info { const char *path; const void *data; size_t size; const char *meta; };
struct retro_system_av_info;
struct retro_system_info;
typedef bool (*retro_environment_t)(unsigned,void*);
typedef void (*retro_video_refresh_t)(const void*,unsigned,unsigned,size_t);
typedef void (*retro_audio_sample_t)(short,short);
typedef size_t (*retro_audio_sample_batch_t)(const short*,size_t);
typedef void (*retro_input_poll_t)(void);
typedef short (*retro_input_state_t)(unsigned,unsigned,unsigned,unsigned);

struct retro_core_t {
 void (*retro_init)(void); void (*retro_deinit)(void); unsigned (*retro_api_version)(void);
 void (*retro_get_system_info)(struct retro_system_info*); void (*retro_get_system_av_info)(struct retro_system_av_info*);
 void (*retro_set_environment)(retro_environment_t); void (*retro_set_video_refresh)(retro_video_refresh_t);
 void (*retro_set_audio_sample)(retro_audio_sample_t); void (*retro_set_audio_sample_batch)(retro_audio_sample_batch_t);
 void (*retro_set_input_poll)(retro_input_poll_t); void (*retro_set_input_state)(retro_input_state_t);
 void (*retro_set_controller_port_device)(unsigned,unsigned); void (*retro_reset)(void); void (*retro_run)(void);
 size_t (*retro_serialize_size)(void); bool (*retro_serialize)(void*,size_t); bool (*retro_unserialize)(const void*,size_t);
 void (*retro_cheat_reset)(void); void (*retro_cheat_set)(unsigned,bool,const char*);
 bool (*retro_load_game)(const struct retro_game_info*); bool (*retro_load_game_special)(unsigned,const struct retro_game_info*,size_t);
 void (*retro_unload_game)(void); unsigned (*retro_get_region)(void); void *(*retro_get_memory_data)(unsigned);
 size_t (*retro_get_memory_size)(unsigned);
};

extern struct retro_core_t *__core_entry_c(void);
extern bool xgo_minimal_environment(unsigned,void*);
extern void retro_video_refresh_cb(const void*,unsigned,unsigned,size_t);
extern size_t retro_audio_sample_batch_cb(const short*,size_t);
extern void retro_input_poll_cb(void);
extern short retro_input_state_cb(unsigned,unsigned,unsigned,unsigned);
extern void run_emulator(int);

extern struct retro_game_info g_retro_game_info;
extern int (*gfn_state_save)(const char*);
extern int (*gfn_state_load)(const char*);
extern unsigned (*gfn_retro_get_region)(void);
extern void (*gfn_get_system_av_info)(struct retro_system_av_info*);
extern bool (*gfn_retro_load_game)(const struct retro_game_info*);
extern void (*gfn_retro_unload_game)(void);
extern void (*gfn_retro_run)(void);
extern void (*gfn_frameskip)(int);
extern volatile u32 XGO_ACTIVE_SYSTEM_FAMILY;
#define XGO_RUN_PHASE_COUNTER (*(volatile u32*)0x80c2e964u)

static char rom_path[MAXPATH];
static int state_stub(const char *p){(void)p;return 1;}

static int build_rom_path(const char *filename)
{
    const char *p,*base=filename,*dot=0; unsigned n=0,i;
    static const char pre[]="/mnt/sda1/ARCADE/";
    if(!filename) return 0;
    for(p=filename;*p;p++){ if(*p=='/'||*p=='\\') base=p+1; if(*p=='.') dot=p; }
    if(dot && dot>base) p=dot; else for(p=base;*p;p++);
    for(i=0;pre[i];i++) rom_path[n++]=pre[i];
    while(base<p && n+5<MAXPATH) rom_path[n++]=*base++;
    rom_path[n++]='.';rom_path[n++]='z';rom_path[n++]='i';rom_path[n++]='p';rom_path[n]=0;
    return 1;
}

void __start(const char *filename,int load_state)
{
    struct retro_core_t *api;
    u32 old_family=XGO_ACTIVE_SYSTEM_FAMILY, old_phase=XGO_RUN_PHASE_COUNTER;
    struct retro_game_info old_info=g_retro_game_info;
    int (*old_ss)(const char*)=gfn_state_save,(*old_sl)(const char*)=gfn_state_load;
    unsigned (*old_gr)(void)=gfn_retro_get_region;
    void (*old_av)(struct retro_system_av_info*)=gfn_get_system_av_info;
    bool (*old_lg)(const struct retro_game_info*)=gfn_retro_load_game;
    void (*old_ug)(void)=gfn_retro_unload_game;
    void (*old_run)(void)=gfn_retro_run;
    void (*old_fs)(int)=gfn_frameskip;

    if(!build_rom_path(filename)) return;
    api=__core_entry_c();
    if(!api) return;

    XGO_ACTIVE_SYSTEM_FAMILY=(old_family&~FAMILY_MASK)|ARCADE_FAMILY;
    XGO_RUN_PHASE_COUNTER=0;

    api->retro_set_video_refresh(retro_video_refresh_cb);
    api->retro_set_audio_sample_batch(retro_audio_sample_batch_cb);
    api->retro_set_input_poll(retro_input_poll_cb);
    api->retro_set_input_state(retro_input_state_cb);
    api->retro_set_environment(xgo_minimal_environment);
    api->retro_init();

    g_retro_game_info.path=rom_path; g_retro_game_info.data=NULL; g_retro_game_info.size=0; g_retro_game_info.meta=NULL;
    gfn_state_save=state_stub; gfn_state_load=state_stub;
    gfn_retro_get_region=api->retro_get_region;
    gfn_get_system_av_info=api->retro_get_system_av_info;
    gfn_retro_load_game=api->retro_load_game;
    gfn_retro_unload_game=api->retro_unload_game;
    gfn_retro_run=api->retro_run;
    gfn_frameskip=NULL;

    run_emulator(load_state);
    api->retro_deinit();

    gfn_frameskip=old_fs; gfn_retro_run=old_run; gfn_retro_unload_game=old_ug;
    gfn_retro_load_game=old_lg; gfn_get_system_av_info=old_av; gfn_retro_get_region=old_gr;
    gfn_state_load=old_sl; gfn_state_save=old_ss; g_retro_game_info=old_info;
    XGO_RUN_PHASE_COUNTER=old_phase; XGO_ACTIVE_SYSTEM_FAMILY=old_family;
}
