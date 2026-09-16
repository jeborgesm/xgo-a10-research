# Hardware Test74 — Three-game SFC batch PASS

Date: 2026-09-13
Branch: `research-stock-catalog-enrichment`
Status: **HARDWARE PASSED**

## Candidate

`xgo-stock-test74-sfc-batch-catalog-merge.zip`

ZIP SHA-256:
`219c61525bb8b8ba1cb0db8c3d59b70a44e068242d51e12f5f6942ea2ccbc8fc`

## Hardware result

A controlled batch of three SFC games was prepared using the Test74 stock-enrichment workflow:

- ROMs under `/SFC/import/`
- matching JPEG artwork under `/SFC/art/`
- matching metadata TXT files under `/SFC/meta/`

The batch Refresh completed successfully and behaved as expected.

This closes the first real multi-entry hardware gate for the explicit SFC enrichment architecture and confirms that the design is not limited to a single recovery/import case.

## What is now proven

The SFC path is now hardware-proven for both single-entry and multi-entry operation:

`source ROM + metadata + JPEG -> .zsf materialization -> explicit stock SFC catalog merge -> visible stock-list entry -> artwork -> launch -> idempotent unchanged Refresh`

The explicit merge remains batch-oriented: generated or existing top-level `.zsf` wrappers are collected and missing entries are appended to the three SFC stock catalogs while preserving existing order and exact slot-0 launch filenames.

## Propagation gate

SFC is sufficiently proven to begin propagation of the same enrichment concept to the remaining stock console families:

1. FC
2. MD
3. GB
4. GBC
5. GBA

Propagation must remain one family at a time, with the cumulative Test72/Test74 baseline protected. Do not assume byte-for-byte wrapper identity for the remaining families until representative stock wrappers or launch-path evidence is checked. Shared concepts may be reused, but each system's wrapper extension, catalog triplet, folder identity, and launch behavior must be validated before producing the corresponding hardware candidate.

## Protected baseline

Do not regress Mapper v19, CPS1 pacing repair, Audio OSD v8, generalized stock Refresh, CLASSIC generalized importer, normalized MAME2000 core, CLASSIC Save/Load, CLASSIC metadata/artwork behavior, stock consoles, or stock Arcade.

Test74 remains the current hardware-passed SFC enrichment checkpoint.