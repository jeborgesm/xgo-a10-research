# CLASSIC bottom strip — unresolved from inception; Test54/Test54b failure

Date: 2026-09-10
Branch: `research-game-metadata-enrichment`

## Historical correction

The garbled/corrupt display at the bottom of the CLASSIC game list was never previously fixed on hardware. It was intentionally left for later while launch, Refresh, compatibility, and Save/Load work took priority.

Earlier notes around Test34 described a proposed bottom-label renderer fix and included a hardware gate stating the strip should disappear, but that is not evidence that the label fix itself ever passed. Later archaeology incorrectly treated that proposal as a previously proven fix/regression. That interpretation is now rejected.

Therefore this is an **original unresolved CLASSIC UI defect**, not a later regression.

## Test54

Test54 attempted to redirect the stock bottom text draw call at `0x80359838` through a list-aware wrapper and substitute the string `CLASSIC`.

Hardware result: **FAIL** — garbled strip unchanged.

## Test54b

Test54b corrected the comparison from logical list ID 11 to zero-based list index 10.

Hardware result: **FAIL** — garbled strip still unchanged.

This proves that changing the text pointer used by the call at `0x80359838` is not sufficient to remove the visible artifact. The visible garble is therefore likely produced by a different UI element/path, or by stale/invalid resource state beneath/around that text draw.

## New investigation direction

Do not make another speculative variant of the `0x80359838` text-pointer hook.

Instead trace the CLASSIC page composition from a known-good stock page and identify every draw/resource operation in the bottom region. Compare list 10/CLASSIC against neighboring stock pages at the renderer/resource-table level and determine which element actually produces the corrupt pixels.

Candidate areas to inspect include:

- bottom banner/sprite resource lookup, not just text rendering;
- list-indexed artwork/resource tables inherited from stock pages;
- stale page-composition buffers or transparency state caused by adding list 11;
- out-of-range table accesses where stock firmware has only entries for lists 0..9;
- any secondary draw after `0x80359838` that overwrites the substituted text;
- dimensions/pitch/format metadata associated with the bottom UI asset.

## Protected state

Test53 remains the hardware-passed metadata/artwork baseline. Test54 and Test54b are rejected UI probes and must not be promoted.

Preserve Mapper v19, Audio OSD v8, generalized Refresh, normalized CLASSIC core, Test52 Save/Load, Test53 metadata/artwork, stock consoles, and stock Arcade while investigating this UI defect.