/* Native-main-list FB Alpha 2012 CPS-1 frontend for XGO Core #3. */
#include <stddef.h>
typedef int bool;
#define true 1
#define false 0
#define XGO_SYSTEM_ARCADE 0x0040u
#define MAX_ROM_SIZE 0x04000000u
#define XGO_ZFB_THUMBNAIL_SIZE 59904u
#define XGO_ZFB_ZIPNAME_OFFSET (XGO_ZFB_THUMBNAIL_SIZE + 4u)
#define XGO_ARCADE_BIN_PREFIX "/mnt/sda1/ARCADE/bin/"

/* crtbegin normally provides this for C++ static-object registration.
 * External XGOC images use -nostartfiles, so provide the freestanding anchor
 * explicitly. __libc_init_array() still executes the actual constructors. */
void *__dso_handle = &__dso_handle;

struct retro_game_info { const char *path; const void *data; size_t size; const char *meta; };
struct retro_system_av_info;
typedef bool (*environment_cb)(unsigned,void*);
typedef void (*video_cb)(const void*,unsigned,unsigned,size_t);
typedef size_t (*audio_batch_cb)(const short*,size_t);
typedef void (*poll_cb)(void);
typedef short (*input_cb)(unsigned,unsigned,unsigned,unsigned);

extern void retro_init(void);
extern void retro_deinit(void);
extern void retro_set_environment(environment_cb);
extern void retro_set_video_refresh(video_cb);
extern void retro_set_audio_sample_batch(audio_batch_cb);
extern void retro_set_input_poll(poll_cb);
extern void retro_set_input_state(input_cb);
extern void retro_get_system_av_info(struct retro_system_av_info*);
extern bool retro_load_game(const struct retro_game_info*);
extern void retro_unload_game(void);
extern void retro_run(void);
extern unsigned retro_get_region(void);

extern bool xgo_cps1_environment(unsigned,void*);
extern void xgo_stock_video_refresh(const void*,unsigned,unsigned,size_t);
extern size_t xgo_stock_audio_sample_batch(const short*,size_t);
extern void xgo_stock_input_poll(void);
extern short xgo_stock_input_state(unsigned,unsigned,unsigned,unsigned);
extern void xgo_stock_run_emulator(int);
extern unsigned xgo_core_get_region(void);
extern void xgo_core_get_av(struct retro_system_av_info*);
extern bool xgo_core_load_game(const struct retro_game_info*);
extern void xgo_core_unload_game(void);
extern void xgo_core_run(void);
extern int xgo_core_state_save(const char*);
extern int xgo_core_state_load(const char*);

#define GAME_INFO (*(volatile struct retro_game_info*)0x80c2e914u)
#define ROM_BUFFER (*(void**)0x80c33ad8u)
#define RUN_FILE_SIZE (*(volatile unsigned*)0x80c33a7cu)
#define SYSTEM_FAMILY (*(volatile unsigned short*)0x80c33ad0u)
#define EMULATOR_LOOP_COUNTER (*(volatile unsigned*)0x80c2e964u)
#define GFN_STATE_LOAD (*(int (**)(const char*))0x80c33a70u)
#define GFN_GET_REGION (*(unsigned (**)(void))0x80c33a9cu)
#define GFN_GET_AV (*(void (**)(struct retro_system_av_info*))0x80c33aacu)
#define GFN_STATE_SAVE (*(int (**)(const char*))0x80c33ac0u)
#define GFN_LOAD_GAME (*(bool (**)(const struct retro_game_info*))0x80c33accu)
#define GFN_UNLOAD_GAME (*(void (**)(void))0x80c33ad4u)
#define GFN_FRAMESKIP (*(void**)0x80c33ae0u)
#define GFN_RUN (*(void (**)(void))0x80c33ae4u)

unsigned xgo_diag_get_region(void){return retro_get_region();}
void xgo_diag_get_av(struct retro_system_av_info *i){retro_get_system_av_info(i);}
bool xgo_diag_load_game(const struct retro_game_info *i){return retro_load_game(i);}
void xgo_diag_unload_game(void){retro_unload_game();}
void xgo_diag_run(void){retro_run();}

#include <reent.h>
extern void __libc_init_array(void);
extern void __sinit(struct _reent*);
static void init_core_runtime(void)
{
    _REENT_INIT_PTR(_REENT);
    __sinit(_REENT);
    __libc_init_array();
}

