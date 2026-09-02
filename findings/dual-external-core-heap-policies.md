# Dual XGO external-core heap policies

Status: **confirmed from XGO `run_game()` disassembly and maintained SF2000 Multicore allocator behavior**.

Firmware SHA-256:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

## Why two allocators are required

XGO does not prepare content the same way for every emulator family before it calls the family runner.

### GBA branch: no ROM preload

At `run_game = 0x80360b88`, system family `0x10` branches directly to the GBA runner:

```text
0x80360c08  compare family with 0x10
...
0x80360ce4  GBA-specific setup
0x80360cf0  move a0, filename
0x80360cf4  jal  0x80360110   ; run_gba
0x80360cf8  move a1, zero
```

The common file-open/read block is skipped.

Therefore a Multicore-style fake-GBA interception reaches the external loader before the selected real ROM exists in `gp_buf_64m`.

For this path the complete stock 64-MiB scratch arena can be used as the external newlib heap. The external frontend reconstructs the real ROM path and loads the ROM later into a temporary `malloc()` buffer for `retro_load_game()`.

Implementation:

`tools/multicore/xgo_full_arena_sbrk.c`

### NES / Sega / SNES / GB-GBC branches: ROM is preloaded

For non-GBA normal cartridge families, `run_game()` first executes the common load block:

```text
0x80360c18  fopen(filename)
0x80360c38  fseeko(..., SEEK_END)
0x80360c40  ftell(...)
0x80360c54  store g_run_file_size
0x80360c64  load gp_buf_64m
0x80360c80  fw_fread(gp_buf_64m, 1, aligned_size, file)
0x80360c88  fclose(...)
```

Only after that preload does it dispatch:

```text
GB/GBC  0x80360e10 -> 0x803604ac
NES     0x80360e20 -> 0x8035f63c
Sega    0x80360e30 -> 0x8035fd74
SNES    0x80360e40 -> 0x8035f9d8
```

Therefore a future **native NES interception** at `0x80360e20` receives a scratch arena whose prefix already contains the selected ROM.

For that path newlib must start its heap after the aligned preloaded ROM extent instead of at `gp_buf_64m` itself.

Implementation:

`tools/multicore/xgo_preloaded_rom_sbrk.c`

## The collision caught during FCEUmm bring-up

An intermediate bridge revision combined these two models incorrectly:

```text
gp_buf_64m = real NES ROM bytes
           = external newlib sbrk() base
```

That means the first external `malloc()` could overwrite ROM bytes and create nondeterministic emulator failures.

The GBA-stub bridge was corrected to stop preloading the real NES ROM. It now:

1. reconstructs `/mnt/sda1/ROMS/fceumm/<real filename>`,
2. leaves `gp_buf_64m` entirely available to the external heap,
3. installs `xgo_fceumm_load_game()` as the stock `GFN_LOAD_GAME` callback,
4. allocates a temporary ROM buffer from external newlib,
5. calls FCEUmm `retro_load_game()` with that temporary buffer,
6. frees it after the call, matching maintained Multicore behavior.

## Consequence

The allocator must be selected by **dispatch architecture**, not merely emulator family:

```text
fake-GBA / self-loading external path
    -> xgo_full_arena_sbrk.c

native preloaded NES/Sega/SNES/GB path
    -> xgo_preloaded_rom_sbrk.c
```

Linking the wrong allocator is a correctness bug, not an optimization difference.

## Additional teardown confirmation

`run_emulator()` itself invokes the currently installed unload callback on normal exit:

```text
0x8035f284  lw   $17,-0xca0($gp)
0x8035f288  jalr $17
```

With XGO stock `$gp = 0x80c34774`, `gp-0xca0 = 0x80c33ad4`, exactly `GFN_UNLOAD_GAME`.

Therefore the external bridge should let stock `run_emulator()` call `retro_unload_game()`, then call `retro_deinit()` after `run_emulator()` returns. It should not call `retro_unload_game()` a second time.

## Confidence

**CONFIRMED:** GBA bypasses the common ROM preload block.

**CONFIRMED:** NES/Sega/SNES/GB-GBC pass through the common `gp_buf_64m` preload block before their runner call.

**CONFIRMED:** maintained Multicore uses `gp_buf_64m` as its private external newlib heap base.

**CONFIRMED:** XGO `run_emulator()` calls `GFN_UNLOAD_GAME` itself before returning.

**CORRECTED DESIGN:** GBA-stub FCEUmm uses the whole scratch arena as heap and loads ROM data temporarily; future native interception preserves the preloaded ROM prefix and begins the heap afterward.
