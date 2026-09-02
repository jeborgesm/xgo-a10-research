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

## Remaining surface

The remaining 89-symbol set is dominated by four normal runtime classes:

- GCC soft-float/integer helpers such as `__adddf3`, `__divdi3`, `__mulsf3`, and conversion/comparison helpers;
- libc allocation/string/stdio/ctype/time functions;
- libm functions (`sin`, `cosf`, `pow`, `sqrt`, `exp*`, `log*`, etc.);
- directory/locale functions from newlib/libretro-common.

That shape strongly argues against implementing the remaining surface as XGO-specific hand-written shims. The next integration boundary is the **exact HC15xx Codescape newlib/libm/libgcc runtime** already proven by the older FCEUmm link lab.

A dedicated `FCEUmm Codescape runtime audit` now measures the native `__core_entry__` graph before and after `-lc -lm -lgcc`. Any symbols surviving that experiment are the real bottom-level XGO/newlib boundary that still requires explicit implementation.

## Current conclusion

The native NES/FCEUmm path has moved beyond archive compatibility testing. We now have a rooted executable call graph, a real stock-filesystem bridge, and quantitative dependency closure. The remaining work should be driven by the small post-Codescape residual set rather than by the much larger pre-runtime symbol list.
