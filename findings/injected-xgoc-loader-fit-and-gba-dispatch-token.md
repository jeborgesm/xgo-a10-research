# Injected XGOC loader fit and GBA dispatch-token behavior

Status: **loader fit confirmed by reproducible Codescape build; GBA run_game token contents confirmed irrelevant after launch**.

## Current injected loader

The XGOC-aware injected loader now performs substantially more work than the original raw-blob probe:

- explicit semicolon opt-in / normal-GBA forwarding;
- live heap-break collision guard;
- reservation of the `0x87000000+` external-core window before file I/O;
- XGOC v1 magic/version/header validation;
- XGOC header CRC32 and payload CRC32 verification;
- payload/runtime/entry bounds validation;
- file-backed payload load at `0x87000000`;
- zero fill of the runtime/BSS tail;
- stock sound-task shutdown handshake;
- HC15xx cache writeback/invalidate sequence;
- `(stub_path, load_state)` handoff to the external entry;
- restoration of the original stock heap ceiling on failure or return.

Despite those checks, a reproducible build with the exact Codescape MIPS32 MTI toolchain remains very small.

## Reproducible loader build

Workflow run:

```text
workflow       XGO injected loader fit
run            #2
run id         33590039922
result         success
artifact id    9831405956
artifact zip SHA-256
4747214e9a18fdc170ca71f73c77fa42e996633b97ecfe2892794c8c9ac73be7
```

Toolchain:

```text
mips-mti-elf-gcc 7.4.0
Codescape GNU Tools 2019.09-03-2
archive SHA-256
 d35717f24a67ed2091c32d9fb3d79dc5ebe84c38ac8872736aa018860a724807
```

Result:

```text
__start              0x80001500
load_and_run_core     0x80001558

.text                 0x80001500..0x8000180f  (0x310 bytes)
.rodata               0x80001810..0x80001833  (0x024 bytes)
.bss                  absent
runtime end            0x80001834

raw loader size        820 bytes
firmware-cave capacity 3200 bytes
remaining              2380 bytes
utilization            25.62%
undefined symbols      0
```

Hashes:

```text
xgo_probe_loader.elf
5f57585e84510e163f4763128379c714e8cafdf75c4edfc44ffb198ac16795a2

xgo_probe_loader.bin
9ca075712c1c101a7de41cffea6a03435d50b1c3ed6d7285462cfe4efaded99f
```

The loader therefore occupies only about one quarter of the preserved stock zero-filled firmware cave.

## Runtime-size enforcement

The loader linker script now defines `__loader_start` / `__loader_end` and contains a link-time assertion:

```text
__loader_start = 0x80001500
__loader_end <= 0x80002180
```

This is deliberately stronger than checking only the objcopied raw binary length: a future non-empty `.bss` or other allocatable section can no longer silently extend beyond the stock cave.

The established loader-preflight CI also rejects non-empty loader NOBITS/BSS because the injected loader itself has no separate startup routine that clears its own BSS.

## GBA dispatch-token content behavior

`run_game()` is at `0x80360b88`.

Its extension classifier at `0x80360a08` scans the 40-entry table beginning at runtime `0x80a3c4c8`; each entry contains an uppercase extension string and a system-family mask. Relevant entries are:

```text
index 19   GBA   0x10
index 20   AGB   0x10
index 21   GBZ   0x10
```

After classification, `run_game()` tests the low family bits. For family `0x10` it takes this path:

```text
0x80360c08  compare family with 0x10
0x80360c0c  branch to 0x80360ce4 when equal
...
0x80360ce4  move  $4,$zero
0x80360ce8  jal   0x80099bb0
0x80360cf0  move  $4,$18        ; original selected path
0x80360cf4  jal   0x80360110    ; stock run_gba / patched loader site
0x80360cf8  move  $5,$zero      ; load_state = 0
```

The generic file-open / seek / length / preload block at `0x80360c14..0x80360c8c` is skipped entirely for GBA-family content.

Therefore, once a selected path has been classified as `.gba` and reaches `run_game()`, **the bytes of the synthetic `.gba` token are not read before the external-core hook executes**. The path string is the meaningful dispatch payload.

## Remaining launch-token question

This does **not yet prove** that the stock User Games browser will display/select a zero-byte `.gba` file. That question lies one layer earlier in the frontend's directory/browser scanner.

What is now confirmed is narrower and useful:

```text
browser accepts/selects .gba token
        ↓
run_game classifies extension as family 0x10
        ↓
NO file-open/read/preload
        ↓
patched 0x80360cf4 calls XGOC loader with original path
```

Thus no real or valid GBA payload is required by the launch dispatcher itself. Future stub-format work only has to satisfy the browser/indexer layer.
