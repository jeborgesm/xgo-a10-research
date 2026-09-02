# XGO external-core memory, link contract, and native emulator dispatch

Status: **critical first-real-core architecture confirmed from XGO disassembly and current SF2000 Multicore source**.

Firmware fingerprint used throughout:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

## Important correction: the GBA interception point precedes ROM loading

The confirmed XGO GBA redirect site is the `jal run_gba` instruction at ASD/runtime offset/address:

- file offset `0x00360cf4`
- runtime `0x80360cf4`
- stock target `run_gba = 0x80360110`
- original instruction word `0x0c0d8044` (`44 80 0d 0c` little endian)

This call occurs in `run_game()` before `run_gba()` itself has loaded content into the stock 64-MiB ROM buffer. Therefore the synthetic external-code probe was valid because it did not need ROM data, but a real libretro emulator must **not** assume `gp_buf_64m` and `g_run_file_size` already contain the selected ROM when entered through this hook.

A real external frontend must open/read/decompress content itself before calling the core's `retro_load_game()`, matching the architecture used by maintained SF2000 Multicore.

## XGO really allocates the stock 64-MiB scratch arena

XGO function `0x8035e54c` clears related state and then performs:

```text
0x8035e570  lui  $a0,0x0400       ; 0x04000000 = 64 MiB
0x8035e578  jal  0x80291c04       ; stock malloc
...
0x8035e5ac  sw   $v0,-0xc9c($gp)
```

With the confirmed XGO stock GP `0x80c34774`, `gp-0xc9c` is:

```text
0x80c33ad8 = gp_buf_64m
```

The adjacent format string at `0x809a3934` is:

```text
ROM_MEM_BUFFER = 0x%X, ROM_MEM_BUFFER_SIZE = %dM
```

Thus the 64-MiB scratch buffer is an active XGO allocation, not an inherited dead symbol.

## Maintained Multicore uses that arena as the external core's private libc heap

Current SF2000 Multicore links each external core image at `0x87000000` with its own static libc (`-lc`) and libretro-common. Its frontend `lib.c` supplies a private `sbrk()` whose first heap pointer is `gp_buf_64m` and whose end is `gp_buf_64m + 0x04000000`.

Therefore external cores do not need to import the stock firmware's `malloc/free` implementation. They need only the small stock service surface used by Multicore's newlib/VFS glue (`fs_*`, tick functions, selected frontend callbacks/globals, etc.).

Maintained loader sequence is conceptually:

```text
stock firmware has already allocated gp_buf_64m
        -> lower RAMSIZE to 0x87000000
        -> load external core image at 0x87000000
        -> repair IRQ-path $gp
        -> initialize core-local libc
        -> external newlib heap grows in gp_buf_64m arena
        -> external frontend opens/loads selected ROM
        -> stock XGO run_emulator() drives core callbacks
```

This substantially reduces the firmware symbol-mapping requirement. The existing XGO linker map already covers the essential filesystem, scheduler, video/audio/input callbacks, run loop, WQW helpers, heap ceiling, game-info, state-function pointers, and two-player state required by a stripped first core.

The extra symbols in the full maintained SF2000 Multicore linker overlay are predominantly enhanced-frontend features (FPS display, framebuffer-preview state, FrogUI/pause-menu hooks, current-game display buffers, OSD scratch globals, and UART-less LCD debug pins). They are not fundamental to a first FCEUmm boot.

## IRQ GP repair is fundamental; pause-menu patching is optional for first boot

The current Multicore core entry copies the firmware's own GP initialization instructions:

```text
0x80001270 -> 0x80049744
0x80001274 -> 0x80049748
```

and flushes the instruction cache before enabling interrupts again.

These exact XGO addresses were independently confirmed earlier. This repair should be retained for a real external core.

Current upstream Multicore also patches the stock pause-menu call so that its richer save-state/FrogUI behavior can run. That patch is useful later, but it is **not required** for the first emulator execution proof. A minimal XGO FCEUmm bring-up can retain stock menu behavior with stubbed/controlled state handlers and defer the enhanced pause-menu hook.

## Native per-system interception points

The XGO `run_game()` dispatcher contains clean, independent calls to each stock emulator runner. All receive the original filename in `$a0` and `load_state = 0` in `$a1`.

Confirmed sites:

| Family | system ID | call site | stock runner | original instruction bytes |
|---|---:|---:|---:|---|
| GBA | `0x10` | `0x80360cf4` | `0x80360110` | `44 80 0d 0c` |
| GB/GBC | `0x20` | `0x80360e10` | `0x803604ac` | `2b 81 0d 0c` |
| NES | `0x01` | `0x80360e20` | `0x8035f63c` | `8f 7d 0d 0c` |
| Sega | `0x04` | `0x80360e30` | `0x8035fd74` | `5d 7f 0d 0c` |
| SNES | `0x08` | `0x80360e40` | `0x8035f9d8` | `76 7e 0d 0c` |

This is a major design result: Multicore does not have to remain a GBA-stub workaround on XGO.

A future patcher can redirect a specific system family directly from the stock main-list dispatcher. For example, replacing only the NES call at `0x80360e20` would allow curated/main-list NES entries to launch FCEUmm directly while GBA, GB, Sega and SNES remain completely stock.

Because the sites are independent, emulator replacement can be staged one family at a time and guarded by exact original instruction signatures.

## Consequence for the long-term XGO PC configurator

The firmware patching model can expose a per-system core policy rather than one global Multicore switch:

```text
NES      -> stock | FCEUmm | other core
SNES     -> stock | external core
Sega     -> stock | external core
GBA      -> stock | external core
GB/GBC   -> stock | external core
```

Combined with the already-reconstructed main-list databases, Zxx packaging, and `.kmp` keymaps, this provides a path to launching improved emulators from the normal curated UI instead of requiring Setup -> User Games or fake `.gba` stubs.

## Confidence

**CONFIRMED:** exact XGO 64-MiB scratch allocation and `gp_buf_64m` global.

**CONFIRMED:** GBA interception occurs before stock ROM loading.

**CONFIRMED:** exact native emulator call sites and original opcodes for GBA, GB/GBC, NES, Sega, and SNES.

**CONFIRMED from maintained Multicore source:** external image is linked at `0x87000000`, carries static libc, uses `gp_buf_64m` for private `sbrk`, lowers `RAMSIZE`, repairs IRQ `$gp`, and loads content itself.

**STRONG design conclusion:** first XGO FCEUmm should use a stripped external frontend plus the native NES dispatcher call rather than making the GBA-stub mechanism the permanent integration path.
