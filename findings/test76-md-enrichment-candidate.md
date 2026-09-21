# Test76 — MD enrichment hardware candidate

Status: **OFFLINE AUDITED — awaiting hardware test**

## Parent

Test76 is additive to the exact hardware-passed Test75 FC baseline.

- Parent ZIP: `xgo-stock-test75-fc-enrichment-proof.zip`
- Parent ZIP SHA-256: `2a550aded4f37ce0b05488f54f30ad5de9295287f446a2f2a593737d615fc686`

Protected SFC, FC, CLASSIC, mapper, Audio OSD, stock console and stock Arcade behavior is retained.

## MD documentary closure

The stock MD catalog triplet in the analyzed image contains 788 aligned entries:

- `scksp.tax` — 22,156 bytes; physical wrapper names; SHA-256 `d04479d8214233d417ebf1791aa38b030a89b9ee55657c586c997257301bba01`
- `setxa.nec` — 15,984 bytes; localized titles; SHA-256 `835be147cfb05da648385667da6ad5c81467a281ecfa8f71d60bf50d01d8197c`
- `wmiui.bvs` — 8,160 bytes; search/pinyin; SHA-256 `60acca83cbcd3086a1f27c2f9c2f192474759d1711f0adf8c9b9e3419a3bf1a8`

The first physical records include `16T.zmd`, `3 Ninjas Kick Back.zmd`, and `A Dinosaur's Tale.zmd`, confirming `.zmd` as the stock packaged MD namespace. Existing launcher archaeology already maps ZMD through the common packaged-console route. A direct representative stock `.zmd` byte capture is still desirable, so this candidate is the MD hardware proof rather than a claim of direct byte-level wrapper proof.

## Candidate behavior

Adds:

- `/MD/refresh.xgc`
- `/MD/catalog.xgc`

First proof input is deliberately limited to native `.bin`:

- `/MD/import/<stem>.bin`
- `/MD/art/<stem>.jpg` or `.jpeg`
- `/MD/meta/<stem>.txt`
- generated `/MD/<friendly-or-basename>.zmd`

The materializer is a family-specific derivation of the hardware-passed FC/SFC helper. The generated wrapper family is ZMD; native proof classifier is BIN. JPEG conversion/scaling, WQW STORE packaging, no-overwrite semantics, batch behavior and source retention are unchanged.

The catalog helper uses `scksp.tax / setxa.nec / wmiui.bvs`, scans top-level `/MD` for `.zmd`, preserves existing order/indexes, appends missing wrappers, and uses the list-2 count-cache slot `0x80D2895C`, following the established 8-byte-per-list cache table (`FC list 0 = 0x80D2894C`, `SFC list 1 = 0x80D28954`, `MD list 2 = 0x80D2895C`). This address progression should remain documented as table-derived evidence until independently observed through a direct MD-specific runtime reference.

## Dispatcher

The Test75 additive pre-scan dispatcher is extended to run, in order:

1. FC materializer
2. FC catalog merge
3. SFC materializer
4. SFC catalog merge
5. MD materializer
6. MD catalog merge
7. existing six-console scanner
8. existing Test72 CLASSIC path

Any helper failure routes to the existing Refresh Failed path. Any helper change contributes to Games Updated. An unchanged run must retain No New Games semantics.

## Candidate identity

- ZIP: `xgo-stock-test76-md-enrichment-proof.zip`
- ZIP SHA-256: `a96b1828cb6deb6e2cc894d8472a75697655cc7c8e0a5bd5eb74524f1affb522`
- firmware SHA-256: `11f2faf849570ea9dc9572e86a536636ef6937dbac7fa0b85a3abc92769823b7`
- LCFG CRC-32/MPEG-2: `0x4E6B600B`
- `/MD/refresh.xgc` SHA-256: `fed8accaa61a34dc706a1aca5b442923ad65130df9a3517fafce6985fff094ab`
- `/MD/catalog.xgc` SHA-256: `2604672d00ec25f49a96e05214b1a3421b35717d04098800309bd08b26077645`
- MD helper size: 1,056,520 (`0x101F08`)
- MD catalog helper size: 2,642 bytes
- expanded dispatcher: 428 bytes, ending at `0x80A3863C`, within the protected cave ending at `0x80A391F8`

ZIP integrity audit passed.

## Explicit exclusions

- No removal implementation is introduced. Catalog behavior remains append-only; standardized removal is deferred as a separate cross-family feature.
- No PNG support is reintroduced.
- This first MD candidate accepts `.bin` only even though the generic stock scanner recognizes additional MD-family native extensions. Broader materializer acceptance can be generalized after the family-specific proof.
- No GB/GBC/GBA enrichment is included yet.

## Hardware gate

Use a known-good MD `.bin` with matching JPG and metadata. First Refresh should report Games Updated; the generated friendly `.zmd` should appear with artwork and launch through the stock MD emulator. Verify existing MD, FC and SFC entries still launch. A second unchanged Refresh must report No New Games without duplication.
