# Minimal XGO external-core link contract

Status: **first-core stock-firmware dependency surface substantially closed**.

## Purpose

The maintained SF2000 Multicore project links each emulator core at `0x87000000` from four layers:

1. a libretro emulator static archive,
2. the Multicore frontend wrapper,
3. libretro-common / static C runtime support,
4. a linker symbol file binding selected calls and globals back into the stock firmware.

For XGO, the first bring-up deliberately strips this to the smallest useful stock-firmware interface instead of porting every SF2000 convenience feature.

## Upstream reference build

The maintained SF2000 Multicore Makefile builds a core as:

```text
libretro_core.a
+ libretro-common.a
+ frontend wrapper objects
+ -lc
+ core.ld @ 0x87000000
+ stock-firmware symbol linker script
```

The resulting ELF is objcopied into a raw `core_87000000` image.

The generic core linker script places `__core_entry__` first at `0x87000000`, then `.text`, `.rodata`, `.data`, GOT/small-data, and BSS.

## XGO first-core stock imports

The minimal XGO FCEUmm path needs only stock facilities that have already been mapped and semantically verified:

```text
fopen                         0x802b3524
fw_fread                      0x802b3698
fclose                        0x802b2f40

dly_tsk                       0x8030f480
run_emulator                  0x8035ed48
run_gba                       0x80360110

retro_video_refresh_cb        0x8035e70c
retro_audio_sample_batch_cb   0x8035e7d8
retro_input_poll_cb           0x8035ea30
retro_input_state_cb          0x8035eb20
retro_environment_cb          0x8035eb64

RAMSIZE                       0x80c2ce6c
XGO_HEAP_BREAK                0x80c337b0
g_snd_task_flags              0x80c2e80c
g_retro_game_info             0x80c2e914

gfn_state_save                0x80c33a70
g_run_file_size               0x80c33a7c
gfn_retro_get_region          0x80c33a9c
gfn_get_system_av_info        0x80c33aac
gfn_state_load                0x80c33ac0
gfn_retro_load_game           0x80c33acc
gfn_retro_unload_game         0x80c33ad4
gp_buf_64m                    0x80c33ad8
gfn_frameskip                 0x80c33ae0
gfn_retro_run                 0x80c33ae4

active system-family word     0x80c33ad0
region selector               0x80c2e878
```

The external environment shim adds no board-driver dependency. It normalizes region spelling, advertises a 44.1-kHz target sample rate, accepts only RGB565, advertises frame duping, supplies system/save directories, and rejects unsupported frontend rotation.

## Deliberately excluded for first boot

The following upstream SF2000 Multicore imports are **not required** for the minimal XGO FCEUmm bring-up:

```text
run_emulator_menu
jal_run_emulator_menu
firmware FPS globals
preview-size / preview-dimension globals
FrogUI run-game filename/name/folder buffers
raw OSD framebuffer globals
direct ST7789V helpers
direct VPO / OSD driver helpers
UARTless LCD-pin debug GPIO symbols
```

Those support richer Multicore features such as FrogUI integration, save-state thumbnails, FPS overlays, direct scaler control, XRGB8888 conversion, debug output, and patched pause-menu behavior. They can be mapped later without blocking the first emulator launch.

## Remaining linker uncertainty

The remaining unknown surface is no longer XGO-specific hardware. It is conventional static runtime support used by the emulator/frontend build:

```text
newlib / libc
libm
libretro-common
possible external zlib symbols
compiler runtime helpers
```

The maintained HC15xx FCEUmm fork already has a `platform=sf2000` target using MIPS32 little-endian soft-float, `-G0`, `-mno-abicalls`, `-fno-pic`, static linking, and external-zlib mode. Therefore emulator ISA/ABI portability is already demonstrated on the same SoC family.

The next definitive step is to build the pinned HC15xx FCEUmm archive with the maintained frog/MTI toolchain and link it against the stripped XGO wrapper. Any unresolved symbols from that link become the authoritative remaining blocker list.

## Conclusion

For first-core bring-up, there is currently **no known unresolved XGO board-support dependency**. The research has moved from reverse-engineering hardware interfaces to completing an ordinary static MIPS link environment.
