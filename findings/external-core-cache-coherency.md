# External-core cache coherency requirement

Status: **confirmed design correction in the XGO probe loader**.

## Finding

The first XGO external-payload prototype loaded `core_87000000` through the stock stdio path into cached KSEG0 memory at `0x87000000`, but its hand-written cache maintenance loop operated on `0x80000000..0x80004000`.

That range does not cover the newly written external payload.

On a split I/D-cache MIPS32 target, executing bytes immediately after cached data writes requires an explicit data-cache writeback / instruction-cache invalidation strategy for the executable range. The old prototype therefore had a real cache-coherency hole even though its file loading and entry address were otherwise correct.

## Correction

The research loader now performs cache maintenance over the same bounded external-core window it loads:

```text
CORE_BASE    = 0x87000000
PROBE_LIMIT  = 0x00100000
range        = 0x87000000..0x870fffff
```

It performs the D-cache operation over that range, executes `sync`, then performs the I-cache operation over that range before calling the external entry point.

This remains a **probe implementation**, not the final production loader. A production loader should derive cache-maintenance bounds from the actual linked image/memory span rather than using the temporary 1 MiB probe limit.

## Second issue exposed: BSS

The current raw `objcopy` build emits `.text`, `.rodata`, and `.data`; `.bss` is not part of the raw file payload. The tiny probe happens not to depend on a substantial zero-initialized runtime area, but a real emulator such as FCEUmm will.

Therefore the production external-core format/loader must explicitly solve BSS initialization. Acceptable designs include:

1. export linked image-end and BSS-end metadata and zero `[__bss_start, __bss_end)` before entry;
2. prepend a tiny core header containing file size, memory size/BSS bounds, and entry offset;
3. include an entry stub in the external image that zeros its own BSS before entering the frontend/core runtime.

Blindly loading a raw binary and jumping to it is not sufficient for a production libretro core.

## Consequence

This is an important pre-hardware catch. It does not invalidate the external-core architecture; it identifies two normal bare-metal loader responsibilities that must be completed before a real emulator test:

- executable-range cache coherency;
- deterministic BSS initialization.

The cache issue is corrected in the research probe. BSS metadata/initialization is now a required item for the production XGO core-image contract.
