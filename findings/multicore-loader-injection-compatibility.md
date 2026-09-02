# XGO Multicore loader-injection compatibility

Status: **stock binary layout and GBA interception point confirmed; no device patch has been executed**.

## Why this matters

SF2000 Multicore does not replace the full operating firmware. Its classic loader build copies the stock `bisrv.asd`, injects a small loader into unused low-address space, patches the stock GBA-launch call to enter that loader, and reseals the ASD CRC.

A direct comparison against the preserved XGO firmware now shows that the XGO retained the same critical low-address free-space layout and the same launch-call contract.

## Exact loader workspace survives on XGO

The upstream SF2000 Multicore Makefile uses:

```text
LOADER_OFFSET   = 0x1500
LOADER_ADDR     = 0x80001500
LOADER_ADDR_MAX = 0x80002180
```

The preserved XGO `bios/bisrv.asd` contains:

```text
file offsets 0x1500..0x217f
length       0x0c80 = 3200 bytes
contents     every byte = 0x00
```

The first live code after that gap begins at runtime/file offset `0x2180`.

Therefore the exact 3200-byte loader window expected by classic SF2000 Multicore is physically unused in the XGO image as well.

## Exact debug-font workspace also survives

Classic Multicore places a 672-byte LCD debug font at file offset `0x2260`.

The XGO range:

```text
0x2260..0x24ff
length = 672 bytes
```

is also entirely zero-filled.

Thus both of Multicore's low-address injection regions exist intact in the XGO firmware.

## XGO GBA interception point

The XGO extension dispatcher identifies native GBA with system mask `0x10` and eventually reaches the GBA wrapper at:

```text
run_gba = 0x80360110
```

The dispatcher call site is:

```text
0x80360cf0  move  $4,$18
0x80360cf4  jal   0x80360110
0x80360cf8  move  $5,$zero
```

This establishes the call contract at the patch site as:

```c
run_gba(filename, load_state);
```

with the filename already in `$a0` and load-state argument supplied in `$a1`.

That is exactly the signature expected by the Multicore loader's `load_and_run_core(const char *file_path, int load_state)` entry.

Therefore the XGO equivalent of the classic SF2000 `jal run_gba -> jal loader` patch is:

```text
XGO patch instruction address/file offset: 0x00360cf4
loader target:                         0x80001500
```

For a loader linked at `0x80001500`, the little-endian MIPS `jal` encoding is the same four bytes used by upstream Multicore:

```text
40 05 00 0c
```

No patch has been applied to a device image during this research.

## IRQ / exception hook layout also matches

The upstream Multicore patch architecture also uses low firmware locations around:

```text
0x80049744  IRQ-path GP restore patch
0x800030d4  watchdog handler redirect
0x800495a0  general-exception trap redirect
```

Those locations are all live, semantically compatible code points in XGO as well.

Most importantly, XGO startup establishes its own GP at:

```text
0x80001270  lui   $gp,0x80c3
0x80001274  addiu $gp,$gp,0x4774
```

and the newer Multicore technique can copy those exact two startup instructions into `0x80049744/48`, avoiding a hard-coded SF2000 GP value.

## Heap/core-load window

The XGO allocator initializes:

```text
current heap break = 0x813b4bb4
heap ceiling       = 0x87cdae00
```

The heap ceiling is stored at:

```text
RAMSIZE = 0x80c2ce6c
```

Classic Multicore lowers this ceiling to `0x87000000` before loading an external core at `0x87000000`.

For XGO this leaves approximately:

```text
0x87000000 - 0x813b4bb4 ~= 91.3 MiB
```

of address space below the external-core window, while reserving roughly 13.7 MiB between `0x87000000` and the stock heap ceiling.

This does not yet prove that every XGO runtime allocation remains below `0x87000000`; runtime testing is still required. It does show that the allocator architecture and address window are compatible with the Multicore reservation strategy.

## Overall conclusion

The following Multicore prerequisites are now independently confirmed on XGO:

- stock firmware runs from SD-loaded `bisrv.asd`;
- ASD can be resealed with known LCFG size + CRC32/MPEG-2 fields;
- 3200-byte loader injection window at `0x1500` is completely unused;
- 672-byte debug-font window at `0x2260` is completely unused;
- XGO has a normal two-argument `run_gba(filename, load_state)` call that can be redirected;
- exact XGO GBA call-site offset is `0x360cf4`;
- stock libretro callbacks have been resolved;
- stock GP and IRQ restoration mechanism have been resolved;
- stock heap ceiling has been resolved and can use the `0x87000000` reservation model.

This substantially upgrades an XGO Multicore port from **conceptually plausible** to **binary-layout compatible with a concrete remaining symbol/build-validation task**.

## Remaining blockers before a controlled test build

1. complete the external-core linker imports needed by one minimal test core;
2. verify any watchdog/exception redirect instructions against the chosen Multicore fork;
3. identify or disable optional debug/LCD dependencies not required for first boot;
4. verify the loader binary fits entirely below `0x2180`;
5. reseal the patched ASD and perform a byte-level patch audit;
6. first hardware test should use a separate SD card and must not include `UpdateFirmware/Firmware.upk`.

## Comparative sources

- `madcock/sf2000_multicore` classic Makefile and loader architecture.
- `Trademarked69/sf2000_multicore` newer GP-restoration approach that copies startup GP instructions into the IRQ path.
- XGO preserved `bios/bisrv.asd`, SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.
