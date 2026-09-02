# XGO guarded high-RAM external-code execution probe

Status: **host build and patch construction successful; no hardware execution yet**.

## Purpose

This is the intermediate step between the 339-byte SD-write smoke loader and a real XGO Multicore/libretro port.

The goal is to prove the exact mechanism Multicore depends on:

```text
SD file -> stock XGO fread -> 0x87000000 -> cache flush -> execute
```

without introducing an emulator core, advanced video code, or additional board-driver imports.

## Runtime heap guard

The loader first checks the live XGO allocator state:

```text
current heap break = *(uint32_t *)0x80c337b0
```

If the value is already at or above:

```text
0x87000000
```

the loader refuses to use the Multicore core window and writes a failure marker instead.

This is possible because the XGO `sbrk` state has now been independently reconstructed.

## Probe path

All ordinary GBA filenames continue to forward to:

```text
run_gba = 0x80360110
```

Only the explicit filename:

```text
/mnt/sda1/ROMS/XGO_EXEC_PROBE.gba
```

enters the high-RAM execution test.

## External module

The loader opens:

```text
/mnt/sda1/XGO_PROBE.BIN
```

and reads it into:

```text
0x87000000
```

The test module is intentionally tiny and contains only:

```c
unsigned xgo_external_probe(void)
{
    return 0x58474f21; // 'XGO!'
}
```

It is linked with entry address exactly `0x87000000`.

## Memory-ceiling handling

Before reading/executing the module, the loader saves the stock heap ceiling:

```text
RAMSIZE = *(uint32_t *)0x80c2ce6c
```

and temporarily writes:

```text
0x87000000
```

After the external function returns, the original ceiling is restored before the result marker is written.

## Cache handling

The loader performs the same broad MIPS cache maintenance strategy used by classic SF2000 Multicore:

- index writeback/invalidate over the data cache range;
- `sync`;
- index invalidate over the instruction cache range;
- execution barrier/nop sequence.

The external function is called only after this operation.

## Observable result

If the external function returns:

```text
0x58474f21
```

then the loader creates:

```text
/mnt/sda1/XGO_EXEC.OK
```

Otherwise it creates:

```text
/mnt/sda1/XGO_EXEC_FAIL.TXT
```

Failure markers also distinguish an unavailable heap window or missing module file.

## Host-build results

Both the loader and external module compile successfully using Clang's `mipsel-none-elf` target.

Observed properties:

```text
injected loader size = 1004 bytes
available XGO hole   = 3200 bytes
remaining margin     = 2196 bytes
external module size = 48 bytes
loader relocations   = none
module relocations   = none
loader entry         = 0x80001500
module entry         = 0x87000000
```

Therefore this substantially more capable probe still occupies less than one third of the stock XGO injection window.

## Unexecuted patched-image construction

A patched research copy of the XGO ASD was generated locally but has not been executed.

It uses the already-confirmed patch architecture:

```text
loader at file offset 0x1500
GBA JAL redirect at file offset 0x360cf4
LCFG CRC32/MPEG-2 resealed at 0x18c
```

For that specific local unexecuted build:

```text
CRC32/MPEG-2 = 0x080696a1
SHA-256      = 9d09e297171b1801dc6eb322e49b0082391ab028da978dcfda78db86b0345c1d
```

These are build-identification values only.

## Significance for Multicore feasibility

A successful physical execution of this probe would independently validate all of the following before a libretro core is attempted:

1. modified + resealed `bisrv.asd` boots on XGO;
2. the XGO GBA call-site redirect works;
3. injected code at `0x80001500` executes;
4. resolved stock stdio addresses are callable;
5. the live heap remains below `0x87000000` at launch time;
6. the stock heap ceiling can be temporarily lowered safely;
7. SD data can be loaded into `0x87000000`;
8. cache maintenance permits execution of freshly loaded code;
9. execution returns cleanly to the stock frontend.

That would leave the libretro ABI/symbol layer—not the fundamental dynamic-loading mechanism—as the next major Multicore task.

## Source

- `tools/multicore/xgo_external_exec_loader.c`
- `tools/multicore/xgo_external_probe_module.c`
- `tools/multicore/xgo_external_probe_module.ld`
- `tools/multicore/xgo_smoke_loader.ld` can also be used to link this loader at `0x80001500`.
