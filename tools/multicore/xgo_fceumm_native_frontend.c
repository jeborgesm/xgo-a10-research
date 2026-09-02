/*
 * Stripped XGO native-FCEUmm frontend prototype.
 *
 * This external image is linked with the HC15xx-compatible FCEUmm archive,
 * static newlib/libretro-common support, the XGO environment shim, and XGO
 * newlib syscall/sbrk glue.
 *
 * Entry contract:
 *   - loader has validated/placed this image at 0x87000000
 *   - filename is a Multicore-style fake GBA stub, e.g.
 *       .../fceumm;Super Mario Bros.nes.gba
 *   - the real ROM lives at
 *       /mnt/sda1/ROMS/fceumm/Super Mario Bros.nes
 *
 * Important memory rule:
 *   gp_buf_64m is the external newlib heap arena. The ROM MUST NOT be copied
 *   there before core initialization. Instead, the load-game wrapper allocates
 *   a temporary ROM buffer from that heap, invokes FCEUmm retro_load_game(),
 *   then frees it, matching maintained SF2000 Multicore behavior.
 *
 * This source does not touch SPI NOR or Firmware.upk.
 */

typedef unsigned int size_t;
typedef int bool;
#define true 1
#define false 0

#define MAXPATH 255u
#define MAX_ROM_SIZE 0x04000000u
#define RETRO_DEVICE_JOYPAD 1u
#define XGO_SYSTEM_NES 0x0001u

struct retro_game_info {
    const char *path;
    const void *data;
    size_t size;
    const char *meta;
};
struct retro_system_av_info;

typedef bool (*environment_cb)(unsigned, void *);
typedef void (*video_cb)(const void *, unsigned, unsigned, size_t);
typedef size_t (*audio_batch_cb)(const short *, size_t);
typedef void (*poll_cb)(void);
typedef short (*input_cb)(unsigned, unsigned, unsigned, unsigned);

/* Supplied by the statically linked FCEUmm archive. */
extern void retro_init(void);
extern void retro_deinit(void);
extern void retro_set_environment(environment_cb);
extern void retro_set_video_refresh(video_cb);
extern void retro_set_audio_sample_batch(audio_batch_cb);
extern void retro_set_input_poll(poll_cb);
extern void retro_set_input_state(input_cb);
extern void retro_set_controller_port_device(unsigned, unsigned);
extern void retro_get_system_av_info(struct retro_system_av_info *);
extern bool retro_load_game(const struct retro_game_info *);
extern void retro_unload_game(void);
extern void retro_run(void);
extern unsigned retro_get_region(void);

/* Supplied by external newlib. */
extern void *malloc(size_t);
extern void free(void *);

/* Supplied by xgo_minimal_environment_shim.c. */
extern bool xgo_minimal_environment(unsigned, void *);

#define STOCK_VIDEO ((video_cb)0x8035e70cu)
#define STOCK_AUDIO ((audio_batch_cb)0x8035e7d8u)
#define STOCK_POLL  ((poll_cb)0x8035ea30u)
#define STOCK_INPUT ((input_cb)0x8035eb20u)

#define FW_RUN_EMULATOR ((void (*)(int))0x8035ed48u)
#define FW_OS_DISABLE   ((void (*)(void))0x802e0750u)
#define FW_OS_ENABLE    ((void (*)(void))0x802e0778u)

/* XGO stock stdio wrappers. */
typedef struct FILE_ FILE;
#define FW_FOPEN  ((FILE *(*)(const char *, const char *))0x802b3524u)
#define FW_FREAD  ((size_t (*)(void *, size_t, size_t, FILE *))0x802b3698u)
#define FW_FSEEKO ((int (*)(FILE *, int, int))0x802b3804u)
#define FW_FTELL  ((int (*)(FILE *))0x802b3f1cu)
#define FW_FCLOSE ((int (*)(FILE *))0x802b2f40u)

#define GAME_INFO     (*(volatile struct retro_game_info *)0x80c2e914u)
#define RUN_FILE_SIZE (*(volatile unsigned *)0x80c33a7cu)
#define SYSTEM_FAMILY (*(volatile unsigned short *)0x80c33ad0u)

#define GFN_STATE_SAVE  (*(int (**)(const char *))0x80c33a70u)
#define GFN_GET_REGION  (*(unsigned (**)(void))0x80c33a9cu)
#define GFN_GET_AV      (*(void (**)(struct retro_system_av_info *))0x80c33aacu)
#define GFN_STATE_LOAD  (*(int (**)(const char *))0x80c33ac0u)
#define GFN_LOAD_GAME   (*(bool (**)(const struct retro_game_info *))0x80c33accu)
#define GFN_UNLOAD_GAME (*(void (**)(void))0x80c33ad4u)
#define GFN_FRAMESKIP   (*(void **)0x80c33ae0u)
#define GFN_RUN         (*(void (**)(void))0x80c33ae4u)

