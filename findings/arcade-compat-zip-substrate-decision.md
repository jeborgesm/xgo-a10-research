# Arcade compatibility validator — ZIP substrate decision

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **IMPLEMENTATION SUBSTRATE LOCKED**

## Reuse-first result

The repository contains no already-isolated Refresh helper that exposes stock
FBA `ZipOpen/ZipGetList` as a safe external-helper ABI.

The pinned stock FBA source does define the required archive interface:
`ZipOpen`, `ZipGetList`, `ZipClose`, with each `ZipEntry` exposing
name, uncompressed length and CRC.

However, calling those stock internals from the Refresh helper would reintroduce
the same resident-core coupling deliberately avoided by the manifest design:
unknown internal globals, allocation ownership and archive state.

The compatibility gate does not need decompression. It needs only metadata that
standard ZIP stores in its central directory.

## Selected substrate

Implement a **read-only ZIP central-directory parser** in the external Refresh
helper.

Required operations only:
1. open imported ZIP with already-proven native FILE callbacks;
2. obtain file length;
3. locate EOCD signature from the bounded ZIP tail;
4. reject ZIP64/multidisk/encrypted/unsupported structural cases for the first
   implementation;
5. read central-directory entries sequentially;
6. expose:
   - member basename/name,
   - CRC-32,
   - uncompressed size;
7. compare against the firmware-bound manifest;
8. close the file.

No payload decompression and no archive rewriting are required.

## Why this is the narrower reuse choice

The materializer lineage already uses the native XGO FILE callback ABI for
ordinary SD-card reads/writes. A metadata-only parser therefore adds format
parsing but no new filesystem ABI and no decompressor.

This keeps compatibility validation independent from:
- resident FBA globals;
- FBA ZipOpen/ZipClose state;
- FBA allocator ownership;
- emulator/core lifetime.

## Fail-closed structural rules

A malformed or unsupported ZIP cannot be published.

The parser must reject:
- missing/ambiguous EOCD;
- central directory outside file bounds;
- entry count/offset/size overflow;
- malformed central-directory signature;
- filename/extra/comment lengths exceeding remaining directory bytes;
- ZIP64 sentinel sizes/offsets until ZIP64 is explicitly implemented;
- multidisk archives;
- encrypted entries when that affects loader compatibility.

A parser/internal failure is distinct from a clean ROM incompatibility verdict;
do not rename a source `.incompatible` for an internal parser failure.

## Matching note

The pinned stock loader's CRC-first lookup is followed by filename fallback and
then a size-state check. The on-device validator must preserve that ordering.

The validator does not need to calculate CRC over ROM payload bytes because ZIP
central-directory CRC is exactly the metadata the stock archive list exposes.
This also keeps Refresh fast and avoids reading/decompressing every ROM.

## Remaining work

- implement/audit the bounded parser;
- choose compact manifest encoding suitable for helper size/memory;
- integrate verdict before materialization/publication;
- close recoverable quarantine/move semantics separately.

No Test05 yet.
