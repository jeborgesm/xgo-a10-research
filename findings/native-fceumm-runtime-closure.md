# Native FCEUmm runtime closure

Status: measured on `research-external-core-integration`

## Question

After replacing the placeholder descriptor stubs with the native XGO filesystem/time bridge, how much of the actually reachable FCEUmm runtime surface is removed, and does the bridge itself create new dependencies?

## Method

The `FCEUmm runtime closure audit` roots a relocatable garbage-collected link at the real native external-core entry point, `__core_entry__`, using the pinned HC15xx FCEUmm and libretro-common sources.

It performs two otherwise identical reachable links:

1. native frontend + environment shim + preloaded-ROM `sbrk()` + FCEUmm/libretro-common;
2. the same graph plus `native_nes/xgo_newlib_syscalls.c`.

Undefined symbols are compared after section GC. This avoids treating unreachable archive members as runtime requirements.

Evidence run: GitHub Actions run `33642991503`, commit `bc6949e4e6ebb46467b41839a48ad44109bd8162`.

## Initial bridge result

Before the first syscall bridge, the reachable Linux-MIPS graph had **96** unresolved symbols.

After the bridge, it had **89**.

Exactly **7** dependencies were resolved:

- `__stat64_time64`
- `close`
- `lseek64`
- `mkdir`
- `open64`
- `read`
- `write`

The bridge introduced **zero** new unresolved symbols.

This established that the filesystem bridge measurably closes the native FCEUmm dependency graph without expanding the external runtime contract.

## SF2000 filesystem ABI correction

While promoting the bridge from a Linux-MIPS reachability experiment to the exact Codescape runtime, two parallel XGO syscall implementations were found in the branch: the earlier general `tools/multicore/xgo_newlib_syscalls.c` and the newer native-NES-specific copy.

Comparing them against the maintained SF2000 Multicore `stockfw.h` and `lib.c` exposed an actual ABI bug in the native copy. The proven ALi filesystem flag values are:

- `FS_O_RDONLY = 0x0000`
- `FS_O_WRONLY = 0x0001`
- `FS_O_RDWR   = 0x0002`
- `FS_O_APPEND = 0x0008`
- `FS_O_CREAT  = 0x0100`
- `FS_O_TRUNC  = 0x0200`

The native copy had incorrectly used `0x0200` for create and `0x0400` for truncate. Commit `0a0dadac4bcc2f4cb463bd0f87aa98dd7ac56976` corrected those values and carried the upstream-proven `fs_opendir` / `fs_readdir` / `fs_closedir` translation into the native path.

This matters independently of link success: a core built with the former constants could silently request the wrong stock-filesystem operation when opening writable files.

The native bridge also supplies `readdir64()` as a large-file ABI alias over the same XGO directory record translation. Directory access belongs in the XGO platform bridge rather than in libc.

## Exact Codescape runtime result

The decisive experiment uses the exact HC15xx Codescape bare-metal toolchain, pinned HC15xx FCEUmm and libretro-common sources, the custom XGO `dirent.h`, and the production frontend contract with `XGO_WITH_NEWLIB` enabled.

The rooted native graph immediately before standard runtime linkage contained **54 unresolved symbols**. These were ordinary newlib/libm dependencies such as `malloc`, `calloc`, stdio/string routines, math functions, locale/time functions, `__libc_init_array`, `__sinit`, and the newlib reentrancy globals.

Adding the exact Codescape runtime group `-lc -lm -lgcc` reduced that graph to only three bottom-level hooks:

- `_init`
- `link`
- `unlink`

This was measured in Actions run `33645093613` at commit `28079aa7c633dbb8e3dc1974ad0739130aaa1358`.

Those three hooks were then closed deliberately in commit `2783df5fe9051143fe99ee931f6bfdb5ce7cea5d`:

- `_init()` is a no-op because the external image has no crt0-provided legacy `_init` section; constructors are still reached through `__libc_init_array()`.
- `link()` returns `-1` / `ENOSYS` because the stock ALi filesystem surface has no proven hard-link operation.
- `unlink()` likewise returns `-1` / `ENOSYS`; no firmware deletion address is guessed or silently treated as success.

The exact Codescape audit was rerun as Actions run `33645381851` and produced the final closure result:

- **before Codescape runtime: 54**
- **after Codescape runtime: 0**
- **resolved by runtime: 54**
- **introduced by runtime: 0**

Therefore the production-shaped native FCEUmm graph now has **zero unresolved symbols** under the exact runtime that HC15xx/SF2000 uses.

## Meaning of the zero-unresolved result

This is stronger than the earlier fully linked support experiment. The measured graph now contains the actual native XGO frontend, production newlib initialization, private preloaded-ROM-preserving heap, low-level XGO filesystem bridge, directory translation, pinned FCEUmm, pinned libretro-common, and exact Codescape libc/libm/libgcc.

No stock firmware `malloc`, `free`, `realloc`, `calloc`, or generic libc symbol has been imported into the core. Standard C runtime behavior is owned by the external image, while only explicitly mapped device services cross into the stock firmware.

The runtime boundary is consequently small and understandable:

- XGO stock filesystem primitives;
- scheduler/tick services;
- stock libretro callback transport and selected globals;
- the preloaded ROM / 64 MiB buffer contract;
- external Codescape newlib/libm/libgcc inside the core image.

## Current conclusion

The dependency-closure phase is complete. The native NES/FCEUmm path now has a rooted production call graph with **zero unresolved symbols** and a corrected, evidence-backed platform bridge.

The next proof is no longer another runtime shim. It is the final absolute image link at `0x87000000`, validation of `__core_entry__`, file-backed/BSS span and reserved-window headroom, raw-binary extraction, and XGOC packaging. That work is now captured by the `XGO native FCEUmm full link` workflow.
