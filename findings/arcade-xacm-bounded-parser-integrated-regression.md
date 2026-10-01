# XACM + bounded ZIP parser integrated regression

Date: 2026-09-27
Status: OFFLINE PASS — NOT HW

The exact preserved firmware was re-extracted from the uploaded analysis archive and independently rehashed as 12,768,452 bytes, SHA256 `869e056d000337e1b10c834f0a93244c0abd99457c1c8374367f7dff20e43daf`.

A fresh end-to-end host run regenerated the deterministic JSON and XACM after the Neo Geo empty-descriptor fix. Results reproduced exactly:

- JSON: 991,463 bytes; SHA256 `c78e74bafe327dda636f36932024c010e84d9b6e4236a63ea62e458dc7cfd6df`
- XACM: 237,921 bytes; SHA256 `86a798ab9e0c8042a84b99a37fcfacd8708706d0010e0459726420d92ab7c0f5`
- 678 target drivers, 10,404 ROM records, 57,797 string bytes.
- Observed families: CPS1 154, CPS2 232, IGS 34, NEOGEO 258. These remain observations, not import limits.

The compatibility fixture was then rerun through the actual intended metadata substrate: XACM v1 lookup plus the bounded central-directory parser. Python `zipfile` and JSON were not used for the verdict.

Results:

```
1941(1).zip -> INCOMPATIBLE
missing: 41e_30.rom, 41e_35.rom, 41e_31.rom, 41e_36.rom
size_bad: none

1941(2).zip -> COMPATIBLE
missing: none
size_bad: none
```

Thus the compact manifest plus metadata-only parser preserves the known hardware compatibility distinction.

The reusable host implementation is `tools/arcade_refresh/validate_arcade_import_xacm.py`. It separates clean unsupported/incompatible outcomes from parser/manifest errors and does no decompression.

Next boundary is translation of this exact bounded lookup/parser contract into the external on-device Refresh helper. No Test05.
