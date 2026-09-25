# Arcade manifest iterator — source construction milestone

Date: 2026-09-24
Branch: research-arcade-refresh-four-family
Status: SRC; no candidate emitted

The source-built replacement for the GBA directory iterator has started at:
tools/arcade_refresh/build_manifest_iterator_source.py

Frozen validation contract:
- basename only;
- ASCII only;
- length 5..127 bytes;
- no NUL, slash, backslash, CR or LF inside an identity;
- case-insensitive .zfb suffix;
- bounded 128-byte read buffer;
- 1 = candidate, 0 = EOF, negative = malformed/I/O failure.

The iterator is intentionally not allowed to serialize or rewrite catalog
triplets. Its only output is one validated outer ZFB identity in the same
current-name workspace consumed by the inherited GBA exact-comparison engine.

Next binary-builder work must bind the exact stock fopen/fread/fclose callbacks
already present in the golden helper, choose scratch state that does not collide
with its missing-entry/catalog workspaces, compile/link little-endian MIPS, and
audit relocations/back-edges before any package exists.
