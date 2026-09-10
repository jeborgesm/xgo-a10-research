/*
 * XGO MAME2000 family-style core API wrapper.
 *
 * Mirrors the SF2000/GB300 multicore ownership model:
 * the entry at 0x87000000 initializes the external runtime and returns an API
 * table.  The stock-side loader owns callback installation and run_emulator().
 *
 * XGO-specific retained behavior:
 * - MAME2000 environment policy from the hardware-proven Test12 lineage;
 * - joypad-only input filtering;
 * - family-style L+R -> internal first-channel mono fold-down while preserving
 *   the second channel for external stereo paths;
 * - MAME2000 admin/service-key source patch is applied at build time.
 */
#include <stddef.h>
#include <reent.h>
typedef int bool;
#define true 1
#define false 0

struct retro_game_info { const char *path; const void *data; size_t size; const char *meta; };
struct retro_system_info;
struct retro_system_av_info;

typedef bool (*retro_environment_t)(unsigned,void*);
typedef void (*retro_video_refresh_t)(const void*,unsigned,unsigned,size_t);
typedef void (*retro_audio_sample_t)(short,short);
typedef size_t (*retro_audio_sample_batch_t)(const short*,size_t);
typedef void (*retro_input_poll_t)(void);
typedef short (*retro_input_state_t)(unsigned,unsigned,unsigned,unsigned);

extern void retro_init(void);
extern void retro_deinit(void);
extern unsigned retro_api_version(void);
extern void retro_get_system_info(struct retro_system_info*);
extern void retro_get_system_av_info(struct retro_system_av_info*);
extern void retro_set_environment(retro_environment_t);
extern void retro_set_video_refresh(retro_video_refresh_t);
extern void retro_set_audio_sample(retro_audio_sample_t);
extern void retro_set_audio_sample_batch(retro_audio_sample_batch_t);
extern void retro_set_input_poll(retro_input_poll_t);
extern void retro_set_input_state(retro_input_state_t);
extern void retro_set_controller_port_device(unsigned,unsigned);
extern void retro_reset(void);
extern void retro_run(void);
extern size_t retro_serialize_size(void);
extern bool retro_serialize(void*,size_t);
extern bool retro_unserialize(const void*,size_t);
extern void retro_cheat_reset(void);
extern void retro_cheat_set(unsigned,bool,const char*);
extern bool retro_load_game(const struct retro_game_info*);
extern bool retro_load_game_special(unsigned,const struct retro_game_info*,size_t);
extern void retro_unload_game(void);
extern unsigned retro_get_region(void);
extern void *retro_get_memory_data(unsigned);
extern size_t retro_get_memory_size(unsigned);

extern bool xgo_mame2000_environment(unsigned,void*);

#define RETRO_DEVICE_JOYPAD 1u
#define XGO_GFN_FRAMESKIP (*(void (**)(int))0x80c33ae0u)

static retro_input_state_t host_input_state;
static retro_audio_sample_batch_t host_audio_batch;
static retro_audio_sample_t host_audio_sample;

static short family_input_state(unsigned port,unsigned device,unsigned index,unsigned id)
{
    if(!host_input_state || device!=RETRO_DEVICE_JOYPAD ||
       index!=0 || port>=2 || id>=16)
        return 0;
    return host_input_state(port,device,index,id);
}

static size_t family_audio_batch(const short *data,size_t frames)
{
    size_t i;
    short *rw=(short*)data;
    if(!host_audio_batch) return frames;
    for(i=0;i<frames*2;i+=2)
        rw[i]=(short)((data[i]>>1)+(data[i+1]>>1));
    host_audio_batch(data,frames);
    return frames;
}

static void family_audio_sample(short left,short right)
{
    short pair[2];
    if(host_audio_sample) {
        host_audio_sample((short)((left>>1)+(right>>1)),right);
        return;
    }
    if(host_audio_batch) {
        pair[0]=(short)((left>>1)+(right>>1));
        pair[1]=right;
        host_audio_batch(pair,1);
    }
}

