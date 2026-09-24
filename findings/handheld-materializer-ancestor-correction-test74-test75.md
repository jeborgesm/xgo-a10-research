# Handheld materializer ancestor correction — Test74/Test75, not Test97

Date: 2026-09-23
Status: repository lineage closure after Test132

## Question

Which proven component should be the architectural ancestor for GB/GBC/GBA
enrichment materialization?

## Direct package fact

The exact HW-proven Test106 package was inspected locally. Its MD directory contains:
- MD/refresh.xgc size 1,056,520 SHA-256
  c0af2dea8291f86b411e819356e7b6b877ca69e39a444f0780348906f610e087
- MD/catalog.xgc size 2642 SHA-256
  e4c21a94055a6aec817494d2f69450f12fbba3244a91c1b74e73de2a4e91b338
- MD/catalog-safe.xgc size 7000 SHA-256
  45b3e2638b27e0d4a3ffa518e359413de619184ea9c93c4a5c83bbbc2e0ac65c

Thus Test106 hardened the MD catalog transaction path but still carries the exact
Test97 materializer. Test106 does NOT contain a later replacement materializer.

## More important architecture evidence

The existing handheld propagation contract already states that GB/GBC/GBA must
inherit materializer semantics from HW-proven Test74/Test75:
- /<SYS>/import source namespace;
- optional meta TXT friendly title;
- optional JPG/JPEG artwork;
- 144x208 LE RGB565 preview;
- stock-shaped wrapper;
- source retained;
- no-overwrite;
- basename/art fallback;
- second unchanged Refresh -> No New Games.

Test75 explicitly cloned the HW-passed Test74 SFC helpers and changed only the
system contract. Test75 then HW-proved a five-game FC batch, wrapper regeneration
with corrected JPG artwork, launch, and stable catalog identity.

Therefore the correct component ancestry for handheld enrichment is:

  Test74 SFC materializer architecture (HW)
      -> Test75 FC mechanical propagation (HW)
      -> GB/GBC/GBA descriptor-specific propagation

Test97 remains relevant only as historical MD/two-character-extension evidence,
not as the preferred handheld materializer implementation.

## Consequence for current GB branch

The Test127/Test131/Test132 GB helper was mechanically derived from Test97 MD.
That was the wrong architectural ancestor under the project's own preserved
handheld propagation contract.

Do not continue patching Test132/Test97 filename predicates.

Next implementation work must recover the exact Test74/Test75 materializer and
derive GB from that proven enrichment architecture, with a deliberate .gb source
predicate adaptation audited before hardware. Catalog merge should likewise derive
from Test74/Test75 stable-merge architecture using GB's known triplet/count cache.

No hardware candidate until the Test75 -> GB mechanical substitution set and any
two-character-extension-specific code delta are explicitly audited.
