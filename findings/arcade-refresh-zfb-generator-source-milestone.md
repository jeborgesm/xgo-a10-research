# Arcade Refresh — deterministic ZFB generator source milestone

Date: 2026-09-24
Branch: `research-arcade-refresh-four-family`
Status: **SOURCE + DIRECT FIXTURE VALIDATION; NO FIRMWARE CANDIDATE**

## New source

`tools/arcade_refresh/zfb_codec.py`

Implements the direct stock record contract only:
- exactly 59,904 bytes of 144x208 RGB565LE preview;
- four zero separator bytes;
- bounded ASCII `.zip` basename;
- two trailing zero bytes;
- strict parser rejects extra/ambiguous bytes.

It intentionally contains no family classifier because direct stock evidence proves family identity is external to ZFB bytes.

`tools/arcade_refresh/verify_stock_zfb_fixtures.py`

Pins the four supplied original stock fixtures by filename, size, driver and SHA-256 and requires:
```
parse(original)
-> extract exact 59904-byte preview + driver
-> build_zfb(preview, driver)
-> byte-for-byte equality with original
```

Direct local execution against the user-supplied files passed all four:
- CPS1 Cadillacs and Dinosaurs -> dino.zip -> exact SHA `906395f2...`
- CPS2 Street Fighter Alpha 3 -> sfa3.zip -> exact SHA `c7f9ba3d...`
- IGS Knights of Valour -> kov.zip -> exact SHA `f102b67b...`
- NeoGeo The King of Fighters '94 -> kof94.zip -> exact SHA `42fe8026...`

This closes the **ZFB serialization** problem. The remaining image task is not ZFB format; it is reuse of the already-proven JPEG -> 144x208 RGB565LE conversion.

## Descriptor source

`tools/arcade_refresh/arcade_descriptors.py`

Freezes:
- CPS1 ID7 -> `mswb7.tax / msdtc.nec / mfpmp.bvs`
- CPS2 ID8 -> `kjbyr.tax / djoin.nec / ke89a.bvs`
- IGS ID9 -> `subst.tax / aepic.nec / sensc.bvs`
- NeoGeo ID10 -> `rmapi.tax / pcadm.nec / ntdll.bvs`
- authoritative input roots `/ARCADE/<FAMILY>/{import,art,meta}`
- common runtime ZIP root `/ARCADE/bin`
- common outer ZFB root `/ARCADE`
- deterministic family order CPS1/CPS2/IGS/NeoGeo.

No count-cache field exists by design; first implementation must not encode a guessed cache address.

## Important consequence

The wrapper-generation portion no longer needs any reverse engineering. Runtime helper implementation can be tested against an exact host-side serialization oracle before hardware.

Next source milestone:
- catalog triplet codec/stable append;
- host-side tests against captured current triplets;
- collision/idempotence planner;
- transaction writer design.
