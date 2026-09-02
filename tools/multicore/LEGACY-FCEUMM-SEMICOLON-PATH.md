# Historical FCEUmm semicolon/GBA experiment

The root-level FCEUmm files in this directory document the first successful XGO external-core dependency/link experiments. They are preserved because they were useful archaeology, but they are **not the current hardware-test implementation**.

In particular:

- `xgo_fceumm_entry.c` reconstructs a ROM path from the original `fceumm;<rom>.gba` browser-token experiment and binds stock callbacks directly.
- `xgo_external_core.ld` is the corresponding generic early external-core linker script.
- `xgo_fceumm_support.c` and `xgo_newlib_stubs.c` helped prove runtime closure against the preserved XGO firmware.
- `.github/workflows/xgo-fceumm-link-lab.yml` now preserves only the archive/runtime-closure part of this experiment.

## Why its final executable model was retired

Later XGO disassembly established a bidirectional `$gp` ABI boundary:

- stock firmware code expects `$gp = 0x80c34774` and performs GP-relative global accesses without reconstructing that value on function entry;
- the external FCEUmm/newlib image has its own linker `_gp` and also performs GP-relative accesses;
- stock `run_emulator()` calls the active external `retro_*` function pointers while stock `$gp` is live.

The early frontend crossed those boundaries with direct C calls/function pointers. Consequently, a zero-undefined-symbol final ELF from that experiment proved **link/runtime closure**, but not a hardware-valid calling convention.

## Authoritative native implementation

Use these files for current executable/device-test work:

```text
tools/multicore/native_nes/xgo_core_entry.s
tools/multicore/native_nes/xgo_gp_bridges.s
tools/multicore/native_nes/xgo_nes_native_frontend.c
tools/multicore/native_nes/xgo_core.ld
tools/multicore/native_nes/xgo_nes_loader.c
```

The authoritative executable CI gate is:

```text
.github/workflows/xgo-native-fceumm-full-link.yml
```

The ABI evidence and exact production disassembly are recorded in:

```text
findings/xgo-bidirectional-gp-abi.md
```

Do not revive the historical final ELF/XGOC path without adding the same bidirectional GP discipline and re-establishing its full call graph from firmware evidence.
