# First fully linked XGO FCEUmm external core

Status: **offline build/link/container path confirmed; physical XGO execution not yet tested**.

## Milestone

The XGO external-core research has reached the first complete emulator image rather than a synthetic transport probe.

The original successful full-link milestone was GitHub Actions run #29. Subsequent pre-hardware audits found and corrected several wrapper/loader hazards (cache-index semantics, stock sound-task shutdown, and stale OEM frameskip state), so the authoritative reference artifact is now the later green build at commit `f6acb5750c2f3aa6a26e4af87814fcf9375b1445`.

Current successful FCEUmm link-lab run:

```text
run id       33587556097
artifact id  9830610308
artifact SHA-256
b91bec56f05725960079c51d9d23f686c51d85649e401a93b41ae9ad10d6d37b
```

The pipeline:

1. installs the exact Codescape MIPS MTI bare-metal toolchain,
2. checks out the pinned HC15xx FCEUmm source,
3. builds the SF2000/HC15xx-compatible FCEUmm static archive,
4. builds the XGO compatibility/runtime support layer,
5. fully links an XGO executable at `0x87000000`,
6. verifies **zero undefined symbols**,
7. verifies the complete runtime image fits the reserved XGO RAM window,
8. extracts the file-backed binary,
9. packs it as an XGOC v1 `core.xgc`,
10. independently revalidates the XGOC header/bounds/CRCs.

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

Archive-level progression:

```text
FCEUmm true external symbols             81
After XGO support layer                  67
After XGO firmware + libc/libm/libgcc     0
Fully linked executable                   0
```

## Current post-audit memory layout

Normalized low-32-bit addresses from the current ELF are:

```text
__image_start  0x87000000
__start        0x87000098
__file_end     0x8717ec00
__bss_start    0x8717ec00
__image_end    0x873a9e30
```

Derived sizes:

```text
entry offset       0x98
file-backed span   1,567,744 bytes = 0x17ec00
payload size       1,567,744 bytes = 0x17ec00
runtime memory     3,841,584 bytes = 0x3a9e30
zero/BSS tail      2,273,840 bytes
reserved window   13,479,424 bytes = 0xcdae00
remaining headroom 9,637,840 bytes
```

Thus FCEUmm still occupies only about 28.5% of the reserved external-core window `0x87000000..0x87cdae00`.

The file-backed payload ends exactly where the linker declares `__file_end`; no hidden gap or accidental runtime-only section is serialized into the XGOC payload.

## Current XGOC result

The packer generated and the independent inspector accepted:

```text
magic         XGOC
version       1
load          0x87000000
entry         0x87000098
payload       1,567,744 bytes
runtime       3,841,584 bytes
zero tail     2,273,840 bytes
payload CRC   0x70631538
header CRC    0x5035ddd8
```

Current output hashes:

```text
xgo-fceumm.elf
d333931900028d9bbc7fa7ba6ccc35132b9ec82e1dd3657f3edd65c8bd4590e5

xgo-fceumm.bin
eefad5d8074a2a58192443e7579aef11b53f29b84226a60fbbbaa3f59efb7c13

core.xgc
0dc7ddef286ac233fe816d9c0400022b85179968ec0d32e7b1ff7853073da8b0
```

These values supersede the earlier run-#29 hashes and dimensions. The small 32-byte file/runtime growth came from the wrapper preflight correction that neutralizes stale `gfn_frameskip` state.

## Binary-startup audit

### Entry point

`__start` is executable code at:

```text
0x87000098
```

matching XGOC `entry_offset=0x98`.

### GP dependency

A complete disassembly search of the linked ELF found **no `$gp` references**.

This is consistent with `-G0 -mno-abicalls -fno-pic` and substantially reduces external-core GP-state risk for this FCEUmm image. Stock interrupt context is still protected by the separate IRQ GP-repair patch in the modified ASD.

### Constructors / newlib startup

The ELF contains no output sections named:

```text
.init_array
.fini_array
.ctors
.dtors
```

The newlib `_reent`/`_impure_ptr` objects retained by libc are file-backed initialized data, not an uninitialized startup obligation. Content I/O deliberately uses XGO firmware stdio compatibility wrappers rather than newlib stdio. No current evidence justifies importing a larger CRT initialization path merely because newer full Multicore implementations perform one.

Classification: **audited; no current startup blocker identified**.

### BSS

The file-backed payload ends at `0x8717ec00`; runtime-only storage continues to `0x873a9e30`. XGOC `memory_size` causes the loader to zero the full 2,273,840-byte runtime tail before entry.

This closes the BSS problem identified during the original raw-probe audit.

## XGO execution bridge

The core is statically linked, so unlike upstream Multicore it does not require a runtime `retro_core_t` API table.

The XGO `__start(stub_path, load_state)` bridge currently:

- accepts only an intercepted component named exactly `fceumm`,
- converts `fceumm;Game.nes.gba` to `/mnt/sda1/ROMS/fceumm/Game.nes`,
- temporarily selects stock NES family policy (`0x01`),
- binds FCEUmm directly to stock XGO video/audio/input callbacks,
- supplies the truthful XGO compatibility environment shim,
- provides a real ROM path with `data=NULL` / `size=0`, matching pinned FCEUmm behavior,
- redirects the stock `run_emulator()` function-pointer slots to FCEUmm,
- neutralizes the OEM `gfn_frameskip` hook for the session so behavior cannot depend on whichever emulator ran previously,
- executes the stock XGO emulator loop,
- restores the previous stock libretro globals, frameskip pointer, game info and system-family state afterward.

The injected loader separately reproduces stock `run_gba()` sound-task shutdown before external-core entry because the dispatcher hook bypasses that wrapper entirely.

## What is now confirmed

**Confirmed offline:**

- FCEUmm compiles for the HC15xx/MIPS ABI.
- The reconstructed XGO stock symbol surface is sufficient for the first core.
- The full executable links with zero undefined symbols.
- The final runtime image fits comfortably inside the XGO reserved core window.
- BSS/runtime-only storage is explicitly represented by XGOC `memory_size` and zeroed before launch.
- The generated image has a valid, independently verified XGOC container.
- The linked FCEUmm image has no discovered `$gp` references and no constructor-array requirement.
- The wrapper no longer inherits stale OEM frameskip state.
- The external dispatch path now reproduces the stock sound-task shutdown precondition before emulator entry.

**Not yet confirmed:**

- physical XGO boot of the modified SD-loaded `bisrv.asd`,
- successful loader execution on hardware,
- successful FCEUmm ROM launch/display/audio/input on hardware,
- runtime interaction across all stock wrapper globals not yet fully classified,
- performance/stability across real NES titles,
- save-state/save-RAM integration.

## Conclusion

The first real XGO replacement emulator is no longer a theoretical port or unresolved linker experiment.

There is now a reproducible post-audit artifact pipeline producing a 1.57 MiB FCEUmm XGOC image with a 3.84 MiB runtime footprint and more than 9.6 MiB of remaining core-window headroom.

The remaining pre-hardware boundary is now the exact stock-wrapper setup contract: every state mutation normally performed by the bypassed `run_gba()` path must be classified as reproduced, intentionally replaced, or irrelevant before an SD-only execution test is justified.