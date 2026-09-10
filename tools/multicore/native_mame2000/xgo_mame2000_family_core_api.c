/*
 * XGO Classic Arcade family-style MAME2000 core wrapper.
 *
 * Entry ABI matches SF2000/GB300 Multicore: __core_entry__ returns a table of
 * libretro function pointers. The stock-side list-11 loader owns the frontend
 * transaction and stock run_emulator().
 */
typedef unsigned long size_t;
typedef int bool;

struct retro_game_info { const char *path; const void *data; size_t size; const char *meta; };
struct retro_system_info;
struct retro_system_av_info;

typedef bool (*retro_environment_t)(unsigned, void *);
typedef void (*retro_video_refresh_t)(const void *, unsigned, unsigned, size_t);
typedef void (*retro_audio_sample_t)(short, short);
typedef size_t (*retro_audio_sample_batch_t)(const short *, size_t);
typedef void (*retro_input_poll_t)(void);
typedef short (*retro_input_state_t)(unsigned,unsigned,unsigned,unsigned);

extern void retro_init(void);
extern void retro_deinit(void);
extern unsigned retro_api_version(void);
extern void retro_get_system_info(struct retro_system_info *);
extern void retro_get_system_av_info(struct retro_system_av_info *);
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
extern bool retro_serialize(void *,size_t);
extern bool retro_unserialize(const void *,size_t);
extern void retro_cheat_reset(void);
extern void retro_cheat_set(unsigned,bool,const char *);
extern bool retro_load_game(const struct retro_game_info *);
extern bool retro_load_game_special(unsigned,const struct retro_game_info *,size_t);
extern void retro_unload_game(void);
extern unsigned retro_get_region(void);
extern void *retro_get_memory_data(unsigned);
extern size_t retro_get_memory_size(unsigned);

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

static struct retro_core_t core_exports = {
 retro_init, retro_deinit, retro_api_version, retro_get_system_info,
 retro_get_system_av_info, retro_set_environment, retro_set_video_refresh,
 retro_set_audio_sample, retro_set_audio_sample_batch, retro_set_input_poll,
 retro_set_input_state, retro_set_controller_port_device, retro_reset, retro_run,
 retro_serialize_size, retro_serialize, retro_unserialize, retro_cheat_reset,
 retro_cheat_set, retro_load_game, retro_load_game_special, retro_unload_game,
 retro_get_region, retro_get_memory_data, retro_get_memory_size
};

struct retro_core_t *__core_entry_c(void)
{
    return &core_exports;
}
