# XGO on-device import feasibility — stock ZIP creator and image stack

Date: 2026-09-06

Status: **ZIP creation capability strongly identified; still-image decoder reuse remains open**

## Stock ZIP creator is present

The XGO firmware contains the exact diagnostic/error-string family from Lucian Wischik's XZip/XUnzip implementation, including:

- `Caller: additions to the zip have already been ended`
- `Caller: mixing creation and opening of zip`
- `Zip-bug: an internal error during flation`
- `unknown compression method`
- `UnzipItem failed`

It also contains the zlib/deflate banner:

`deflate 1.2.5 Copyright 1995-2010 Jean-loup Gailly and Mark Adler`

Open-source copies of that exact library expose the creation API:

`CreateZip(...)`
`ZipAdd(...)`
`CloseZip(...)`

and support both DEFLATE and STORE methods.

This is strong code-lineage evidence that the XGO binary contains ZIP creation logic in addition to the already-mapped OpenZipU/UnzipItem/CloseZipU-style extraction path.

Exact XGO addresses for CreateZip/ZipAdd/CloseZip are not yet labeled and remain a reverse-engineering target.

## Import consequence

If those creator entry points can be mapped and called safely, the handheld does not need a new compression library for raw-ROM import.

Potential on-device flow:

`raw ROM -> stock CreateZip/ZipAdd/CloseZip -> WQW transform -> prepend RGB565 thumbnail -> .zxx`

The WQW transform itself is trivial and already byte-perfectly proven.

## Image decoding

The firmware contains multimedia/image strings including:

`image/jpeg`
`image/png`
`JPEG scan type no support!`
`MJPG decore`

and a substantial media-engine decoder subsystem.

However, the MIME strings are embedded in a broader media-type table, and the JPEG diagnostics belong to the multimedia engine. This proves JPEG/PNG-related code exists in the firmware but does not yet prove a small reusable still-image API that directly yields an RGB framebuffer.

Therefore image handling remains the harder half of a fully user-friendly on-device importer.

## Proven RGB565 thumbnail representation

Decoding the first 59,904 bytes of XGO `Resources/Test.zsf` as little-endian RGB565 at 144x208 produces the expected Super Famicom controller-test cover image.

This independently verifies:

- dimensions 144x208;
- 2 bytes per pixel;
- RGB565 channel layout;
- little-endian 16-bit storage;
- row-major pixel order.

## Recommended staged importer

1. `Refresh Games`: scan ready-made `.zxx` wrappers and stable-append missing catalog entries.
2. `Import Prepared Game`: accept raw ROM plus a 144x208 `.rgb565` cover; use stock ZIP creator and WQW wrapper writer.
3. `Import Game`: later accept PNG/JPEG once a convenient stock decoder API is mapped or a small decoder is ported.

This staged plan reaches PC-independent game import without making PNG/JPEG decoding a blocker for the catalog scanner.