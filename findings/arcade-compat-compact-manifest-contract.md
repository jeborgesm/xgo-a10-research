# Arcade compatibility manifest — compact binary contract

Date: 2026-09-26
Branch: `research-arcade-refresh-four-family`
Status: **FORMAT + ROUND-TRIP AUDIT TOOLING LOCKED**

The verbose JSON manifest is an audit artifact, not the on-device representation.

A deterministic binary format, `XACM v1`, is now defined for the external
Refresh validator.

## Header

```
magic             4   "XACM"
version           2   1
family_count      2   4
driver_count      4
rom_count         4
string_bytes      4
firmware_sha256  32
```

The exact source firmware SHA-256 is therefore carried inside the binary
manifest itself.

## Tables

Four fixed family rows identify CPS1, CPS2, IGS and NEOGEO and delimit their
sorted driver ranges.

Each driver row is 20 bytes:
- short-name string offset;
- parent-name string offset;
- board-ROM-name string offset;
- first ROM-record index;
- ROM-record count;
- family index;
- reserved byte.

Each ROM row is 16 bytes:
- name string offset;
- expected uncompressed size;
- expected CRC32;
- original XGO/FBA type flags.

All strings occupy one deduplicated NUL-terminated ASCII pool. Offset zero means
NULL.

## Determinism

Drivers are sorted by fixed family order then short name. Strings are allocated
on first deterministic encounter. No host timestamps, object ordering or ZIP
metadata enter the format.

The compiler fails closed if the extracted target population is not exactly:

```
CPS1    154
CPS2    232
IGS      34
NEOGEO  258
```

## Independent round-trip audit

`audit_arcade_compat_manifest.py` decodes the binary representation and checks
every driver and every ROM tuple against the source JSON:
- family;
- short name;
- parent;
- board archive;
- ROM name;
- size;
- CRC;
- type flags;
- firmware SHA.

This prevents compaction from silently changing compatibility semantics.

## Repository tooling

- `tools/arcade_refresh/compile_arcade_compat_manifest.py`
- `tools/arcade_refresh/audit_arcade_compat_manifest.py`

The next package gate is to run the compiler/auditor against the exact generated
manifest and establish the actual byte size/hash before selecting whether the
XACM blob is loaded as a sidecar or appended to the external helper.

No Test05 yet.
