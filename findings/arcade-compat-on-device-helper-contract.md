# XGO Arcade compatibility helper — on-device implementation contract

Date: 2026-09-27
Branch: `research-arcade-refresh-four-family`
Status: **OFFLINE IMPLEMENTATION CONTRACT CLOSED — no Test05**

The host XACM + bounded-central-directory regression is now translated into a
device-side contract using only XGO services whose addresses/ABI already exist
in repository evidence.

## Placement and responsibility

Compatibility validation stays in an external helper, before materialization
publishes ZIP/ZFB/marker/catalog state.

```
family import ZIP
 -> compat helper
      -> /ARCADE/.xgo-compat (XACM v1, read only)
      -> imported ZIP central directory (read only)
      -> verdict
 -> only COMPATIBLE may enter existing materializer publication path
```

The 237,921-byte XACM is a sidecar, not linked into the approximately 1 MiB
materializer.

## Proven stock I/O surface

The repository already closes these stock stdio services:

```
fopen   0x802B3524
fread   0x802B3698
fseeko  0x802B3804
ftell   0x802B3F1C
fclose  0x802B2F40
```

The generic Refresh scanner finding independently records the same surface.
The external-core work additionally proves these stock services execute in the
stock `$gp` domain. Therefore an independently linked external C helper must
use the already-proven core->stock GP veneer pattern; direct calls from an
external `_gp` domain are not safe.

This does not require a new filesystem ABI.

## Bounded memory design

Do not load the 237,921-byte XACM or a whole imported ZIP into RAM.

XACM lookup is streaming/random-access:
1. read and validate 52-byte header;
2. verify magic/version/family count and exact expected file size from table
   counts/string bytes;
3. verify the embedded firmware SHA against the package-time expected SHA;
4. read the selected 12-byte family row;
5. walk only that family's 20-byte driver rows;
6. resolve strings from the string pool with bounded reads;
7. once family+stem matches, stream only that driver's 16-byte ROM records.

ZIP validation is likewise metadata-only:
1. seek end and obtain file length;
2. read at most the final 65,557 bytes;
3. find the last EOCD signature;
4. reject malformed comment termination, multidisk and ZIP64;
5. validate central-directory offset/size against file length;
6. stream 46-byte central headers plus bounded variable name/extra/comment;
7. reject encrypted, ZIP64 or malformed entries;
8. compare basename/CRC/uncompressed-size metadata only.

No decompression and no ROM payload reads are required.

A small fixed scratch allocation is therefore sufficient: tail buffer <=65,557
bytes, bounded filename/string buffers, and a few table records. This avoids
coupling validation to the large materializer image or FBA allocator/global
state.

## Matching semantics

For each nonzero, nonoptional game descriptor:
1. CRC match first;
2. CRC hit must have expected uncompressed size;
3. otherwise expected filename fallback is accepted, preserving stock
   wrong-CRC fallback behavior;
4. unresolved required descriptor => INCOMPATIBLE.

All-zero descriptor slots are satisfied. Optional descriptors are skipped.
Parent/board dependency names remain metadata and are not incorrectly demanded
from the game ZIP.

## Verdict ABI

Use a narrow integer result, independent of UI:

```
 0  COMPATIBLE
 1  INCOMPATIBLE
 2  UNSUPPORTED
-1  VALIDATOR_ERROR
```

COMPATIBLE alone may proceed to ZIP/ZFB/marker/catalog publication.
INCOMPATIBLE and UNSUPPORTED publish nothing.
VALIDATOR_ERROR fails the family Refresh operation closed.

Quarantine rename remains a separate VFS problem: do not reinterpret the
unclosed two-path VFS operation as rename merely to implement
`.incompatible`. Nonpublication is already safe without rename.

## Firmware binding

XACM's embedded firmware SHA is not intended to make the device compute SHA-256
over 12.7 MiB at Refresh time. Packaging already knows the exact firmware being
patched and must reject a sidecar generated for another firmware. The helper
then compares XACM's embedded SHA with the 32-byte expected SHA compiled into
that candidate/helper. This keeps the database and firmware contract pinned
without adding a new on-device hash implementation.

## Implementation consequence

The next code artifact should be a small external compatibility helper with:
- GP-safe stock stdio veneers;
- bounded XACM reader;
- bounded ZIP central-directory reader;
- the four-result verdict ABI;
- no publication writes.

It can be mechanically host-tested before being spliced into command6. The
existing four specialized materializers remain publication owners; the
compatibility helper is a precondition, not a replacement.

No Test05 is authorized by this contract.
