# XGO external-core memory, link contract, and native emulator dispatch

Status: **critical first-real-core architecture confirmed from XGO machine code and current SF2000 Multicore source**.

Firmware fingerprint used throughout:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

## Important correction: GBA and native NES cross different preload boundaries

The confirmed XGO GBA redirect site is the `jal run_gba` instruction at ASD/runtime offset/address:

- file offset `0x00360cf4`
- runtime `0x80360cf4`
- stock target `run_gba = 0x80360110`
- original instruction word `0x0c0d8044` (`44 80 0d 0c` little endian)

This GBA call occurs before the common `run_game()` ROM-preload block. Therefore the synthetic semicolon/GBA external-code probe was valid because it did not need ROM data, but a real core entered through that hook must open/load its selected ROM itself, matching the original maintained SF2000 Multicore architecture.

The native NES call is different. Direct disassembly of the preserved XGO `bisrv.asd` confirms that non-GBA families pass through a common preload block before the per-system dispatch.

For an ordinary NES launch, `run_game()` performs, in order:

```text
open(real selected filename, "rb")
seek end
tell size
store g_run_file_size
seek start
load gp_buf_64m
round size upward to four bytes
fread(gp_buf_64m, 1, aligned_size, file)
close(file)
dispatch on system family
```

The relevant machine-code sequence loads the filename held in `$s2`, calls stock `fopen` (`0x802b3524`), obtains the file size, stores it at `gp-0xcf8`, loads `gp_buf_64m` from `gp-0xc9c`, aligns the size, calls stock `fread` (`0x802b3698`), and closes the file before reaching the family branches.

At the NES branch, the call contract is then:

```text
move  $a0,$s2       # original real NES filename
jal   0x8035f63c    # stock run_nes
move  $a1,$zero     # load_state = 0 (delay slot)
```

The native patch at `0x80360e20` replaces only this JAL, so the 924-byte native loader inherits the exact same `$a0/$a1` arguments **after the ROM has already been preloaded**.

Inspection of stock `run_nes()` independently confirms the other side of the contract. Its normal execution path does not open/read the ROM. It saves the filename/load-state arguments, installs the NES/libretro callbacks, reads the already-populated run-file-size and `gp_buf_64m` globals into the stock game-info structure, and transfers control to `run_emulator()`.

Therefore the native FCEUmm frontend is correct to consume the preloaded ROM directly and to start its private newlib heap after the aligned ROM prefix. This is now a machine-code-confirmed XGO contract, not an extrapolation from SF2000.

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

For the original semicolon/GBA Multicore path, maintained loader sequence is conceptually:

```text
stock firmware has allocated gp_buf_64m
        -> lower RAMSIZE to 0x87000000
        -> load external core image at 0x87000000
        -> repair IRQ-path $gp
        -> initialize core-local libc
        -> external newlib heap grows in gp_buf_64m arena
        -> external frontend opens/loads selected ROM
        -> stock run_emulator() drives core callbacks
```

For XGO's native NES interception, the confirmed stock common preload lets us improve that contract:

```text
stock run_game() preloads NES into gp_buf_64m
        -> patched NES JAL enters external loader
        -> lower RAMSIZE / validate and load core at 0x87000000
        -> repair IRQ-path $gp / flush caches
        -> initialize core-local libc
        -> private sbrk begins after aligned preloaded-ROM prefix
        -> FCEUmm receives gp_buf_64m directly with no second ROM copy
        -> stock run_emulator() drives core callbacks
```

This substantially reduces both the firmware symbol-mapping requirement and first-boot memory pressure. The existing XGO linker map already covers the essential filesystem, scheduler, video/audio/input callbacks, run loop, WQW helpers, heap ceiling, game-info, state-function pointers, and two-player state required by a stripped first core.

The extra symbols in the full maintained SF2000 Multicore linker overlay are predominantly enhanced-frontend features (FPS display, framebuffer-preview state, FrogUI/pause-menu hooks, current-game display buffers, OSD scratch globals, and UART-less LCD debug pins). They are not fundamental to a first FCEUmm boot.

## IRQ GP repair is fundamental; pause-menu patching is optional for first boot

The current/newer Multicore strategy copies the firmware's own GP initialization instructions into the IRQ path. XGO's exact startup pair is already confirmed as:

```text
0x80001270  lui   $gp,0x80c3
0x80001274  addiu $gp,$gp,0x4774
```

The native loader copies those two instruction words to:

```text
0x80049744
0x80049748
```

with interrupts disabled, performs D/I cache maintenance, and only then re-enables interrupts. This is the same IRQ site and same underlying strategy used by maintained SF2000 Multicore to prevent an interrupt from entering stock code with an external/dynarec `$gp` value.

Current upstream Multicore also patches the stock pause-menu call so that its richer save-state/FrogUI behavior can run. That patch is useful later, but it is **not required** for the first emulator execution proof. A minimal XGO FCEUmm bring-up can retain stock menu behavior with stubbed/controlled state handlers and defer the enhanced pause-menu hook.

## Native per-system interception points

The XGO `run_game()` dispatcher contains clean, independent calls to each stock emulator runner. They receive the original filename in `$a0` and `load_state = 0` in `$a1`. For NES/GB/Sega/SNES, the common ROM preload has already completed before these calls. GBA is a special path and branches to `run_gba()` before that common preload block.

Confirmed sites:

| Family | system ID | call site | stock runner | original instruction bytes |
|---|---:|---:|---:|---|
| GBA | `0x10` | `0x80360cf4` | `0x80360110` | `44 80 0d 0c` |
| GB/GBC | `0x20` | `0x80360e10` | `0x803604ac` | `2b 81 0d 0c` |
| NES | `0x01` | `0x80360e20` | `0x8035f63c` | `8f 7d 0d 0c` |
| Sega | `0x04` | `0x80360e30` | `0x8035fd74` | `5d 7f 0d 0c` |
| SNES | `0x08` | `0x80360e40` | `0x8035f9d8` | `76 7e 0d 0c` |

This is a major design result: Multicore does not have to remain a GBA-stub workaround on XGO.

A patcher can redirect a specific system family directly from the stock main-list dispatcher. Replacing only the NES call at `0x80360e20` allows normal main-list NES entries to launch FCEUmm directly while GBA, GB, Sega and SNES remain completely stock.

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

**CONFIRMED:** GBA interception occurs before the common `run_game()` ROM preload.

**CONFIRMED from direct XGO machine code:** NES/GB/Sega/SNES common-path ROM preload occurs before their native runner JALs; the NES JAL receives the original filename in `$a0` and zero load-state in `$a1`.

**CONFIRMED from direct XGO `run_nes()` machine code:** stock NES consumes the already-populated `gp_buf_64m` and run-file-size globals rather than reopening the ROM on its normal runner path.

**CONFIRMED:** exact native emulator call sites and original opcodes for GBA, GB/GBC, NES, Sega, and SNES.

**CONFIRMED from maintained Multicore source:** external image is linked at `0x87000000`, carries static libc, uses `gp_buf_64m` for private `sbrk`, lowers `RAMSIZE`, and repairs IRQ `$gp`.

**CONFIRMED design consequence:** native NES interception can preserve the stock preload and start the external private heap after that ROM prefix, eliminating a second ROM load/copy.
