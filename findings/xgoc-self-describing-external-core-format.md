# XGOC self-describing external-core format

Status: **implemented research container; offline-validated, not yet hardware-tested**.

## Why a container is needed

The first XGO external-code probe used a raw `core_87000000` blob and several implicit assumptions:

- fixed load address `0x87000000`,
- hard-coded 1 MiB read window,
- entry point assumed to equal load address,
- no file-integrity check,
- no explicit runtime/BSS extent.

That was sufficient to prove the architecture offline, but it is too ambiguous for production emulator cores. In particular, an ELF's file-backed `.text/.rodata/.data` bytes and its runtime `.bss` extent are different quantities.

The XGOC container makes those quantities explicit while keeping the on-device loader very small.

## Version 1 header

The header is exactly 32 bytes, little-endian:

```text
offset  size  field
0x00    4     magic = ASCII "XGOC"
0x04    4     low16 version (=1), high16 header size (=32)
0x08    4     load address (=0x87000000)
0x0c    4     entry offset from load address
0x10    4     file-backed payload size
0x14    4     total runtime memory size
0x18    4     payload CRC-32/IEEE
0x1c    4     header CRC-32/IEEE over bytes 0x00..0x1b
0x20          payload bytes begin
```

Version 1 intentionally has no flags. If future cores need metadata such as system-family ID or capabilities, the format can grow by increasing the version/header-size pair rather than overloading an unprotected field.

## Integrity model

Two independent CRCs are used:

- `header_crc32` protects the executable placement metadata, entry point, sizes, and expected payload CRC;
- `payload_crc32` protects the file-backed executable/data image.

The CRC is the standard reflected CRC-32/IEEE used by Python `binascii.crc32`, not the CRC-32/MPEG-2 algorithm used by the outer XGO LCFG firmware container.

The separation is deliberate: XGOC is an external-core format and should not inherit the firmware-container checksum merely because both happen to use CRCs.

## Runtime reconstruction

The external-core linker exposes:

```text
__image_start
__file_end
__bss_start
__bss_end
__image_end
```

`objcopy` serializes only `.text/.rodata/.data`. It may trim meaningless trailing alignment bytes. Therefore `payload_size` is the actual raw file length, while `memory_size = __image_end - __image_start` describes the complete in-memory image.

After loading and validating the payload, the XGO loader zeros:

```text
[load_addr + payload_size, load_addr + memory_size)
```

This reconstructs both omitted trailing alignment and BSS/runtime-only storage before execution.

A local LLVM build of the current probe demonstrated the distinction concretely:

```text
load/entry          0x87000000
raw payload         472 bytes
linker file span    480 bytes
runtime image       496 bytes
zero-filled tail     24 bytes
```

The eight-byte difference between raw payload and linker file span is harmless trailing alignment and is intentionally reconstructed as zero together with BSS.

## Device-side refusal checks

The current loader refuses the image unless all of the following are true:

- stock GBA behavior is bypassed only for an explicit semicolon-tagged launch;
- the live stock heap break is still below `0x87000000`;
- the 32-byte XGOC header is fully readable;
- magic/version/header size match version 1;
- header CRC matches;
- load address is exactly `0x87000000`;
- payload is non-empty;
- `memory_size >= payload_size`;
- entry point is inside the file-backed payload;
- runtime image fits below `0x87cdae00`;
- the complete payload can be read;
- payload CRC matches.

Only then does the loader zero the runtime tail, perform data-cache writeback and instruction-cache invalidation across the exact runtime range, and call the advertised entry point.

The original heap ceiling is restored after the external core returns or after any post-load validation failure.

## Live heap collision guard

The stock allocator's current-break pointer is already mapped at:

```text
0x80c337b0
```

Before lowering `RAMSIZE` to `0x87000000`, the XGOC loader checks that the live break has not already reached that address. If it has, the launch is refused.

This avoids lowering the allocator ceiling beneath memory that may already contain live stock allocations.

## Host-side tooling

`tools/multicore/probe/pack_xgoc.py` creates version-1 containers and refuses impossible address/size combinations.

`tools/multicore/probe/inspect_xgoc.py` independently validates:

- exact file length versus payload size,
- both CRCs,
- version/header geometry,
- load address,
- entry point,
- runtime memory bounds.

This gives the future XGO PC configurator a host-side validation contract while retaining independent device-side checks.

## Loader size

A local LLVM/MIPS32 soft-float build of the hardened loader is approximately:

```text
1025 bytes
```

against the confirmed stock injection window:

```text
0x1500..0x217f = 3200 bytes
```

Therefore robust metadata validation, dual CRCs, BSS reconstruction, heap-collision checks, and exact cache maintenance still consume only about one third of the available loader space.

## Confidence

**Confirmed:**

- the format/tooling implementation and host-side geometry;
- the XGO heap-break and heap-ceiling addresses used by the guard;
- the 3200-byte firmware loader hole;
- the runtime core window beginning at `0x87000000`;
- successful local MIPS32 compilation well within the injection budget.

**Not yet device-confirmed:**

- execution of an XGOC-wrapped payload on physical XGO hardware;
- the live heap position at the exact moment an external-core launch occurs;
- whether additional cache-controller quirks appear under a large production emulator image.

## Conclusion

The external-core handoff is no longer based on a raw blob and magic size assumptions. XGOC version 1 gives the XGO loader enough information to validate, reconstruct, and execute a core deterministically while remaining small enough to live entirely inside the stock firmware's confirmed unused injection window.
