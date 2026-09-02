# XGO external-core `$gp` ABI is bidirectional

Status: **confirmed from preserved XGO machine code and exact Codescape final-link disassembly; incorporated into the native FCEUmm path. Physical execution remains untested.**

## Finding

An XGO external core cannot treat `$gp` as a one-time entry concern.

There are two simultaneously valid global-pointer domains while a native external core is running:

```text
stock XGO firmware $gp = 0x80c34774
external FCEUmm _gp    = linker-defined inside the 0x87000000 image
```

For the production build recorded below, external `_gp` is `0x8718f450`.

Code must therefore switch `$gp` in **both directions** at every firmware/core boundary:

```text
stock run_game / loader
        |
        | stock gp = 0x80c34774
        v
__core_entry__ veneer
        |
        | gp := external _gp
        v
FCEUmm / newlib / native frontend
        |
        | core -> stock veneer: gp := 0x80c34774
        v
stock callback / stdio / VFS / run_emulator
        |
        | stock -> core veneer: gp := external _gp
        v
external retro_* function
```

This is a required ABI bridge, not a defensive optimization.

## Why the original linked image was unsafe

The native FCEUmm image is linked with `-nostartfiles`. No crt0 runs before the external entry.

The linker script intentionally defines the external global pointer:

```text
_gp = ALIGN(16) + 0x7ff0
```

The earlier C `__core_entry__` therefore began executing while `$gp` still held the stock XGO value inherited from the loader. Final ELF disassembly showed reachable external code using GP-relative accesses, so a successful static link with zero undefined symbols did not guarantee valid execution.

`tools/multicore/native_nes/xgo_core_entry.s` now owns the true entry at `0x87000000`. It saves the incoming stock `$gp`, establishes linker `_gp`, calls `__core_entry_c`, and restores the stock value before returning.

## Stock firmware functions also require stock `$gp`

Direct disassembly of the preserved XGO `bisrv.asd` shows stock firmware services using GP-relative globals without reconstructing `$gp` on entry.

Representative confirmed cases include:

- `retro_video_refresh_cb @ 0x8035e70c` — GP-relative access by `0x8035e73c`;
- `retro_audio_sample_batch_cb @ 0x8035e7d8` — GP-relative access by `0x8035e81c`;
- `retro_input_state_cb @ 0x8035eb20` — GP-relative access by `0x8035eb34`;
- `retro_environment_cb @ 0x8035eb64` — GP-relative access by `0x8035ebdc`;
- stock `fseeko`, `ftell`, and `fclose` use GP-relative state;
- `os_get_tick_count @ 0x8030fec8` reads the tick counter directly through `$gp`.

Consequently, once external C is running under its own `_gp`, a direct call to one of these stock addresses is invalid. The caller must temporarily install `0x80c34774`.

## `run_emulator()` proves the reverse transition is required

Stock `run_emulator @ 0x8035ed48` executes under the firmware GP and obtains its active-core callbacks through GP-relative global slots before indirect `jalr` calls.

Confirmed slot relationships are:

```text
gp - 3240 = 0x80c33acc = gfn_retro_load_game
gp - 3272 = 0x80c33aac = gfn_get_system_av_info
gp - 3288 = 0x80c33a9c = gfn_retro_get_region
gp - 3216 = 0x80c33ae4 = gfn_retro_run
gp - 3232 = 0x80c33ad4 = gfn_retro_unload_game
```

Therefore stock `run_emulator()` reaches external FCEUmm functions while the **stock** GP is active. Those function-pointer targets also require a veneer that restores the external image `_gp` before entering FCEUmm.

## Implemented bridge

`tools/multicore/native_nes/xgo_gp_bridges.s` provides two families of signature-transparent O32 veneers.

### Core -> stock

The reachable production surface currently includes veneers for:

- stock stdio used to recover exact ROM size;
- ALi VFS functions needed by external newlib/libretro-common;
- scheduler/time services;
- video/audio/input/environment callbacks;
- stock `run_emulator()`.

Each veneer:

1. allocates a 32-byte O32 frame;
2. saves `$ra` and external `$gp`;
3. installs `0x80c34774`;
4. calls the stock firmware target;
5. restores external `$gp` and `$ra`;
6. returns with `v0/v1` untouched.

### Stock -> core

The reverse veneers cover the functions installed into stock `run_emulator()` indirection slots:

