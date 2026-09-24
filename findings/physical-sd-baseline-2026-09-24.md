# 2026-09-24 ROM-free physical SD baseline validation

Status: **VALIDATED PHYSICAL BASELINE**

Source archive:
`20260924_PostGBRefresh_CLEAN.zip`

Archive SHA-256:
`035decffefbffcfe57242b60739b49da0213d9b98f51fa99bca683f44fcf21f6`

Archive size: 32,836,059 bytes. ZIP integrity test passed with no corrupt member. The snapshot contains 1,150 files (90,225,006 uncompressed bytes).

This is the ROM-free snapshot of the physical SD card immediately after the hardware-proven GB Refresh closure. It is the default physical/card baseline for subsequent GBC work, subject to the cautions below.

## Protected component identity audit

| Component | SHA-256 | Result |
|---|---|---|
| `bios/bisrv.asd` | `b4b1ffa3e92c61d042b77345a21c16d67fcf586c8af6127dbc545997942f5542` | **MATCH — GB golden firmware** |
| `GB/refresh.xgc` | `34f4714ecbe5affc97b7a0b87726944c253286c3baa3531e437e982174bda238` | **MATCH — GB golden materializer** |
| `GB/catalog.xgc` | `66030c93bfde3e790140265b1123b0ca6cb684efc251a9f602bad480ac7cbbfb` | **MATCH — GB golden explicit merge** |
| `SFC/refresh.xgc` | `1c1706dc1974f48eb6ab8b4598f866ac74992342e2e0885c5509c5edb8fe2dde` | **MATCH — Test74 HW golden** |
| `SFC/catalog.xgc` | `7c45d63c4f15a23661a6f47873bd5c664d68a0a0806155a422f123952bc28a01` | **MATCH — Test74 HW golden** |
| `FC/refresh.xgc` | `8b9607e51e4ad24cf19b92dc356f065d57081eaf93d722ccd9c65c00156fbd4e` | **MATCH — Test75 HW golden** |
| `FC/catalog.xgc` | `b12541d5daede8c6e35c0f6f3a53c35c705a7d7ea7bbb508a6ae7e1b8d956067` | **MATCH — Test75 HW golden** |
| `MD/refresh.xgc` | `c0af2dea8291f86b411e819356e7b6b877ca69e39a444f0780348906f610e087` | **MATCH — Test106 materializer** |
| `MD/catalog.xgc` | `e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338` | **MATCH — Test106 golden Stage1** |
| `MD/catalog-safe.xgc` | `45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c` | **MATCH — Test106 golden Stage2** |
| `CLASSIC/refresh.xgc` | `9f932f35b1627bb8a4a7427831454e3c5dd854972231c1062316a814ada8723f` | **MATCH — preserved Test72/123 CLASSIC helper** |
| `cores/classic-mame2000/core.xgc` | `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e` | **MATCH — protected CLASSIC MAME2000 core** |
| `cores/fceumm/core.xgc` | `e98dcdddd925051cedd52c32db0e9fcaea9aafa76897103d8944bdc48149efd8` | **KNOWN HW-proven external core identity** |
| `cores/snes9x2005/core.xgc` | `ee694b5989e1d056f73de99a47588f124caa2df9b5e8c751862c92adb7a543bf` | **KNOWN protected SNES core identity** |

Both `GB/art/.xgo-cat-state` and `MD/art/.xgo-cat-state` contain exactly `CLEAN!`.

## Important residue / future-work cautions

The snapshot contains handheld catalog files from the earlier Test125/Test126 exploratory lineage:

- `GBC/catalog.xgc` SHA `62de14865f8a14143c7980df0b242f33a5c76cbfe967ef16ff9db367a47ac13f`
- `GBA/catalog.xgc` SHA `dca88ac36235669a0e98a591d145e45b005b58d80221e09b9ae8b4b54a55e3a8`
- `GBC/catalog-saf.xgc` SHA `a79fb1b98ff6253d541e471a3741cb2dbed08dbf928621e2eb70192b4d2395f6`
- `GBA/catalog-saf.xgc` SHA `1111a51ce927c68599df1dd0b8b958b3e7303ac1cb0b27f04c2e31f882a02635`
- `GB/catalog-saf.xgc` SHA `6b3ec79439e7597044024bbf04a959b0309078c3e56b3884c8e277cc12f89568`

These identities belong to Test125/Test126 candidate work and **must not be promoted to GBC/GBA golden simply because they are present on this working card**. Test126 documentation explicitly says the candidate was not golden and that its pass would only establish selective discovery/isolation, not enrichment.

The GB directory additionally contains `GB/catalog-safe.xgc` SHA `fc669f719a9001986671092d7e4c136e5539138e26e43f3d3c007bffec8a77fd`, a later MD-transaction-derived experimental GB Stage2, plus the Test126 `catalog-saf.xgc`. Neither participates in the final hardware-proven GB two-stage path, which calls the 2,642-byte `GB/catalog.xgc` directly.

These are classified as **inert archaeological residue**, not baseline dependencies. Future builders must not copy or derive from them accidentally.

## Baseline rule

For future firmware/card candidates, preserve the physical snapshot as the starting card state, but use the protected component table above as the executable identity contract. GBC work must be derived mechanically from the hardware-proven GB architecture and independently audited offline; existing GBC/GBA candidate helpers on this snapshot are evidence/reference only.

The complete per-file SHA-256 + CRC32 manifest was generated from the uploaded archive during validation and should be retained with the private baseline.


## Superseding physical baseline — Post GBC/GBA Refresh

Validated archive: `20260924_PostGBCGBARefresh_CLEAN.zip`

- size: 34,186,948 bytes
- SHA-256: `5df0b1340e7950ee072ccd72dd6f40fd84535d095f1dabd2359e7c5d9d60872e`
- ZIP integrity: PASS
- files: 1,000
- artifact-vault path: `golden/sd-baselines/2026-09-24/20260924_PostGBCGBARefresh_CLEAN.zip`

This snapshot is now the default physical baseline and supersedes the earlier PostGBRefresh snapshot for future modifications. The earlier snapshot remains historical evidence.

The snapshot contains the exact HW-proven cumulative firmware `ea442b74bdc07cd5e05ec2de8da5c997848a76ed3125681c1955fbcb29b66152`, exact golden GB/GBC/GBA materializer and catalog helpers, protected CLASSIC identities, and the final surgically cleaned GBA resource triplet:

- VFNET.TAX `284379c58bd787d1696b25ba3d1505b4356060b635f9428718b4b83720cc2df0`
- HTUIW.NEC `400f92601286ddd25a6e404c70618901f051ee0cf3f07309ad83fd0d4f17250c`
- SPPNP.BVS `39d8597e28a9da3f9cc8127ff791a43e7833caa4d805d7348e5ccea0424190e2`

The final GBA triplet therefore confirms the cleanup that removed the six leaked GB records and obsolete first GBA test batch while preserving A Sound of Thunder and the four working shortened-name GBA additions.