static char rom_path[MAXPATH + 1u];

static int disabled_state_io(const char *path)
{
    (void)path;
    return 0;
}

static int streq_n(const char *a, const char *b, unsigned n)
{
    unsigned i;
    for (i = 0; i < n; ++i) {
        if (a[i] != b[i])
            return 0;
        if (!a[i])
            return 1;
    }
    return 1;
}

/*
 * Convert the fake GBA dispatch token into the real first-core ROM path.
 * Accepted basename contract: fceumm;<real ROM filename>.gba
 * Only the final synthetic .gba suffix is removed.
 */
static int build_real_rom_path(const char *stub)
{
    static const char prefix[] = "/mnt/sda1/ROMS/fceumm/";
    const char *base = stub;
    const char *semi = 0;
    const char *p;
    unsigned i = 0;
    unsigned name_len;

    for (p = stub; *p; ++p) {
        if (*p == '/' || *p == '\\')
            base = p + 1;
        else if (*p == ';')
            semi = p;
    }

    if (!semi || semi < base)
        return 0;
    if ((unsigned)(semi - base) != 6u || !streq_n(base, "fceumm", 6u))
        return 0;

    p = semi + 1;
    name_len = 0;
    while (p[name_len])
        ++name_len;

    if (name_len <= 4u ||
        p[name_len - 4u] != '.' ||
        p[name_len - 3u] != 'g' ||
        p[name_len - 2u] != 'b' ||
        p[name_len - 1u] != 'a')
        return 0;
    name_len -= 4u;

    while (prefix[i]) {
        if (i >= MAXPATH)
            return 0;
        rom_path[i] = prefix[i];
        ++i;
    }
    if (i + name_len > MAXPATH)
        return 0;
    while (name_len--)
        rom_path[i++] = *p++;
    rom_path[i] = 0;
    return 1;
}

static int get_real_rom_size(unsigned *rom_size)
{
    FILE *f;
    int size;

    f = FW_FOPEN(rom_path, "rb");
    if (!f)
        return 0;
    if (FW_FSEEKO(f, 0, 2) != 0) {
        FW_FCLOSE(f);
        return 0;
    }
    size = FW_FTELL(f);
    FW_FCLOSE(f);

    if (size <= 0 || (unsigned)size > MAX_ROM_SIZE)
        return 0;
    *rom_size = (unsigned)size;
    return 1;
}

/*
 * FCEUmm does not require the ROM path to remain open. Maintained Multicore
 * loads non-fullpath cores into a temporary malloc() buffer, calls
 * retro_load_game(), then frees the buffer. Do the same here so gp_buf_64m can
 * remain exclusively the external newlib heap arena.
 */
static bool xgo_fceumm_load_game(const struct retro_game_info *info)
{
    FILE *f;
    int size;
    void *buffer;
    bool ok;
    struct retro_game_info tmp;

    if (!info || !info->path)
        return false;

    f = FW_FOPEN(info->path, "rb");
    if (!f)
        return false;
    if (FW_FSEEKO(f, 0, 2) != 0) {
        FW_FCLOSE(f);
        return false;
    }
    size = FW_FTELL(f);
    if (size <= 0 || (unsigned)size > MAX_ROM_SIZE ||
        FW_FSEEKO(f, 0, 0) != 0) {
        FW_FCLOSE(f);
        return false;
    }

    buffer = malloc((unsigned)size);
    if (!buffer) {
        FW_FCLOSE(f);
        return false;
    }

    if (FW_FREAD(buffer, 1, (unsigned)size, f) != (unsigned)size) {
        FW_FCLOSE(f);
        free(buffer);
        return false;
    }
    FW_FCLOSE(f);

    tmp.path = info->path;
    tmp.data = buffer;
    tmp.size = (unsigned)size;
    tmp.meta = 0;
    ok = retro_load_game(&tmp);
    free(buffer);
    return ok;
}

static void repair_irq_gp(void)
{
    volatile unsigned *src = (volatile unsigned *)0x80001270u;
    volatile unsigned *dst = (volatile unsigned *)0x80049744u;
    unsigned p;

    FW_OS_DISABLE();
    dst[0] = src[0];
    dst[1] = src[1];
    for (p = 0x80049740u; p < 0x80049750u; p += 16)
        __asm__ volatile("cache 1,0(%0); cache 1,0(%0)" : : "r"(p));
    __asm__ volatile("sync; nop; nop");
    for (p = 0x80049740u; p < 0x80049750u; p += 16)
        __asm__ volatile("cache 0,0(%0); cache 0,0(%0)" : : "r"(p));
    __asm__ volatile("nop; nop; nop; nop; nop");
    FW_OS_ENABLE();
}

