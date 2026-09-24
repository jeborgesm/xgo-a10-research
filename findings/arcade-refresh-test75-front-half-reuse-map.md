# Arcade Refresh - Test75 front-half reuse map

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: DIRECT BIN ANALYSIS FROM GOLDEN TEST75

Source: golden FC/refresh.xgc SHA-256
8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e

## Directory enumeration

The helper opens the fixed import directory and iterates directory entries using
the stock firmware directory wrappers. The active filename is held at
0x87600008.

Test75 literals:
- /mnt/sda1/FC/import at helper +0x0FE7
- %s/%s at +0x0FFD
- /mnt/sda1/FC at +0x1003

The extension filter is implemented in low code, not in the directory API.
For FC it case-folds the final three extension characters and requires n/e/s.
This is one of the four code-immediate substitutions already observed between
Test74 and Test75.

Arcade consequence: preserve the enumeration skeleton but specialize the
filter to .zip. Family identity must come from the selected descriptor/input
folder, never from ZIP introspection.

## Source stem and friendly title

Helper function +0x0DCC derives a source stem into 0x87600500.

The main path then probes:
  /mnt/sda1/FC/meta/%s.txt

If readable, it consumes a bounded first line, rejects control/invalid filename
characters through helper +0x0E6C, substitutes underscore for rejected
characters, and trims trailing spaces. If no usable metadata title remains,
the source-derived stem is sanitized through the same helper and used instead.

This is the exact behavior behind the HW-proven friendly-title fallback and is
safe to retain conceptually for Arcade.

The sanitizer explicitly rejects control bytes plus filename-hostile
characters including backslash, vertical bar and asterisk; the bitmask branch
also covers the other punctuation rejected by the existing implementation.

## Destination identity and collision behavior

The sanitized friendly title is assembled in the output-name workspace and
the console wrapper suffix is appended. For Test75 the packed literal is
.zfc.

The destination pathname is then built under the system root. Before creating
a new wrapper the helper attempts to open the destination for reading. If it
already exists, it closes it and skips materialization rather than overwriting
it.

This is the HW-proven non-destructive outer-wrapper collision behavior.

Arcade consequence:
- retain the no-overwrite rule;
- replace .zfc with .zfb;
- root becomes /ARCADE, not the family import directory;
- strengthen the old simple existence check with the already-built Arcade
  collision planner: parse existing ZFB and require the same embedded driver
  before treating it as reusable.

## Artwork sidecar resolution

The helper constructs/probes, in order:
  /mnt/sda1/FC/art/%s.jpg
  /mnt/sda1/FC/art/%s.jpeg

using the source stem, not the friendly display title.

This distinction is important and should remain for Arcade:
  import/dino.zip
  meta/dino.txt -> Cadillacs and Dinosaurs
  art/dino.jpg
  output /ARCADE/Cadillacs and Dinosaurs.zfb

The decoder scratch paths are independent fixed files and are cleaned before
decode, as recorded in the low-code ABI finding.

## What is reusable and what is not

Reusable from the golden front half:
- directory iteration skeleton;
- bounded filename handling;
- metadata first-line lookup;
- friendly-title fallback;
- filename sanitization;
- JPG then JPEG sidecar lookup;
- non-destructive destination existence gate;
- scratch cleanup and proven decoder path;
- exact 0xEA00 preview copy/fallback.

Must change for Arcade:
- import root selected from four family descriptors;
- extension filter .zip;
- source stem removes .zip;
- runtime ZIP destination is /ARCADE/bin/<driver>.zip;
- byte-identity collision check for an existing runtime ZIP;
- outer suffix .zfb;
- outer root /ARCADE;
- existing ZFB must be parsed and checked against driver identity;
- no WQW packaging after preview;
- append Arcade trailer at the proven +0x09B4 boundary;
- catalog mutation remains a separate stage.

## Architectural result

The materializer does not need a wholesale rewrite. The safe implementation is
a specialization of the HW-proven Test75 front half plus two Arcade-specific
asset checks/copies, followed by the already-closed ZFB trailer writer.

The catalog helper remains independent, preserving the two-stage architecture
that passed SFC/FC/GB/GBC/GBA.
