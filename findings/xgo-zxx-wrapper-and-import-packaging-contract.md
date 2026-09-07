# XGO Zxx wrapper and import packaging contract

Date: 2026-09-06
Branch: `research-game-list-scanning`

Status: **wrapper structure and WQW payload contract confirmed from XGO; deterministic STORE-mode builder added; Test03 scratch candidate audited cleanly**

## Exact XGO wrapper boundary

Captured XGO `Resources/Test.zsf`:

- size: 93,867 bytes
- SHA-256: `8e661f5a9246091228dd2eedae65c109d2add7aa3c22cc0231c39dd67b3600f4`

The first 59,904 bytes are thumbnail data.

At exact offset:

`0xEA00 = 59,904`

the payload begins with:

`WQW\x03`

This proves the XGO Zxx wrapper layout:

```text
[thumbnail RGB565 bytes]
[WQW-obfuscated ZIP archive]
```

## Thumbnail size is configuration-derived

The stock `run_game()` call sites compute the package preview size immediately before calling the launcher.

At approximately `0x80357370..0x80357388`, firmware loads two frontend globals, multiplies them, then shifts left by one before passing the result as `run_game(..., preview_size)`.

The second package call path around `0x80359050..0x80359068` performs the same operation.

Therefore:

`preview_size = thumbnail_width * thumbnail_height * 2`

The shipped XGO `Resources/Foldername.ini` defines thumbnail geometry:

`472 144 144 208`

where the family format identifies the final pair as width/height.

`144 * 208 * 2 = 59,904`

matching the observed XGO wrapper boundary exactly.

This means the prefix size is derived from the configured RGB565 thumbnail dimensions rather than being an unrelated magic constant.

## WQW is lightly obfuscated standard ZIP

Family source documents three WQW signatures:

- local file header: `0x03575157` = bytes `WQW\x03`
- central directory: `0x02575157` = bytes `WQW\x02`
- end-of-central-directory: `0x01575157` = bytes `WQW\x01`

Stored filenames in local and central records are XORed byte-for-byte with `0xE5`.

The compressed payload bytes, CRC, sizes, and ordinary ZIP record structure remain standard.

## XGO de-obfuscation proof

The WQW payload from captured `Test.zsf` was converted back to a normal ZIP by only:

1. restoring the three standard ZIP signatures;
2. XOR-decoding stored filenames with `0xE5`.

Python's standard ZIP implementation then opened the archive and verified its CRC successfully.

The XGO package contains one SNES ROM:

`手柄测试.sfc`

compressed with ordinary DEFLATE.

Therefore XGO does not require a proprietary compressor for Zxx wrappers.

## Stock runtime parser

XGO's packaged-content path uses the already-mapped helpers:

- `unwqw_init = 0x80365c4c`
- `unwqw_decompress = 0x80365d70`
- `unwqw_free = 0x80365de4`

`run_game()` passes the computed preview size to `unwqw_init(path, preview_size, 2)`.

## Minimal on-device packaging implication

A handheld importer does not need image libraries or a ZIP compressor if we constrain the first implementation.

A minimal pipeline can be:

```text
already-prepared 144x208 RGB565 thumbnail
+
raw ROM
->
ZIP method 0 (STORE) records
->
replace ZIP signatures with WQW variants
->
XOR filenames with 0xE5
->
concatenate thumbnail + WQW
```

Method 0 is intentionally attractive for the first hardware proof because it removes DEFLATE generation from the device-side implementation.

## Test03 scratch candidate audit

Recovered after the chat stream failure:

`xgo-game-list-test03-sfc-import-store-wrapper.zip`

ZIP SHA-256:

`bfef6f95adaf7cd986061154d20e500580135930426994b5ed3b44c822987320`

It creates:

`SFC/XGO Import Test.zsf`

Wrapper SHA-256:

`f600c45d37a77d9af80ecb1ad136e1dbcfbb7e22fd9afc91531f82cfd2fb03b1`

Wrapper audit:

- thumbnail prefix exactly 59,904 bytes;
- WQW local magic valid;
- one payload named `XGO-Import-Test.sfc`;
- ZIP method 0 / STORE;
- compressed size = uncompressed size = 131,072;
- payload CRC32 matches header;
- payload SHA-256 `76e60393139669b25c5a82247c3fbbc6f2a9715049532b2d14991adbec60ac9b`;
- valid WQW central and end records;
- SFC catalog triplet goes 929 -> 930;
- all 929 original offset words remain byte-identical;
- all original string-blob bytes remain byte-identical.

## Repository builder

`tools/game_lists/build_wqw_store_wrapper.py`

implements a deterministic one-ROM WQW STORE wrapper using an already-converted RGB565 thumbnail.

## Scope boundary

Image conversion itself is still a separate concern.

Generating RGB565 from PNG/JPEG on-device would require either:

- a decoder for those image formats; or
- a much simpler import convention where the user supplies a preconverted `.rgb565`/raw cover asset.

The current wrapper work proves that once RGB565 thumbnail bytes exist, packaging the ROM itself is small and straightforward.

## Next dig

1. finish audit/recovery of Test03 private-vault staging;
2. hardware-test the newly generated STORE-mode wrapper;
3. if it passes, treat WQW generation as hardware proven;
4. then determine the cheapest cover-image import contract for the handheld;
5. only after wrapper and catalog append are both proven, combine them into an on-device Import/Refresh workflow.