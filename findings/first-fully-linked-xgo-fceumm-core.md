# First fully linked XGO FCEUmm external core

Status: **offline build/link/container path confirmed; physical XGO execution not yet tested**.

## Milestone

The XGO external-core research has reached the first complete emulator image rather than a synthetic transport probe.

GitHub Actions run **#29** (`33586812526`) successfully performed the entire build chain:

1. installed the exact Codescape MIPS MTI bare-metal toolchain,
2. checked out the pinned HC15xx FCEUmm source,
3. built the SF2000/HC15xx-compatible FCEUmm static archive,
4. built the XGO compatibility/runtime support layer,
5. fully linked an XGO executable at `0x87000000`,
6. verified **zero undefined symbols**,
7. verified the complete runtime image fits the reserved XGO RAM window,
8. extracted the file-backed binary,
9. packed it as an XGOC v1 `core.xgc`,
10. independently revalidated the XGOC header/bounds/CRCs.

This proves the first real emulator core is buildable against the reconstructed XGO firmware ABI. It does **not** yet prove successful execution on physical hardware.

## Exact source and toolchain

FCEUmm source:

```text
repository  madcock/libretro-fceumm
commit      e6111e684e7a7761f3f1d6c80d0a825e2c8cdc7e
```

The pinned revision is the HC15xx-oriented snapshot whose commit introduces the `platform=sf2000` target.

Codescape toolchain:

```text
mips-mti-elf-gcc (GCC) 7.4.0
package: Codescape GNU Tools 2019.09-03-2, MIPS32 MTI bare metal
archive SHA-256:
d35717f24a67ed2091c32d9fb3d79dc5ebe84c38ac8872736aa018860a724807
```

Core compile ABI remains:

```text
-EL
-march=mips32
-mtune=mips32
-msoft-float
-G0
-mno-abicalls
-fno-pic
-ffast-math
-fomit-frame-pointer
-ffunction-sections
-fdata-sections
-O2
-DNDEBUG
-DSF2000
```

## Link result

The production link combines:

```text
xgo_fceumm_entry.o
xgo_minimal_environment_shim.o
fceumm_libretro_sf2000.a
xgo_fceumm_support.a
Codescape libc
Codescape libm
libgcc
xgo_external_core.ld
xgo_stockfw_symbols.ld
```

The final `mips-mti-elf-nm -u xgo-fceumm.elf` output is empty:

```text
undefined symbols = 0
```

The earlier archive-level progression remains useful context:

```text
FCEUmm true external symbols             81
After XGO support layer                  67
After XGO firmware + libc/libm/libgcc     0
Fully linked executable                   0
```

## Final memory layout

Normalized low-32-bit addresses from the final ELF are:

```text
__image_start  0x87000000
__start        0x87000098
__file_end     0x8717ebe0
__bss_start    0x8717ebe0
__image_end    0x873a9e10
```

Derived sizes:

```text
entry offset       0x98
file-backed span   1,567,712 bytes = 0x17ebe0
payload size       1,567,712 bytes = 0x17ebe0
runtime memory     3,841,552 bytes = 0x3a9e10
zero/BSS tail      2,273,840 bytes
reserved window   13,479,424 bytes = 0xcdae00
remaining headroom 9,637,872 bytes = 0x930ff0
```

Thus FCEUmm occupies only about 28.5% of the currently reserved external-core window `0x87000000..0x87cdae00`.

The file-backed payload ends exactly where the linker declares `__file_end`; no hidden gap or accidental runtime-only section is being serialized into the XGOC payload.

## XGOC result

The XGOC packer generated and the independent inspector accepted:

```text
magic         XGOC
version       1
load          0x87000000
entry         0x87000098
payload       1,567,712 bytes
runtime       3,841,552 bytes
zero tail     2,273,840 bytes
payload CRC   0xbb16f3f9
header CRC    0xf58d1a1f
```

Output hashes for run #29:

