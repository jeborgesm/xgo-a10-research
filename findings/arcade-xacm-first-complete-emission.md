# XACM v1 first complete emission

Date: 2026-09-26
Status: OFFLINE MECHANICALLY AUDITED — NOT HW

Exact firmware SHA256: `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.

Observed firmware population, not limits: CPS1 154, CPS2 232, IGS 34, NEOGEO 258; total 678.

Deterministic JSON: 991,463 bytes, SHA256 `c78e74bafe327dda636f36932024c010e84d9b6e4236a63ea62e458dc7cfd6df`.

XACM v1: 237,921 bytes, SHA256 `86a798ab9e0c8042a84b99a37fcfacd8708706d0010e0459726420d92ab7c0f5`; 10,404 ROM records; 57,797 string bytes; 24.00% of JSON size.

Family ranges: CPS1 first 0 count 154; CPS2 first 154 count 232; IGS first 386 count 34; NEOGEO first 420 count 258.

Independent decode/round-trip audit passed for firmware SHA, family ranges, every driver name/parent/board tuple, every ROM name/size/CRC/type tuple, counts and bounds.

Known fixture regression: `1941(1).zip` is INCOMPATIBLE with four unresolved program ROMs (`41e_30.rom`, `41e_35.rom`, `41e_31.rom`, `41e_36.rom`) and no size mismatches. `1941(2).zip` is COMPATIBLE with zero unresolved descriptors and zero size mismatches. This reproduces the known hardware distinction.

At 237,921 bytes, the preferred first deployment is a firmware-SHA-bound read-only SD sidecar such as `/ARCADE/.xgo-compat`, rather than embedding compatibility metadata into the 1 MiB materializer.

No ROM payloads committed. No Test05.
