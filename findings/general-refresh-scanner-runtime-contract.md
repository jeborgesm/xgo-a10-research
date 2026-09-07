# General Refresh scanner — exact runtime discovery contract

Date: 2026-09-07  
Branch: `research-game-list-general-scanner`

Status: **new post-Test06b runtime contract closed; no hardware candidate generated yet**

## Protected starting point

The implementation must start from golden artifact:

`game-list-test06b-explicit-refresh-timed-status`

- ZIP SHA-256: `2d859b3ca3f0644a461c197fcfe0b58f2650c26bc6a7c8d28a189da196aa1042`
- firmware SHA-256: `5d15cbe1cef380b3517cbd64727526e1b837df5160ba5275ccde6fec01324f4e`

The Test06b User Menu layout, Refresh dispatch, stock-font result messages, ~3-second expiry, selector/footer behavior, PAL/NTSC placement, and prior emulator/audio behavior are frozen.

## Exact stock directory ABI

Direct disassembly of the preserved stock XGO firmware (SHA-256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`) closes the wrapper contract used by the native User Games scanner.

### Open directory

`0x807d40c4`

Input:
- `a0 = path`

Behavior:
- calls lower `fs_opendir @ 0x802abe28`;
- on success allocates a 0x404-byte frontend handle;
- stores the lower directory handle at offset 0;
- copies the path at offset 4.

Return:
- pointer to frontend directory handle;
- zero/null on failure.

### Read next entry

`0x807d4124`

Inputs:
- `a0 = frontend directory handle`
- `a1 = frontend entry buffer`

The caller-supplied entry buffer is 0x238 bytes.

On a successful read the wrapper writes:

```text
entry + 0x000 : uint8  is_directory
entry + 0x008 : char   filename[0x226]
entry + 0x22d : forced NUL terminator
```

The directory flag is derived from the lower stat/mode field; file size is not copied into the frontend entry.

The wrapper calls:
- `fs_readdir @ 0x802ac438`
- filename copy helper `0x801b0cd8`

The native scanner loops while this wrapper returns a non-negative value.

### Close directory

`0x807d41f4`

Input:
- `a0 = frontend directory handle`

Behavior:
- calls `fs_closedir @ 0x802ac4f0` on handle+0;
- frees the frontend handle.

## Stock scanner corroboration

The native scanner at `0x80353ae0` uses exactly this contract:

```text
0x80353b4c  dir_open(path)
0x80353b5c  allocate 0x238-byte entry
0x80353ba8  dir_next(handle, entry)
0x80353bb8  read entry.is_directory
0x80353bc4  strlen(entry.filename)
0x80353bd4  find extension separator
0x80353be0  uppercase extension
0x80353be8  extension classifier 0x80360a08
```

Accepted filenames therefore can be discovered by a new Refresh implementation without touching raw FAT directory structures.

## Exact stdio size helpers

Existing repository work is confirmed for the stock stdio surface needed by the stable-merge implementation:

```text
fopen   0x802b3524
fread   0x802b3698
fseeko  0x802b3804
ftell   0x802b3f1c
fclose  0x802b2f40
fwrite  0x802b42ac
```

This allows the general scanner to determine current catalog file lengths dynamically instead of embedding Test06b's staged resource sizes.

## Stable-merge implementation consequence

The next Refresh writer no longer needs `Resources/refresh.bin`.

For the first real scanner candidate, the safe mutation remains:

1. scan a real built-in ROM folder through `0x807d40c4 / 0x807d4124 / 0x807d41f4`;
2. reject directories;
3. apply the stock extension classifier `0x80360a08`;
4. load slot-0/1/2 catalogs dynamically;
5. preserve every existing index and byte sequence;
6. identify discovered filenames absent from slot 0;
7. append only new filenames;
8. append basename fallbacks to slots 1 and 2;
9. never delete and never reorder;
10. fs-sync and invalidate only `count[list_id]` after a fully successful triplet write.

This is the real discovery + stable-merge path requested after Test06b.

## Candidate scope decision

The first hardware candidate should remain **SFC-only** while using real discovery, because SFC already has the hardware-proven `XGO Import Test.zsf` wrapper and known-good 929/930 catalog behavior. The difference from Test06b is fundamental: the firmware must discover the physical SFC directory and compute the append itself; no staged 930-entry `refresh.bin` may be present.

Once this passes, the same engine can be generalized over FC/SFC/MD/GB/GBC/GBA and then evaluated separately for curated Arcade pages.

## Transaction boundary

This finding closes discovery ABI, not power-loss recovery. The first general-scanner hardware candidate should still run only on the disposable clone unless it also implements the previously designed backup/transaction-marker recovery protocol.

Do not regress Test06b UI/status behavior while introducing the scanner.
