# Test58 — CLASSIC Refresh reconciliation candidate

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Baseline

Built on the Test57 hardware-PASS baseline, preserving the completed CLASSIC bottom-logo atlas (`Resources/ihdsf.bke`). The protected MAME2000 core remains unchanged.

## Purpose

Make `/CLASSIC/bin` the source of truth for imported CLASSIC games. Deleting a ROM ZIP should remove the corresponding visible CLASSIC entry on the next Refresh.

## Reconciliation contract

Refresh now:

1. reads `Resources/clm.tax` as the canonical CLASSIC catalog;
2. for each catalog entry, opens the corresponding `/CLASSIC/<display>.zfb` wrapper;
3. reads the wrapper's embedded inner ZIP target after the 59,904-byte preview + 4-byte padding;
4. checks `/CLASSIC/bin/<shortname>.zip`;
5. if the ZIP is absent, removes that entry from the in-memory catalog;
6. scans `/CLASSIC/bin` and imports any missing ZIPs using the existing Test53 metadata and RGB565 artwork-sidecar behavior;
7. writes the exact same resulting catalog to `clm.tax`, `clm.nec`, and `clm.bvs`;
8. syncs and invalidates list 11 count if anything changed;
9. preserves the stable no-change / `No New Games` path if nothing changed.

## Safety choice

Test58 deliberately does **not** call filesystem delete/unlink. Orphan `.zfb` wrappers remain on SD but are invisible once removed from the synchronized catalogs. Re-adding the ZIP can reuse the existing wrapper. This avoids introducing an unproven destructive filesystem API in the same test as reconciliation.

Malformed/manual wrappers whose inner target cannot be parsed are retained. A catalog entry whose wrapper file itself is missing is removed because the visible entry is unusable.

Existing aliases for Pac-Man, Ms Pac-Man, Cadillacs and Dinosaurs, and Galaga are retained using a compact hash dispatch.

## Cave pressure

The rebuilt importer is 4,584 bytes in the 4,600-byte established importer cave (`0x80A38000..0x80A391F8`), leaving only 16 bytes. Therefore on-device PNG/JPEG decoding cannot be added to this cave. Image conversion must reuse a callable stock decoder and execute from a separate safe helper region, or use another proven code region.

## Candidate identity

- ZIP: `xgo-classic-test58-refresh-reconcile-delete.zip`
- ZIP SHA-256: `08dbf8bb5e6f9c36496572c95f8f938239a520769c95bf19eec2a3497148c7d0`
- firmware SHA-256: `34b4c3c7f157e13d7af628a422480b67f16bec71d7523d0d63885588c4b61cd2`
- importer size: 4,584 / 4,600 bytes
- protected MAME2000 core SHA-256: `60a62e463fd6faf92744a7be666602dd1621b9fd706f90d20e3b55ee3382bb1e`

## Hardware gate

1. Confirm Test57 CLASSIC bottom logo remains clean.
2. Pick one expendable imported CLASSIC ROM and note its visible title.
3. Delete only that ZIP from `/CLASSIC/bin`.
4. Run Refresh once; title should disappear and device remain responsive.
5. Run Refresh again; expect stable no-change behavior.
6. Put the ZIP back and Refresh; title should reappear and launch.
7. Verify CLASSIC Save/Load still works on another game.
