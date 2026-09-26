# CPS1 stock archive lookup semantics — CRC-first closure

Date: 2026-09-26
Branch: research-arcade-refresh-four-family
Status: SRC/UP correspondence strengthened by XGO BIN diagnostics
Hardware candidate: NOT AUTHORIZED

## Question

Could Test04 fail merely because the imported 1941.zip uses modern MAME member filenames instead of the FBA-era aliases compiled into the XGO driver table?

## Source-family closure

The preserved stock-FBA reconstruction identifies the XGO libretro-facing arcade loader as the later FB Alpha v0.2.97.42 / 621e371 archive-loader family.

That loader's archive matching algorithm is:

1. enumerate archive entries;
2. for each required driver ROM, search archive entries by required CRC;
3. only if CRC lookup fails, obtain the driver ROM name and search by filename;
4. if filename matches despite CRC mismatch, accept it while flagging bad_crc / emitting a warning;
5. only an unresolved required ROM remains a load failure.

The exact XGO BIN contains the corresponding diagnostic vocabulary:
- "[FBA] Searching ROM at index %d with CRC 0x%08x and name %s => Not Found"
- "[FBA] Using ROM at index %d with wrong CRC and name %s"
- "[FBA] ROM at index %d with CRC 0x%08x is required ..."

This correspondence is substantially stronger than a generic upstream analogy: the branch structure implied by the source diagnostics is preserved in the XGO binary's diagnostic set.

Classification:
- loader algorithm from historical source family: SRC/UP;
- matching XGO diagnostic strings: BIN;
- exact instruction-level XGO control-flow equivalence: not yet claimed beyond this correspondence.

## Consequence for 1941

The XGO 1941 World descriptor table uses FBA-era names such as 41e_30.rom and 41_gfx5.rom.

However, because archive matching is CRC-first, an archive containing differently named members with the correct required CRCs should still satisfy the loader.

Therefore:

**Modern-vs-FBA internal member naming by itself is not a viable explanation for Test04 launch failure.**

Filename differences matter only when the payload CRC does not match and the loader must use its filename fallback.

This materially weakens the previous ROM-naming hypothesis.

## What ROM compatibility now means

The remaining ROM-set compatibility question is narrower:

- Are the actual Test04 archive payload CRCs the ones required by the XGO 1941 driver?
- If not, do any members nevertheless match the XGO fallback names?
- Are all required non-optional members present across the archive search set?

Without the exact Test04 1941.zip, these remain OPEN.

## Comparison with known-good Cadillacs

Cadillacs and 1941 both use:
- the same stock CPS1/FBA runtime family;
- the same descriptor-table architecture;
- valid driver/archive basename identity (dino.zip versus 1941.zip);
- the same CRC-first archive-loader family.

No first divergence has yet been demonstrated at those layers.

## Next offline task

Move one layer outward/upstream from ROM-member resolution and close the exact stock CPS1 driver selection and archive-list construction for 1941 versus Cadillacs:

- how 1941.zip/dino.zip becomes the initial archive path;
- whether parent/clone archive names are appended;
- whether driver selection is based solely on archive basename or another state value;
- whether generated catalog position can alter selected driver identity;
- whether 1941 World is selected when the wrapper says 1941.zip.

Separately retain the live-list/cache freeze as an independent OPEN defect.

No Test05 authorized.