static void wrap_set_environment(retro_environment_t cb)
{
    (void)cb;
    retro_set_environment(xgo_mame2000_environment);
}

static void wrap_set_audio_sample(retro_audio_sample_t cb)
{
    host_audio_sample=cb;
    retro_set_audio_sample(family_audio_sample);
}

static void wrap_set_audio_batch(retro_audio_sample_batch_t cb)
{
    host_audio_batch=cb;
    retro_set_audio_sample_batch(family_audio_batch);
}

static void wrap_set_input_state(retro_input_state_t cb)
{
    host_input_state=cb;
    retro_set_input_state(family_input_state);
}

static bool wrap_load_game(const struct retro_game_info *info)
{
    bool ok;
    /* Never allow a stale stock-FBA frameskip callback into MAME2000. */
    XGO_GFN_FRAMESKIP=0;
    ok=retro_load_game(info);
    if(ok) {
        retro_set_controller_port_device(0,RETRO_DEVICE_JOYPAD);
        retro_set_controller_port_device(1,RETRO_DEVICE_JOYPAD);
    }
    return ok;
}

struct retro_core_t {
    void (*retro_init)(void);
    void (*retro_deinit)(void);
    unsigned (*retro_api_version)(void);
    void (*retro_get_system_info)(struct retro_system_info*);
    void (*retro_get_system_av_info)(struct retro_system_av_info*);
    void (*retro_set_environment)(retro_environment_t);
    void (*retro_set_video_refresh)(retro_video_refresh_t);
    void (*retro_set_audio_sample)(retro_audio_sample_t);
    void (*retro_set_audio_sample_batch)(retro_audio_sample_batch_t);
    void (*retro_set_input_poll)(retro_input_poll_t);
    void (*retro_set_input_state)(retro_input_state_t);
    void (*retro_set_controller_port_device)(unsigned,unsigned);
    void (*retro_reset)(void);
    void (*retro_run)(void);
    size_t (*retro_serialize_size)(void);
    bool (*retro_serialize)(void*,size_t);
    bool (*retro_unserialize)(const void*,size_t);
    void (*retro_cheat_reset)(void);
    void (*retro_cheat_set)(unsigned,bool,const char*);
    bool (*retro_load_game)(const struct retro_game_info*);
    bool (*retro_load_game_special)(unsigned,const struct retro_game_info*,size_t);
    void (*retro_unload_game)(void);
    unsigned (*retro_get_region)(void);
    void *(*retro_get_memory_data)(unsigned);
    size_t (*retro_get_memory_size)(unsigned);
};

static struct retro_core_t core_exports={
    retro_init,retro_deinit,retro_api_version,retro_get_system_info,
    retro_get_system_av_info,wrap_set_environment,retro_set_video_refresh,
    wrap_set_audio_sample,wrap_set_audio_batch,retro_set_input_poll,
    wrap_set_input_state,retro_set_controller_port_device,retro_reset,retro_run,
    retro_serialize_size,retro_serialize,retro_unserialize,retro_cheat_reset,
    retro_cheat_set,wrap_load_game,retro_load_game_special,retro_unload_game,
    retro_get_region,retro_get_memory_data,retro_get_memory_size
};

static void clear_bss(void)
{
    extern unsigned char __bss_start;
    extern unsigned char _end;
    unsigned char *p=&__bss_start;
    while(p<&_end) *p++=0;
}

struct retro_core_t *__core_entry__(void)
    __attribute__((section(".init.core_entry")));

struct retro_core_t *__core_entry__(void)
{
    extern void __sinit(struct _reent*);
    extern void __libc_init_array(void);

    clear_bss();
    _REENT_INIT_PTR(_REENT);
    __sinit(_REENT);
    __libc_init_array();
    return &core_exports;
}