- `retro_get_region`;
- `retro_get_system_av_info`;
- `retro_load_game`;
- `retro_unload_game`;
- `retro_run`;
- disabled state I/O.

They save stock `$gp`, install linker `_gp`, invoke the external function, then restore stock `$gp` before returning to `run_emulator()`.

Each veneer occupies a separate `.text.<name>` section. `--gc-sections` can therefore discard unused bridge functions and the reachable-runtime audits do not inherit the whole bridge surface merely because one veneer is used.

## O32 stack-argument exception: `fs_lseek`

A generic veneer is transparent only while all argument words fit in `a0-a3`.

The recovered ALi `fs_lseek` ABI is:

```c
int64_t fs_lseek(int fd, int64_t offset, int whence);
```

Under O32, the 64-bit argument is aligned into `a2/a3`; `whence` is the fifth argument word at caller `sp+16`.

Because a normal GP veneer moves `$sp` by 32 bytes, `fs_lseek` has a dedicated five-word veneer. It copies:

```text
old sp + 16  == new sp + 48
                       |
                       v
               new sp + 16
```

before calling stock firmware.

The exact production disassembly confirms this sequence:

```text
87000270 <xgo_stock_fs_lseek>:
  addiu sp,sp,-32
  sw    ra,28(sp)
  sw    gp,24(sp)
  lw    t0,48(sp)
  sw    t0,16(sp)
  lui   gp,0x80c3
  addiu gp,gp,18292       # 0x4774 -> 0x80c34774
  jal   0x802ac394        # stock fs_lseek
  nop
  lw    gp,24(sp)
  ...
```

## Exact production evidence

Workflow: `XGO native FCEUmm full link`

Run: `33654506801`

Source commit: `47d217d84976bbf59f8f5dd6e11daa9f2e235639`

Result: **success**.

The workflow verifies final machine code, not only source intent. It confirms that the external entry and reverse core veneers reconstruct linked `_gp`, and representative stock veneers reconstruct `0x80c34774` and restore the caller GP afterward.

Production layout from the successful artifact:

```text
image_start       0x87000000
entry             0x87000000
C entry           0x87000550
external _gp      0x8718f450
file_end          0x87187470
payload_size      1,602,672 bytes
bss_start         0x87187470
image_end         0x873b2508
memory_size       3,876,104 bytes
reserved_size    13,479,424 bytes
headroom           9,603,320 bytes
```

Entry machine code:

```text
87000000 <__core_entry__>:
  addiu sp,sp,-32
  sw    ra,28(sp)
  sw    gp,24(sp)
  lui   gp,0x8719
  addiu gp,gp,-2992       # 0x8718f450
  jal   0x87000550        # __core_entry_c
  nop
  lw    gp,24(sp)
  lw    ra,28(sp)
  addiu sp,sp,32
  jr    ra
  nop
```

Representative core -> stock bridge:

```text
87000308 <xgo_stock_video_refresh>:
  ...
  lui   gp,0x80c3
  addiu gp,gp,18292       # 0x80c34774
  jal   0x8035e70c
  ...
  lw    gp,24(sp)
```

Representative stock -> core bridge:

```text
870004e8 <xgo_core_run>:
  ...
  lui   gp,0x8719
  addiu gp,gp,-2992       # 0x8718f450
  jal   0x87004978        # retro_run
  ...
  lw    gp,24(sp)
```

Output SHA-256 values:

```text
xgo-native-fceumm.elf
177e34b4c195543422ae5987691ceee8ab5293ebdee4f6b78906601b13f7e9f8

xgo-native-fceumm.bin
170c7ab82f9717cb985f9e5415a4f2ef194244468ce14a5e942a130c3051bf36

core-native-nes.xgc
32cc83f733954020361259badee0592af9c223d1dab1b7aa30a7d7c585d8625f
```

## Consequence for earlier link experiments

The earlier generic/semicolon FCEUmm link lab remains useful evidence that archive/runtime closure was feasible, but its original direct stock-call model is **not a hardware-safe ABI**. A zero-undefined-symbol ELF can still be wrong when caller/callee disagree about `$gp`.

The native NES production path and its bidirectional GP veneers are now authoritative for device testing.

## Remaining boundary

This finding removes the last known static `$gp` mismatch in the normal native NES call graph. It does not prove physical execution. The remaining high-value unknowns are now device observations: upper-RAM loading under live firmware, cache/IRQ behavior with the full payload, first FCEUmm frame/audio/input, and return behavior on actual XGO hardware.
