# Test58 — CLASSIC Refresh reconciliation hardware PASS

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

Hardware result: PASS.

Confirmed on the physical XGO:

- deleting a ROM ZIP from `/CLASSIC/bin` and running Refresh removes that game from the visible CLASSIC catalog;
- the device remains responsive;
- Test57's completed CLASSIC logo atlas remains the protected UI baseline;
- Test52 Save/Load, Test53 metadata/RGB565 artwork behavior, Mapper v19, Audio OSD v8, and the protected MAME2000 core remain part of the cumulative baseline.

Implementation behavior retained for now:

- `/CLASSIC/bin` is the source of truth for visible imported CLASSIC games;
- removed ROMs are removed from the synchronized CLASSIC catalog triplet;
- orphan `.zfb` wrappers are intentionally left on SD rather than physically deleted, because filesystem unlink/remove is not yet mapped/proven;
- re-adding the ROM can reuse its wrapper;
- malformed/manual wrappers whose inner ZIP cannot be parsed are preserved conservatively.

The reconciliation importer is 4,584 bytes in the 4,600-byte established importer cave, leaving only 16 bytes. Therefore normal PNG/JPEG decode/conversion must not be added to this cave. It requires a separate safe helper region and/or reuse of a stock image decoder routine.

Next priority: map and prove the stock still-image decode path so `/CLASSIC/art/<shortname>.png|jpg` can be converted on-device to the 144x208 little-endian RGB565 wrapper preview.