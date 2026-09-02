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

## Result

Before the syscall bridge, the reachable graph had **96** unresolved symbols.

After the syscall bridge, it had **89**.

Exactly **7** dependencies were resolved:

- `__stat64_time64`
- `close`
- `lseek64`
- `mkdir`
- `open64`
- `read`
- `write`

The bridge introduced **zero** new unresolved symbols.

This is an important distinction: the bridge is not merely compiling. It measurably closes the native FCEUmm dependency graph without expanding the external runtime contract.

## SF2000 filesystem ABI correction

While promoting the bridge from a Linux-MIPS reachability experiment to the exact Codescape runtime, two parallel XGO syscall implementations were found in the branch: the earlier general `tools/multicore/xgo_newlib_syscalls.c` and the newer native-NES-specific copy.

Comparing them against the maintained SF2000 Multicore `stockfw.h` and `lib.c` exposed an actual ABI bug in the native copy. The proven ALi filesystem flag values are:

- `FS_O_RDONLY = 0x0000`
- `FS_O_WRONLY = 0x0001`
- `FS_O_RDWR   = 0x0002`
- `FS_O_APPEND = 0x0008`
- `FS_O_CREAT  = 0x0100`
- `FS_O_TRUNC  = 0x0200`

The native copy had incorrectly used `0x0200` for create and `0x0400` for truncate. Commit `0a0dadac4bcc2f4cb463bd0f87aa98dd7ac56976` corrects those values and carries the upstream-proven `fs_opendir` / `fs_readdir` / `fs_closedir` translation into the native path.

This matters independently of link success: a core built with the former constants could silently request the wrong stock-filesystem operation when opening writable files.

The native bridge now also supplies `readdir64()` as a large-file ABI alias over the same XGO directory record translation. The Linux-MIPS reachability audit had exposed `opendir`, `closedir`, and `readdir64` as remaining external dependencies; they belong in the XGO platform bridge rather than in libc.

## Remaining surface

The original remaining 89-symbol set was dominated by four normal runtime classes:

- GCC soft-float/integer helpers such as `__adddf3`, `__divdi3`, `__mulsf3`, and conversion/comparison helpers;
- libc allocation/string/stdio/ctype/time functions;
- libm functions (`sin`, `cosf`, `pow`, `sqrt`, `exp*`, `log*`, etc.);
- directory/locale functions from newlib/libretro-common.

The directory subset is now being closed by the native XGO bridge. The large libc/libm/compiler-runtime remainder still strongly argues against implementing standard runtime functions as XGO-specific hand-written shims.

The next integration boundary is the **exact HC15xx Codescape newlib/libm/libgcc runtime** already proven by the older FCEUmm link lab.

A dedicated `FCEUmm Codescape runtime audit` measures the real native `__core_entry__` graph before and after `-lc -lm -lgcc`. It now compiles the frontend with `XGO_WITH_NEWLIB`, making `_REENT_INIT_PTR`, `__sinit`, and `__libc_init_array` part of the graph; this is intentionally stricter than the first simplified reachability experiment.

Any symbols surviving that experiment are the real bottom-level XGO/newlib boundary that still requires explicit implementation.

## Current conclusion

The native NES/FCEUmm path has moved beyond archive compatibility testing. We now have a rooted executable call graph, a real stock-filesystem bridge, a corrected SF2000 open-flag contract, directory translation, private ROM-preserving heap policy, and quantitative dependency closure. The remaining work should be driven by the post-Codescape residual set rather than by the much larger pre-runtime symbol list.
