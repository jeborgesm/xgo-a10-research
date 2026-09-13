# Game metadata enrichment — title/art contract closed

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`
Status: **reverse-engineering contract closed; Test53 candidate built, hardware validation pending**

## Exact field relationship

The stock XGO frontend does not carry four explicit per-entry fields for display name, ROM filename, artwork reference, and emulator ID. Instead those identities are distributed across the catalog, wrapper, and selected system/list route.

### Display name

For English menus, the visible title is derived from the outer catalog filename / wrapper filename with its extension stripped.

This is why stock entries can display human-readable names while preserving a different runtime identity inside the wrapper.

### Runtime ROM filename

For stock Arcade and the CLASSIC list, the outer `.zfb` wrapper contains the actual ZIP basename used by the runtime. Example already recovered from the hardware baseline:

```text
/CLASSIC/Cadillacs and Dinosaurs.zfb
    -> embedded target: dino.zip
/CLASSIC/bin/dino.zip
```

Therefore a metadata-enriched entry can safely use:

```text
/CLASSIC/Teenage Mutant Ninja Turtles.zfb
    -> embedded target: tmnt.zip
/CLASSIC/bin/tmnt.zip
```

without renaming the ROM ZIP.

For FC/SFC/MD/GB/GBC/GBA stock `.zxx` wrappers, the WQW archive member provides the runtime ROM identity while the outer `.zxx` filename remains the catalog/display identity.

### Artwork

Artwork is not stored in the catalog and is not referenced by a separate metadata field.

Every stock wrapper begins with a raw 144 x 208 x 16-bit preview:

```text
144 * 208 * 2 = 59,904 bytes = 0xEA00
```

The image is little-endian RGB565, row-major.

For console `.zxx` wrappers, the WQW archive begins at `0xEA00`.
For Arcade/CLASSIC `.zfb` wrappers, the lightweight launcher payload follows the same 59,904-byte image prefix.

Because the image prefix is outside the inner archive/payload, an existing stock image prefix can be copied or replaced without altering inner ZIP CRCs. Only the complete wrapper hash changes.

### Emulator/system identity

The emulator/system route is selected by the active menu/list/folder and launcher path, not by a fourth per-entry catalog field. CLASSIC already has its dedicated list/runtime path and canonical MAME2000 core location.

## Catalog relationship

The stock catalog format remains:

```text
uint32_le count
uint32_le offsets[count]
char string_blob[]
```

Primary console triplets are position-coupled. Slot 0 contains the outer filename used by the English UI/launcher. Slots 1 and 2 provide the corresponding localized/search strings. There is no artwork pointer.

The generalized Refresh implementation historically appended filename-derived fallbacks into all synchronized slots. That is structurally safe but explains bare names for newly imported content.

## Safe enrichment model

The recovered OEM Arcade structure already gives the desired separation, so a UI-renderer hook is not required for CLASSIC.

Preferred CLASSIC sidecar contract:

```text
/CLASSIC/bin/tmnt.zip
/CLASSIC/meta/tmnt.txt
/CLASSIC/art/tmnt.rgb565
```

where `tmnt.txt` first line might contain:

```text
Teenage Mutant Ninja Turtles
```

Refresh can then generate:

```text
/CLASSIC/Teenage Mutant Ninja Turtles.zfb
```

with:

- first 59,904 bytes from `/CLASSIC/art/tmnt.rgb565`;
- embedded runtime target `tmnt.zip`;
- catalog entry `Teenage Mutant Ninja Turtles.zfb`;
- unchanged ROM shortname and MAME lookup;
- unchanged mapper/save identity.

If artwork is absent, a known-good stock preview prefix can be reused as a fallback.
If metadata is absent, filename-derived Test47 behavior can remain the fallback.

## Why raw RGB565 first

The firmware contains image-decoder infrastructure and JPEG/PNG-related code, but a small, safe callable still-image conversion API has not yet been proven. Test03 already hardware-proved wrapper generation when RGB565 preview bytes are supplied.

Therefore the first hardware candidate uses prepared `.rgb565` assets exactly 59,904 bytes long. PNG/JPEG sidecars can be considered later after the decoder call contract is mapped.

## Test53 candidate

Private artifact workflow: `build-test53-classic-metadata-enrichment.yml`

Protected composition:

- normalized Test47 non-firmware/core package SHA-256: `59f23688770588b7ea0670d5ffa167097a5a7b7ca8be6d6c1d6674bba8b14d36`
- Test52 firmware package SHA-256: `f7aa1ebb7509913d389bc5922011c80795d4e5ec056f312800fe6ba3a02b78d4`
- Test52 input firmware SHA-256: `8475cfdbec0e334d226d13e29c69bbd71dc99e5736b3ef185d4afdd360b91189`
- protected MAME2000 core SHA-256: `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`

Build audit:

- importer cave: `0x80a38000..0x80a391f8`
- capacity: 4,600 bytes
- Test53 importer size: 4,314 bytes
- importer SHA-256: `b01148d8db0338f9279fdf4a99beae1517641897b7a0973df1d19307c39e4c28`
- output firmware SHA-256: `40083d8d05297bef6fd4dc6122f09151ddba6c6db1c4060b917ecbc2ee40c217`
- outside-cave byte audit: PASS
- protected MAME2000 core hash after build: unchanged
- Test53 ZIP SHA-256: `5e64494ebf4339a0bb8e19924f363a891d6fcd5b719732d282d1692df7876d17`

Test53 intentionally enriches only newly discovered CLASSIC ZIPs. It does not yet migrate already-imported bare entries. Hardware PASS is still required before promotion to a protected golden baseline.
