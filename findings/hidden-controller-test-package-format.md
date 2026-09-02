# XGO Hidden Controller Test Package Format

Status: **`Resources/Test.zsf` fully carved as a thumbnail + WQW/ZIP package; inner controller-test ROM name, size, compression and hashes recovered.**

## Major finding

The hidden diagnostic launched by `L + SELECT` is stored as:

```text
Resources/Test.zsf
size: 93,867 bytes
```

The file follows the SF2000-family `.zsf` packaged-ROM layout exactly:

```text
0x0000..0xE9FF   0xEA00 bytes / 59,904 bytes
                 raw 144x208 RGB565 thumbnail

0xEA00..EOF      WQW-wrapped ZIP/Deflate archive
```

The thumbnail itself visibly shows a Super Famicom controller-test screen with:

```text
SUPER FAMICOM
PRESS KEY:
TIME=00
```

and a Super Famicom controller illustration.

## WQW archive structure

The WQW payload begins at exact file offset:

```text
0xEA00
```

Its first bytes are:

```hex
57 51 57 03 14 00 00 00 08 00 ...
 W  Q  W  03
```

Three WQW signatures occur in the payload:

```text
relative 0x0000  -> WQW 03   local-file record
relative 0x841E  -> WQW 02   central-directory record
relative 0x8495  -> WQW 01   end-of-central-directory record
```

The surrounding fields line up exactly with ordinary ZIP structures. Replacing only those four-byte markers with the standard ZIP signatures:

```text
WQW 03 -> PK 03 04
WQW 02 -> PK 01 02
WQW 01 -> PK 05 06
```

produces a structurally valid ZIP file that ordinary ZIP tooling can decompress successfully.

This substantially narrows the WQW format used here: **the compression stream, CRC, sizes, central directory and normal ZIP field layout are preserved; the main obfuscation is altered record signatures plus the legacy filename bytes.**

## Exact inner-file metadata

Parsing the local record yields:

```text
compression method: 8 (Deflate)
compressed size:    33,755 bytes
uncompressed size:  131,072 bytes (128 KiB)
CRC-32:             EDF7EBB9
legacy filename len: 12 bytes
extra-field len:     25 bytes
```

The 12-byte legacy ZIP filename is intentionally scrambled/non-textual:

```hex
2f 33 54 1f 57 07 2f 31 cb 96 83 86
```

However, the local and central records contain the standard Info-ZIP Unicode Path extra field (`0x7075`). Its UTF-8 filename is:

```text
手柄测试.sfc
```

which translates directly as:

```text
Controller Test.sfc
```

or literally `Handle/Controller Test.sfc` (`手柄` = handheld controller/gamepad, `测试` = test).

This is **CONFIRMED metadata embedded by the ROM packager**, not a name inferred from the XGO menu behavior.

## Extracted ROM

Raw Deflate decompression of the inner payload succeeds without modification.

Recovered ROM properties:

```text
size:    131,072 bytes
CRC-32:  EDF7EBB9
MD5:     64934a22a04d044c4d6b295cdfbba89e
SHA-1:   b93c39c683ba3be4c8f7b4fc120444fe0510568e
```

The decompressed CRC exactly matches the CRC stored in the package header.

ASCII strings in the ROM include:

```text
NINTENDO
PRESS KEY!
PLEASE SET CONTROLLER
TIME=00
```

No matching public source/repository was found from those strings in the initial search, so the current evidence is that this is a small vendor/OEM controller-test program rather than an immediately identifiable commercial Super Famicom ROM.

The ROM does not present a conventional readily readable SNES title/header at the usual LoROM/HiROM header locations, so its exact build provenance remains open.

## Why this matters

This closes several questions around the hidden diagnostic:

1. `Test.zsf` is genuinely an SFC/Super-Famicom packaged ROM, not native H1512 diagnostic code disguised as one.
2. The firmware's normal SFC emulator path is being used to execute the test.
3. The packager explicitly names the inner payload `手柄测试.sfc`, proving its intended purpose independently of our physical reproduction.
4. The test package provides a known-good real-world WQW specimen whose entire archive structure can now be reconstructed.
5. WQW on this card is weak obfuscation around ordinary ZIP/Deflate rather than a fundamentally different compression format.

This also means other XGO `.zfc/.zsf/.zmd/.zgb` packages can be carved using the same approach: skip the 0xEA00 thumbnail, parse the WQW records as ZIP records with substituted signatures, honor Unicode-path extra fields where present, and inflate the payload normally.

## Reconstructed WQW-to-ZIP transformation for this specimen

Conceptually:

```text
input = Test.zsf[0xEA00:]

replace local signature:
    57 51 57 03 -> 50 4B 03 04

replace central signature:
    57 51 57 02 -> 50 4B 01 02

replace end signature:
    57 51 57 01 -> 50 4B 05 06
```

After those substitutions, standard ZIP parsers can walk the archive and decompress the 128 KiB ROM. Some parsers will still display the scrambled legacy filename because they do not honor the Unicode Path field when the legacy bytes are not valid text; the authoritative embedded UTF-8 name remains available in extra field `0x7075`.

## Confidence

### CONFIRMED

- `Test.zsf` has a 0xEA00-byte 144x208 RGB565 thumbnail;
- WQW archive begins exactly at 0xEA00;
- WQW records map structurally to ZIP local/central/end records;
- compression method is normal Deflate;
- stored compressed/uncompressed sizes are 33,755 / 131,072 bytes;
- stored CRC-32 is `EDF7EBB9` and matches the decompressed ROM;
- Unicode Path field names the inner ROM `手柄测试.sfc`;
- ROM contains `PRESS KEY!`, `PLEASE SET CONTROLLER`, `TIME=00`, and `NINTENDO` strings;
- ROM hashes are recorded above;
- replacing the three WQW signatures with their normal ZIP equivalents yields a decompression-compatible archive.

### STRONG EVIDENCE

- this is a vendor/OEM controller-test SFC program rather than a commercial game;
- the WQW format used by this specimen is deliberately superficial ZIP obfuscation.

### OPEN

- original source/build provenance of `手柄测试.sfc`;
- whether all XGO WQW packages use precisely the same three signature substitutions and filename scrambling method;
- algorithm used to scramble the 12-byte legacy filename;
- detailed internal logic of the SFC diagnostic ROM itself;
- whether the ROM was authored specifically for this product family or inherited from an earlier OEM test suite.