```text
xgo-fceumm.elf
71987ec44db1111bd8248a8e4951fd3cd996d4f86410d98e4c1b381b86d29031

xgo-fceumm.bin
dbda26a7518a6627ae282821d6ef0b40ba39712135b67607db131592e33c4756

core.xgc
e421f3a0b1f087dbb96ea57d41fb01f28816ec13963d61e24fb6082a2eb010e6
```

The complete Actions artifact ZIP has digest:

```text
3edfc917721265ddea2dafdfbb40ab5c643aed95004853629968ca5db93e31a9
```

## Binary-startup audit

The generated ELF was independently inspected after the successful link.

### Entry point

`__start` is real executable code at:

```text
0x87000098
```

which matches XGOC `entry_offset=0x98`.

### GP dependency

A complete disassembly search of the linked ELF found **no `$gp` references**.

This is consistent with the `-G0 -mno-abicalls -fno-pic` build and substantially reduces external-core GP-state risk for FCEUmm itself. The stock IRQ GP-repair patch remains desirable as a general Multicore safety measure, especially for future cores/dynarecs, but this particular linked FCEUmm image is not relying on `$gp` for ordinary code/data access.

### Constructors

The ELF contains no output sections named:

```text
.init_array
.fini_array
.ctors
.dtors
```

Therefore the first FCEUmm image has no discovered constructor/destructor startup obligation that the custom `__start` bridge is failing to execute.

### BSS

The final section layout places:

```text
.sbss  0x8717ebe0 ...
.bss   0x8717ebf0 ...
```

behind the 1,567,712-byte file payload. The XGOC loader's declared `memory_size=3,841,552` causes the complete runtime-only tail to be zeroed before entry.

This directly closes the BSS problem identified during the raw-probe audit.

## XGO execution bridge

The core is statically linked, so unlike upstream Multicore it does not require a runtime `retro_core_t` API table.

The XGO `__start(stub_path, load_state)` bridge:

- only accepts an intercepted component named exactly `fceumm`,
- converts a launch stub such as `fceumm;Game.nes.gba` to `/mnt/sda1/ROMS/fceumm/Game.nes`,
- sets the active stock frontend family temporarily to NES (`0x01`),
- binds FCEUmm directly to the stock XGO video/audio/input callbacks,
- supplies the XGO compatibility environment shim,
- provides FCEUmm a real ROM path with `data=NULL`/`size=0`, matching the pinned core's fallback load behavior,
- points the stock `run_emulator()` indirection slots at FCEUmm's libretro exports,
- executes the stock XGO emulator loop,
- restores the previous stock libretro globals and system-family value afterward.

## What is now confirmed

**Confirmed offline:**

- FCEUmm compiles for the HC15xx/MIPS ABI.
- The reconstructed XGO stock symbol surface is sufficient for the first core.
- The full executable links with zero undefined symbols.
- The final runtime image fits comfortably inside the XGO reserved core window.
- BSS/runtime-only storage is explicitly represented by XGOC `memory_size` and can be zeroed before launch.
- The generated image has a valid, independently verified XGOC container.
- The linked FCEUmm image has no discovered `$gp` references and no constructor-array requirement.

**Not yet confirmed:**

- physical XGO boot of the modified SD-loaded `bisrv.asd`,
- successful loader execution on hardware,
- successful FCEUmm ROM launch/display/audio/input on hardware,
- runtime interaction between stock interrupt context and the external core,
- performance/stability across real NES titles,
- save-state/save-RAM integration.

## Conclusion

The first real XGO replacement emulator is no longer a theoretical port or an unresolved linker experiment.

There is now a complete, validated offline artifact pipeline producing a 1.57 MiB FCEUmm XGOC image with a 3.84 MiB runtime footprint and more than 9.6 MiB of remaining core-window headroom.

The next research boundary is no longer static linking. It is final pre-hardware safety auditing of the injected loader/firmware patch and then, when deliberately chosen, an SD-only device experiment.