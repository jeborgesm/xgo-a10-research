/* Native-main-list FB Alpha 2012 CPS-1 frontend for XGO Core #3. */
#include <stddef.h>
typedef int bool;
#define true 1
#define false 0
#define XGO_SYSTEM_ARCADE 0x0040u
#define MAX_ROM_SIZE 0x04000000u
#define XGO_STOCK_SYSTEM_DIR ((const char*)0x810a0eb0u)
#define XGO_STOCK_GAME_NAME  ((const char*)0x8109fce8u)
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
    const char *system_dir;
    const char *game_name;
    char zip_path[192];
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
     * By the time the corrected arcade runtime hook is reached, stock XGO has
     * already resolved the selected arcade package. Reuse the exact frontend
     * globals stock itself feeds to "%s/bin/%s":
     *
     *   0x810a0eb0 = current selected system/list directory
     *   0x8109fce8 = current game/archive filename
     *
     * Do not inspect ROM_BUFFER here; Test 06/07 proved it is no longer a
     * reliable representation of the original .zfb wrapper at this stage.
     */
    system_dir=XGO_STOCK_SYSTEM_DIR;
    game_name=XGO_STOCK_GAME_NAME;
    if(!system_dir || !*system_dir || !game_name || !*game_name)
        return -1;

    j=0;
    for(i=0; system_dir[i] && i<128 && j+1<sizeof(zip_path); ++i)
        zip_path[j++]=system_dir[i];
    if(i==0 || i>=128 || j+5>=sizeof(zip_path))
        return -1;

    zip_path[j++]='/';
    zip_path[j++]='b';
    zip_path[j++]='i';
    zip_path[j++]='n';
    zip_path[j++]='/';

    for(i=0; game_name[i] && i<64 && j+1<sizeof(zip_path); ++i) {
        unsigned char ch=(unsigned char)game_name[i];
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
