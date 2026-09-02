# XGO external-core RAM window static-reference audit

Status: **strong XGO-specific evidence that `0x87000000..0x87cdae00` is not occupied by a hidden fixed stock subsystem**.

Firmware SHA-256:

`869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`

## Target window

The external-core design reserves:

```text
0x87000000 .. 0x87cdae00
```

The upper bound is XGO's confirmed stock heap ceiling (`RAMSIZE`). The loader refuses to lower that ceiling if the live stock heap break has already reached `0x87000000`.

## Static executable scan

The preserved firmware was scanned for aligned MIPS `lui` instructions whose immediate could construct an address/value in the `0x87xx....` range, then each plausible executable hit was inspected in context.

### Real stock heap-ceiling construction

At allocator initialization:

```text
0x8029197c  lui  $v0,0x87cd
0x80291980  ori  $v0,$v0,0xae00
0x80291984  sw   $v0,-0x7908($gp)
```

This constructs exactly:

```text
0x87cdae00
```

and stores it into the already-mapped `RAMSIZE` global at `0x80c2ce6c`.

This is the expected upper boundary, not a fixed consumer within the proposed core window.

### `0x87654321` is an allocator sentinel, not a pointer

Another coherent executable hit appears around `0x80297168`:

```text
0x80297168  lui  $v0,0x1234
0x8029716c  ori  $v0,$v0,0x5678
...
0x80297174  lui  $v0,0x8765
0x80297178  ori  $v0,$v0,0x4321
```

Related code around `0x80297290..0x802972b8` reconstructs the same `0x87654321` value for allocator bookkeeping/checking.

The paired constants:

```text
0x12345678
0x87654321
```

are integrity/sentinel patterns. They are not accesses to RAM address `0x87654321`.

### Remaining apparent `0x87xx` hits

Other raw `lui`-pattern matches occur in large resource/data regions. Disassembly around those locations is incoherent (invalid/unknown opcodes, impossible control flow, media/resource-like data) and does not support classification as executable fixed-address users.

No coherent stock code path was found that constructs and dereferences a fixed address inside:

```text
0x87000000 <= address < 0x87cdae00
```

other than the heap-ceiling boundary itself.

## What this does and does not prove

This audit does **not** prove that no runtime pointer could ever enter the window. Dynamic stock allocations are handled separately by the loader's live `XGO_HEAP_BREAK < 0x87000000` precondition.

It does provide XGO-specific evidence against a different failure mode: an undocumented framebuffer, DMA buffer, codec arena, or board-specific static structure hard-coded into the same upper-RAM region outside the allocator.

## Combined safety model

The external-core window is now protected by complementary evidence/checks:

```text
static firmware audit
    -> no coherent fixed stock user found in 0x87000000..0x87cdae00

stock allocator map
    -> normal heap ceiling is 0x87cdae00

runtime loader guard
    -> refuse external launch if live heap break >= 0x87000000

XGOC bounds
    -> external image memory_size may not exceed 0x87cdae00 - 0x87000000
```

## Confidence

**CONFIRMED:** stock allocator initializes `RAMSIZE` to `0x87cdae00`.

**CONFIRMED:** `0x87654321` appearances in coherent allocator code are sentinel/integrity constants paired with `0x12345678`, not a fixed RAM pointer.

**STRONG EVIDENCE:** no coherent statically addressed XGO subsystem was found inside the proposed external-core window.

**STILL DEVICE-RUNTIME DEPENDENT:** live heap position and any runtime-generated pointers must still be checked before an external launch; the loader already guards the heap break.