#ifdef XGO_WITH_NEWLIB
#include <reent.h>
extern void __libc_init_array(void);
extern void __sinit(struct _reent *);
static void init_core_runtime(void)
{
    /* XGOC loader already zeroes file_size..memory_size, including .bss. */
    _REENT_INIT_PTR(_REENT);
    __sinit(_REENT);
    __libc_init_array();
}
#else
static void init_core_runtime(void) {}
#endif

__attribute__((section(".init.core_entry"), used))
int __core_entry__(const char *filename, int load_state)
{
    struct retro_game_info old_game_info;
    unsigned old_run_file_size;
    unsigned real_rom_size;
    unsigned short old_system_family;
    int (*old_state_save)(const char *);
    int (*old_state_load)(const char *);
    unsigned (*old_get_region)(void);
    void (*old_get_av)(struct retro_system_av_info *);
    bool (*old_load_game)(const struct retro_game_info *);
    void (*old_unload_game)(void);
    void (*old_run)(void);
    void *old_frameskip;

    init_core_runtime();

    /* Capture stock frontend state before changing any shared values. */
    old_game_info.path = GAME_INFO.path;
    old_game_info.data = GAME_INFO.data;
    old_game_info.size = GAME_INFO.size;
    old_game_info.meta = GAME_INFO.meta;
    old_run_file_size = RUN_FILE_SIZE;
    old_system_family = SYSTEM_FAMILY;
    old_state_save = GFN_STATE_SAVE;
    old_state_load = GFN_STATE_LOAD;
    old_get_region = GFN_GET_REGION;
    old_get_av = GFN_GET_AV;
    old_load_game = GFN_LOAD_GAME;
    old_unload_game = GFN_UNLOAD_GAME;
    old_run = GFN_RUN;
    old_frameskip = GFN_FRAMESKIP;

    if (!build_real_rom_path(filename) || !get_real_rom_size(&real_rom_size))
        return -1;

    repair_irq_gp();
    SYSTEM_FAMILY = XGO_SYSTEM_NES;
    RUN_FILE_SIZE = real_rom_size;

    retro_set_video_refresh(STOCK_VIDEO);
    retro_set_audio_sample_batch(STOCK_AUDIO);
    retro_set_input_poll(STOCK_POLL);
    retro_set_input_state(STOCK_INPUT);
    retro_set_environment(xgo_minimal_environment);
    retro_init();

    /* ROM data is loaded lazily by xgo_fceumm_load_game from this real path. */
    GAME_INFO.path = rom_path;
    GAME_INFO.data = 0;
    GAME_INFO.size = real_rom_size;
    GAME_INFO.meta = 0;

    GFN_STATE_LOAD = disabled_state_io;
    GFN_STATE_SAVE = disabled_state_io;
    GFN_GET_REGION = retro_get_region;
    GFN_GET_AV = retro_get_system_av_info;
    GFN_LOAD_GAME = xgo_fceumm_load_game;
    GFN_UNLOAD_GAME = retro_unload_game;
    GFN_RUN = retro_run;
    GFN_FRAMESKIP = 0;

    retro_set_controller_port_device(0, RETRO_DEVICE_JOYPAD);
    retro_set_controller_port_device(1, RETRO_DEVICE_JOYPAD);

    /* run_emulator() calls GFN_UNLOAD_GAME at 0x8035f284 on normal exit. */
    FW_RUN_EMULATOR(load_state);
    retro_deinit();

    /* Return the stock frontend to exactly the state we borrowed. */
    GFN_STATE_SAVE = old_state_save;
    GFN_STATE_LOAD = old_state_load;
    GFN_GET_REGION = old_get_region;
    GFN_GET_AV = old_get_av;
    GFN_LOAD_GAME = old_load_game;
    GFN_UNLOAD_GAME = old_unload_game;
    GFN_RUN = old_run;
    GFN_FRAMESKIP = old_frameskip;
    SYSTEM_FAMILY = old_system_family;
    RUN_FILE_SIZE = old_run_file_size;
    GAME_INFO.path = old_game_info.path;
    GAME_INFO.data = old_game_info.data;
    GAME_INFO.size = old_game_info.size;
    GAME_INFO.meta = old_game_info.meta;

    return 0;
}
