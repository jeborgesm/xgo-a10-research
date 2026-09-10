# Test53 metadata enrichment — Hardware PASS and next Refresh contract

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Hardware result

Test53 CLASSIC metadata enrichment is hardware-confirmed PASS.

Confirmed on the physical XGO:

- `/CLASSIC/meta/<shortname>.txt` can provide a human-readable wrapper/display name;
- `/CLASSIC/art/<shortname>.rgb565` is accepted as custom artwork;
- artwork contract is 144 x 208, little-endian RGB565, row-major, exactly 59,904 bytes;
- the outer `.zfb` display identity can differ from the inner MAME ZIP shortname;
- runtime continues to launch the original `/CLASSIC/bin/<shortname>.zip`.

This closes the display-name / runtime-name / artwork separation without a UI renderer hook and without modifying the protected MAME2000 core.

## Next user-facing target

The desired normal workflow should require no PC-side image conversion:

```text
/CLASSIC/bin/tmnt.zip
/CLASSIC/meta/tmnt.txt
/CLASSIC/art/tmnt.png   (or .jpg)
```

Refresh should decode the ordinary image on-device, scale/letterbox it to 144x208, convert to little-endian RGB565, write/embed the preview into the `.zfb` wrapper, update the catalog, and only after complete success remove the source PNG/JPG if it is no longer needed.

Deletion must be transactional: never delete the source image before decode + conversion + wrapper write + catalog update have succeeded.

## Stock decoder status

Firmware evidence proves JPEG/PNG-related code exists (`image/jpeg`, `image/png`, JPEG decoder diagnostics and multimedia decoder subsystem), but a small callable still-image API that returns a framebuffer has not yet been mapped. This remains the next reverse-engineering gate. A new image decoder must not be added to the already-tight Test47/Test53 importer cave unless stock decoder reuse is proven impossible and a separate safe code region is established.

## Refresh reconciliation / removal target

Refresh should evolve from additive-only import to reconciliation for CLASSIC:

- `/CLASSIC/bin` is the source of truth for imported CLASSIC games;
- deleting an imported ZIP should remove its generated wrapper and synchronized entries from `clm.tax`, `clm.nec`, and `clm.bvs`;
- removal must identify generated/imported entries by the wrapper's inner ZIP target, not merely by visible filename;
- stock/manual wrappers must not be deleted accidentally;
- order of surviving entries should remain stable;
- `No New Games` semantics should become a no-change result (no additions or removals).

## CLASSIC bottom-label regression

The garbled bottom strip is a known regression, not a new unknown.

Test34 documented the proven minimal fix:

```text
0x80359838  jal 0x803528a4
```

redirected through a list-aware wrapper. For list 11 only, stack +24 is replaced with `CLASSIC`; all other lists tail-call the stock renderer unchanged. The Test34 helper was at `0x807dba64` in that lineage.

This behavior did not survive into the later Test52/Test53 cumulative baseline and should be restored on the current protected lineage. The implementation must be re-based to current free space rather than blindly copying the old Test34 cave addresses, because later Refresh work reused/changed that area.

## Protected baseline

Any next candidate must preserve:

- Mapper v19;
- Audio OSD v8;
- Test47 generalized CLASSIC importer behavior;
- normalized `/cores/classic-mame2000/core.xgc` and its protected hash;
- Test52 CLASSIC Save/Load;
- Test53 metadata/RGB565 enrichment;
- stable Refresh / no-change behavior;
- stock consoles and stock Arcade.

Implementation order:

1. restore CLASSIC bottom label on current Test53 lineage;
2. map a callable stock JPEG/PNG still-image decode path;
3. add on-device image scale/letterbox + RGB565 conversion with transactional source deletion;
4. add safe CLASSIC removal/reconciliation;
5. generalize metadata/art handling to the other refreshed systems after CLASSIC hardware passes.