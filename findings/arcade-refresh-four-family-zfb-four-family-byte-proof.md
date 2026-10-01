# Arcade ZFB four-family byte proof

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **DIRECT FILE/BIN EVIDENCE — EXACT STOCK ZFB RECORD GEOMETRY CLOSED**

Four original stock XGO ZFB samples supplied directly from the device/card were compared byte-for-byte:

| Family | Outer ZFB | Size | SHA-256 | Referenced archive |
|---|---|---:|---|---|
| NeoGeo | The King of Fighters '94.zfb | 59919 | 42fe80265245293f097ba415f070a4840bcb2dd985a5bcd1558c4b6db0c726b9 | kof94.zip |
| CPS1 | Cadillacs and Dinosaurs.zfb | 59918 | 906395f282ba3c048311a77f32ee929622c92b074a1ff3f46450ddf19f06a6bc | dino.zip |
| IGS/PGM | Knights of Valour.zfb | 59917 | f102b67b5beb7e2acdc248a249a45c633bd5c1830d6d8b43ab0a136c487cf774 | kov.zip |
| CPS2 | Street Fighter Alpha 3.zfb | 59918 | c7f9ba3d3e8bf260d2ceaf31481e6d35aa6a0a61d7e490a63a6331de6f331a56 | sfa3.zip |

## Exact common geometry

All four independently prove the identical structure:

```
0x0000 .. 0xE9FF   59904 bytes
                     144 * 208 * 2
                     raw little-endian RGB565 thumbnail

0xEA00 .. 0xEA03   4 zero bytes

0xEA04 ..          ASCII driver/archive basename including ".zip"

after basename     2 zero bytes
```

Thus:

```
zfb_size = 59904 + 4 + strlen(zip_basename) + 2
         = 59910 + strlen(zip_basename)
```

Observed:
- kof94.zip len 9 -> 59919
- dino.zip len 8 -> 59918
- kov.zip len 7 -> 59917
- sfa3.zip len 8 -> 59918

The archive name starts at exact file offset `59908 = 0xEA04` in every family.

There is no family tag, list ID, archive size, checksum, pointer, WQW header, or other metadata after the RGB565 image in these samples. Family membership is therefore not encoded in the ZFB record itself.

## Consequences

The initial folder-classification design is strengthened: CPS1/CPS2/IGS/NeoGeo classification must come from the chosen input family/catalog destination, not from ZFB bytes.

A deterministic ZFB generator requires only:
1. a verified 59,904-byte 144x208 RGB565 image;
2. four zero bytes;
3. a bounded ASCII ZIP basename;
4. two zero bytes.

The outer ZFB filename is independent of the inner driver ZIP basename, as demonstrated directly:
- `Cadillacs and Dinosaurs.zfb` -> `dino.zip`
- `Street Fighter Alpha 3.zfb` -> `sfa3.zip`
- `Knights of Valour.zfb` -> `kov.zip`
- `The King of Fighters '94.zfb` -> `kof94.zip`

This gives the importer separate frontend/display identity and runtime/driver identity.

## Correction of older Test06/Test07 interpretation

The old Test06 geometry inference was actually correct for the physical files: the boundary is 59904, followed by four zeros, then the basename. Test06/Test07 failed because the external CPS1 hook incorrectly assumed the physical ZFB record was still available in `ROM_BUFFER` at that lifecycle point. The failure does **not** invalidate the physical-file format.

The prior pass-1 finding's caution is now resolved by direct file evidence.

## Remaining OPEN items

- Correlate these outer ZFB filenames with exact slot0 records in each current family catalog.
- Verify representative slot1/slot2 metadata for these same four records.
- Inventory all current ZFB -> archive relationships and the historical seven unindexed ZFBs.
- Resolve exact current count-cache/reload addresses for lists 7..10.
- Close BIOS/parent-set dependency policy.
- Recover/reuse the proven JPEG -> RGB565 worker without changing its image semantics.

No hardware candidate is authorized by this finding alone.