int __core_entry_c(const char *filename,int load_state)
{
    struct retro_game_info old_game_info;
    unsigned old_run_file_size,rom_size;
    const unsigned char *zfb;
    const char *zip_name;
    char zip_path[160];
    unsigned i, j;
    unsigned short old_system_family;
    int (*old_state_save)(const char*),(*old_state_load)(const char*);
    unsigned (*old_get_region)(void);
    void (*old_get_av)(struct retro_system_av_info*);
    bool (*old_load_game)(const struct retro_game_info*);
    void (*old_unload_game)(void),(*old_run)(void);
    void *old_frameskip;

    init_core_runtime();
    rom_size=RUN_FILE_SIZE;
    if(!filename || !*filename || !ROM_BUFFER)
        return -1;

    /*
     * XGO arcade menu entries are .zfb wrappers, not the real ROM ZIPs.
     * Stock run_game() has already preloaded the selected wrapper into
     * ROM_BUFFER. Its on-card layout is:
     *
     *   59904 bytes RGB565 thumbnail
     *       4 bytes zero
     *       N bytes real ZIP basename (e.g. "sf2.zip")
     *       2 bytes zero
     *
     * FBA2012 identifies the driver from the ZIP basename, so recover the
     * embedded name and point the core at ARCADE/bin/<name>.zip.
     */
    if (rom_size <= XGO_ZFB_ZIPNAME_OFFSET + 2u)
        return -1;

    zfb=(const unsigned char*)ROM_BUFFER;
    if(zfb[XGO_ZFB_THUMBNAIL_SIZE+0] ||
       zfb[XGO_ZFB_THUMBNAIL_SIZE+1] ||
       zfb[XGO_ZFB_THUMBNAIL_SIZE+2] ||
       zfb[XGO_ZFB_THUMBNAIL_SIZE+3])
        return -1;

    zip_name=(const char*)(zfb + XGO_ZFB_ZIPNAME_OFFSET);

    j=0;
    for(i=0; XGO_ARCADE_BIN_PREFIX[i] && j+1<sizeof(zip_path); ++i)
        zip_path[j++]=XGO_ARCADE_BIN_PREFIX[i];

    for(i=0; i<64 && j+1<sizeof(zip_path); ++i) {
        unsigned char ch=(unsigned char)zip_name[i];
        if(!ch)
            break;
        /* Embedded value is a basename only; reject path traversal/separators. */
        if(ch=='/' || ch=='\\')
            return -1;
        zip_path[j++]=(char)ch;
    }
    if(i==0 || i>=64)
        return -1;
    zip_path[j]=0;

    old_game_info.path=GAME_INFO.path;
    old_game_info.data=GAME_INFO.data;
    old_game_info.size=GAME_INFO.size;
    old_game_info.meta=GAME_INFO.meta;
    old_run_file_size=RUN_FILE_SIZE;
    old_system_family=SYSTEM_FAMILY;
    old_state_save=GFN_STATE_SAVE;
    old_state_load=GFN_STATE_LOAD;
    old_get_region=GFN_GET_REGION;
    old_get_av=GFN_GET_AV;
    old_load_game=GFN_LOAD_GAME;
    old_unload_game=GFN_UNLOAD_GAME;
    old_run=GFN_RUN;
    old_frameskip=GFN_FRAMESKIP;

    SYSTEM_FAMILY=XGO_SYSTEM_ARCADE;
    EMULATOR_LOOP_COUNTER=0;

    retro_set_video_refresh(xgo_stock_video_refresh);
    retro_set_audio_sample_batch(xgo_stock_audio_sample_batch);
    retro_set_input_poll(xgo_stock_input_poll);
    retro_set_input_state(xgo_stock_input_state);
    retro_set_environment(xgo_cps1_environment);
    retro_init();

    /* FBA2012 CPS1 is full-path based and must see the real ARCADE/bin ZIP,
     * not the menu-facing .zfb wrapper path. */
    GAME_INFO.path=zip_path;
    GAME_INFO.data=0;
    GAME_INFO.size=0;
    GAME_INFO.meta=0;

    GFN_STATE_SAVE=xgo_core_state_save;
    GFN_STATE_LOAD=xgo_core_state_load;
    GFN_GET_REGION=xgo_core_get_region;
    GFN_GET_AV=xgo_core_get_av;
    GFN_LOAD_GAME=xgo_core_load_game;
    GFN_UNLOAD_GAME=xgo_core_unload_game;
    GFN_RUN=xgo_core_run;
    GFN_FRAMESKIP=0;

    xgo_stock_run_emulator(load_state);
    retro_deinit();

    GFN_STATE_SAVE=old_state_save;
    GFN_STATE_LOAD=old_state_load;
    GFN_GET_REGION=old_get_region;
    GFN_GET_AV=old_get_av;
    GFN_LOAD_GAME=old_load_game;
    GFN_UNLOAD_GAME=old_unload_game;
    GFN_RUN=old_run;
    GFN_FRAMESKIP=old_frameskip;
    SYSTEM_FAMILY=old_system_family;
    RUN_FILE_SIZE=old_run_file_size;
    GAME_INFO.path=old_game_info.path;
    GAME_INFO.data=old_game_info.data;
    GAME_INFO.size=old_game_info.size;
    GAME_INFO.meta=old_game_info.meta;
    return 0;
}
