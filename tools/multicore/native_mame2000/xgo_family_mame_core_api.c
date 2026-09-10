/*
 * XGO family-style MAME2000 raw-core wrapper.
 *
 * Mirrors the SF2000/GB300 Multicore contract:
 *   raw image @ 0x87000000
 *   entry initializes core runtime
 *   entry returns an API table
 *   stock firmware owns run_emulator()
 *
 * XGO-specific difference:
 * every stock/core boundary is routed through already-proven GP veneers.
 */
typedef unsigned int u32;
typedef unsigned long size_t;
typedef int bool;
#define true 1
#define false 0

struct retro_game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};
struct retro_system_av_info;

extern void retro_init(void);
extern void retro_deinit(void);
extern unsigned retro_get_region(void);
extern void retro_get_system_av_info(struct retro_system_av_info *);
extern bool retro_load_game(const struct retro_game_info *);
extern void retro_unload_game(void);
extern void retro_run(void);
extern void retro_set_environment(bool (*)(unsigned,void*));
extern void retro_set_video_refresh(void (*)(const void*,unsigned,unsigned,size_t));
extern void retro_set_audio_sample_batch(size_t (*)(const short*,size_t));
extern void retro_set_input_poll(void (*)(void));
extern void retro_set_input_state(short (*)(unsigned,unsigned,unsigned,unsigned));

extern void xgo_stock_video_refresh(const void*,unsigned,unsigned,size_t);
extern size_t xgo_stock_audio_sample_batch(const short*,size_t);
extern void xgo_stock_input_poll(void);
extern short xgo_stock_input_state(unsigned,unsigned,unsigned,unsigned);
extern bool xgo_mame2000_environment(unsigned,void*);

#define RETRO_DEVICE_JOYPAD 1u

static short xgo_family_input_state(unsigned port,unsigned device,
                                    unsigned index,unsigned id)
{
    if(device!=RETRO_DEVICE_JOYPAD || index!=0 || port>=2 || id>=16)
        return 0;
    return xgo_stock_input_state(port,device,index,id);
}

void xgo_family_init_impl(void){ retro_init(); }
void xgo_family_deinit_impl(void){ retro_deinit(); }
unsigned xgo_family_get_region_impl(void){ return retro_get_region(); }
void xgo_family_get_av_impl(struct retro_system_av_info *i){ retro_get_system_av_info(i); }
bool xgo_family_load_game_impl(const struct retro_game_info *i){ return retro_load_game(i); }
void xgo_family_unload_game_impl(void){ retro_unload_game(); }
void xgo_family_run_impl(void){ retro_run(); }

void xgo_family_bind_impl(void)
{
    retro_set_video_refresh(xgo_stock_video_refresh);
    retro_set_audio_sample_batch(xgo_stock_audio_sample_batch);
    retro_set_input_poll(xgo_stock_input_poll);
    retro_set_input_state(xgo_family_input_state);
    retro_set_environment(xgo_mame2000_environment);
}

/* Entry points below are assembly veneers that install external _gp before
 * calling the implementation functions above. */
extern void xgo_family_api_init(void);
extern void xgo_family_api_deinit(void);
extern void xgo_family_api_bind(void);
extern unsigned xgo_family_api_get_region(void);
extern void xgo_family_api_get_av(struct retro_system_av_info*);
extern bool xgo_family_api_load_game(const struct retro_game_info*);
extern void xgo_family_api_unload_game(void);
extern void xgo_family_api_run(void);

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

static struct xgo_family_core_api api = {
    xgo_family_api_bind,
    xgo_family_api_init,
    xgo_family_api_deinit,
    xgo_family_api_get_region,
    xgo_family_api_get_av,
    xgo_family_api_load_game,
    xgo_family_api_unload_game,
    xgo_family_api_run
};

#include <reent.h>
extern unsigned char __bss_start[];
extern unsigned char __image_end[];
extern void __libc_init_array(void);
extern void __sinit(struct _reent*);

void *__core_entry_c(const char *unused,int unused2)
{
    unsigned char *p;
    (void)unused; (void)unused2;
    for(p=__bss_start;p<__image_end;++p) *p=0;
    _REENT_INIT_PTR(_REENT);
    __sinit(_REENT);
    __libc_init_array();
    return &api;
}
