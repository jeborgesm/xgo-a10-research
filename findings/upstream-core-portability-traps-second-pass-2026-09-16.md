# Upstream core portability traps — second commit-history pass

Date: 2026-09-16
Branch: `research-a10-hardware-lineage`

This pass continued mining historical SF2000 multicore commits for failures that were solved upstream but could easily be misdiagnosed as an incompatible emulator when porting cores to XGO.

## 1. `.sdata` is essential for some C/C++ cores

Commit `90f6ffe91f92ef3f2b23f6c56e184945857b36a2` documents a subtle binary-packaging failure. The external-core objcopy initially omitted `.sdata`. That section contains important small-data globals including `_impure_ptr`, which carries newlib reentrancy state.

Consequences included crashes during C++ constructor initialization when a static object's destructor registration called `atexit()`, and broken `_r` reentrant libc functions such as `sscanf_r`-style paths. Adding `.sdata` to the emitted core binary allowed Stella2014 to run.

### XGO implication

When importing upstream cores, a crash before or during `retro_init`/constructors must not automatically be blamed on the loader ABI. Audit emitted ELF sections and the flat-binary conversion contract. Preserve `.text`, `.rodata`, `.data`, `.sdata`, constructor/destructor arrays, exception tables, and any other section actually required by the core/toolchain.

This is especially important if future XGO imports use C++ cores.

## 2. MIPS unaligned accesses are a recurring portability fault

Commit `44efa1df854464198b49316753e3fcc9808cde73` preserves an Osaka fix for Caprice32. A computed byte offset used to form a `uint32_t *` could be misaligned. The fix forces four-byte alignment before forming the pointer:

`val = val & ~3`

The same commit records the SF2000 build contract as little-endian MIPS32, soft-float, `-G0`, no ABI calls and no PIC, with static linking.

Later commit history also explicitly records an unaligned-memory-access fix for the Atari 5200 core.

### XGO implication

If a core loads but crashes only in particular rendering/emulation paths, inspect unaligned 16/32-bit memory access before assuming a firmware fault. The family CPU/toolchain environment does not tolerate every access pattern that may happen to work on x86/ARM hosts.

Create an `unaligned-access` classification in the future XGO core-port matrix.

## 3. `clock()` semantics were wrong in the compatibility libc

Commit `e239483a76df4654e26f6e6bead2d551957c1ab1`, explicitly credited to Osaka, fixes the compatibility implementation of `clock()`.

`os_get_tick_count()` returns milliseconds; returning that value directly as `clock_t` is incorrect. Correct conversion is:

`os_get_tick_count() * CLOCKS_PER_SEC / 1000`

### XGO implication

Timing bugs in imported cores may originate in libc/POSIX compatibility shims rather than emulator timing itself. Our future XGO core environment should have a small validated compatibility-runtime test suite covering at least time, filesystem, allocation/reentrancy, directory operations, formatted I/O, cache flushing, and constructor initialization.

## 4. Core failures frequently belong to the platform shim, not the emulator

The historical commit stream repeatedly contains fixes for:

- controller device negotiation;
- audio callback return semantics;
- sample-rate adaptation;
- XRGB8888 conversion;
- save-state screenshot allocation;
- cache coherency;
- `$gp` and interrupt context;
- unaligned memory access;
- libc/reentrancy state;
- `clock()` semantics;
- scaling and overscan;
- build/link section selection.

This changes how future XGO import failures should be triaged.

Recommended stages:

1. flat binary/link packaging
2. loader entry and `$gp`
3. constructors/libc runtime
4. `retro_init`
5. environment negotiation
6. content loading contract
7. video format/geometry
8. audio callback/sample rate
9. input device negotiation
10. first `retro_run`
11. cache/dynarec/IRQ behavior
12. save/load
13. clean unload/return to menu

Only after identifying the failing stage should a core be labeled incompatible.

## Research direction

Continue mining commits with words such as `fix`, `workaround`, `crash`, `freeze`, `unaligned`, `audio`, `sample rate`, `input`, `scaling`, `cache`, `gp`, `state`, `libc`, and `working`. Also inspect old attempts that never became release builds: failed ports often document platform constraints more clearly than successful ones.
