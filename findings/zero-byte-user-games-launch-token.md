# Zero-byte XGO User Games launch token

Status: **confirmed statically** for the stock User Games browser + `run_game()` launch path.

## Result

A synthetic external-core token such as:

```text
/ROMS/fceumm;ScienceFrog.nes.gba
```

may be **zero bytes long**.

The stock XGO frontend uses only its filename/extension to list and dispatch it. No valid GBA header or payload is required before the patched external-core hook receives the path.

## User Games scanner

The active frontend directory scanner is around `0x80353ae0..0x80353db4`.

It opens the active user-games directory at:

```text
0x80353b4c  call directory-open wrapper 0x807d40c4
```

and iterates entries through:

```text
0x80353ba8  call directory-next wrapper 0x807d4124
```

For each entry:

```text
0x80353bb8  read directory/file flag
0x80353bbc  skip directory entries
0x80353bc4  strlen(filename)
0x80353bd4  locate '.' extension separator
0x80353be0  uppercase extension
0x80353be8  call system-extension classifier 0x80360a08
0x80353bf0  reject only if classifier returns negative
```

The accepted filename is then copied into the frontend list and its counters/pointers are updated.

There is no file-size test and no file-open/header-read step in this acceptance loop.

## Directory wrapper confirms size is discarded

The directory-next wrapper at `0x807d4124` calls the lower `fs_readdir` layer and constructs the frontend-facing entry.

Its relevant behavior is:

```text
0x807d4174  fs_readdir
0x807d41a4  load raw entry mode/type field
0x807d41a8..b4
            reduce mode to directory/not-directory flag
0x807d41b8..c4
            copy filename from raw entry +0x22
```

It does not copy or inspect the file-size fields from the raw directory entry. The frontend therefore cannot reject a file for being zero bytes through this wrapper.

## Same classifier as launch dispatcher

The scanner calls `0x80360a08`, the same 40-entry extension classifier used by `run_game()`.

Relevant table entries at runtime `0x80a3c4c8` are:

```text
19  GBA  -> 0x10
20  AGB  -> 0x10
21  GBZ  -> 0x10
```

Therefore a filename ending in `.gba` is accepted as GBA-family User Games content solely from its extension.

## `run_game()` also does not read GBA-family token bytes

At `0x80360b88`, `run_game()` classifies the extension first.

For family `0x10` it bypasses the generic open/seek/read/preload path at `0x80360c14..0x80360c8c` and goes directly to:

```text
0x80360cf0  move $4,$18       ; selected token path
0x80360cf4  jal  run_gba      ; patched to injected loader
0x80360cf8  move $5,$zero     ; load_state = 0
```

Thus the token bytes are not consumed by the browser or the GBA dispatch path before our hook.

## Card-layout corroboration

The preserved XGO card already stores ordinary User Games directly under `/ROMS`, including `.nes`, `.gb`, `.smc`, and `.gba` files. The external-core staging convention therefore uses:

```text
/ROMS/fceumm;Game.nes.gba     zero-byte browser-visible token
/ROMS/fceumm/Game.nes         real NES ROM
```

The real-ROM subdirectory is intentionally separate from the browser-visible token. The FCEUmm bridge removes only the final synthetic `.gba` suffix and reconstructs the second path.

## Tooling consequence

`tools/multicore/stage_fceumm_test.py` now creates the zero-byte `.gba` token automatically. It still does **not** copy, modify, or fabricate the actual NES ROM.

This closes the last known static uncertainty in the Multicore-style launch-token mechanism itself. Physical hardware execution remains the next validation layer.
